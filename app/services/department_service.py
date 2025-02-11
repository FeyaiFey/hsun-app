from typing import List, Dict, Any, Optional
from sqlmodel import Session, select

from app.models.department import Department
from app.schemas.department import DepartmentResponse, DepartmentUserInfo, DepartmentRegister, DepartmentTreeNode
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.monitor import MetricsManager
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.error_codes import HttpStatusCode, ErrorCode

class DepartmentService:
    """部门服务类"""
    
    def __init__(self, db: Session, cache: MemoryCache):
        self.db = db
        self.cache = cache
        self.metrics = MetricsManager()

    def _clear_department_cache(self, department_id: Optional[int] = None) -> None:
        """清除部门缓存
        
        Args:
            department_id: 部门ID，为None时清除所有部门缓存
            
        Raises:
            DatabaseError: 缓存清除失败
        """
        try:
            if department_id is None:
                # 清除所有部门相关缓存
                cache_keys = ["all:departments", "department:tree", "department:register", "department:tree:register"]
                logger.debug("清除所有部门缓存")
            else:
                # 清除特定部门缓存
                cache_keys = [
                    f"department:{department_id}",
                    "department:tree",  # 树结构可能受影响，也需要清除
                    "department:tree:register"  # 注册树结构也需要清除
                ]
                logger.debug(f"清除部门 {department_id} 的缓存")
                
            for key in cache_keys:
                if not self.cache.delete(key):
                    raise DatabaseError(detail=f"清除缓存失败: {key}")
        except Exception as e:
            logger.error(f"清除部门缓存失败: {str(e)}")
            raise DatabaseError(detail=f"清除部门缓存失败: {str(e)}")

    async def _get_department_by_id(self, department_id: int) -> Optional[Department]:
        """根据ID获取部门
        
        Args:
            department_id: 部门ID
            
        Returns:
            Optional[Department]: 部门对象
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            # 先从缓存获取
            cache_key = f"department:{department_id}"
            cached_dept = self.cache.get(cache_key)
            if cached_dept:
                self.metrics.track_cache_metrics(hit=True)
                return cached_dept

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取
            statement = select(Department).where(Department.id == department_id)
            department = self.db.exec(statement).first()
            
            # 缓存结果
            if department:
                self.cache.set(cache_key, department, expire=3600)
                
            return department
            
        except Exception as e:
            logger.error(f"获取部门失败: {str(e)}")
            raise DatabaseError(detail="获取部门失败")

    async def _get_children_departments(self, parent_id: Optional[int] = None) -> List[Department]:
        """获取子部门列表
        
        Args:
            parent_id: 父部门ID
            
        Returns:
            List[Department]: 子部门列表
        """
        try:
            query = select(Department)
            if parent_id is not None:
                query = query.where(Department.parent_id == parent_id)
            else:
                query = query.where(Department.parent_id.is_(None))
                
            return self.db.exec(query).all()
            
        except Exception as e:
            logger.error(f"获取子部门失败: {str(e)}")
            raise DatabaseError(detail="获取子部门失败")

    def _build_department_tree(self, departments: List[Department]) -> List[Dict[str, Any]]:
        """构建部门树
        
        Args:
            departments: 部门列表
            
        Returns:
            List[Dict[str, Any]]: 部门树
        """
        dept_map = {dept.id: dept.dict() for dept in departments}
        tree = []
        
        for dept_id, dept_dict in dept_map.items():
            parent_id = dept_dict.get('parent_id')
            if parent_id is None:
                tree.append(dept_dict)
            else:
                parent = dept_map.get(parent_id)
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(dept_dict)
        
        return sorted(tree, key=lambda x: x.get('id', 0))
    
    async def get_department_register_list(self) -> List[DepartmentRegister]:
        """获取部门注册列表
        Returns:
            DepartmentRegister 列表
        """
        try:
            cache_key = "department:register"
            cached_depts = self.cache.get(cache_key)
            if cached_depts:
                self.metrics.track_cache_metrics(hit=True)
                return cached_depts

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取
            statement = select(Department.id,Department.department_name).order_by(Department.id)
            departments_register = self.db.exec(statement).all()
            # 转换为 DepartmentRegister 格式
            departments_register = [
                DepartmentRegister(
                    label=dept.department_name,
                    value=dept.id
                ) for dept in departments_register
            ]
            # 缓存结果
            if departments_register:
                self.cache.set(cache_key, departments_register, expire=3600)
            return departments_register
        except Exception as e:
            logger.error(f"获取所有注册所有部门列表失败: {str(e)}")
            raise DatabaseError(detail="获取部门列表失败")

            
            

    async def get_department_tree(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取部门树结构
        
        Args:
            parent_id: 父部门ID，为None时获取完整树
            
        Returns:
            List[Dict[str, Any]]: 部门树
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            # 如果是获取完整树，尝试从缓存获取
            cache_key = "department:tree" if parent_id is None else None
            if cache_key:
                cached_tree = self.cache.get(cache_key)
                if cached_tree:
                    self.metrics.track_cache_metrics(hit=True)
                    return cached_tree
                self.metrics.track_cache_metrics(hit=False)
            
            # 获取所有部门
            departments = await self.get_all_departments()
            
            # 构建部门字典，用于快速查找
            dept_dict = {dept.id: dept.dict() for dept in departments}
            
            # 构建树结构
            tree = []
            for dept in departments:
                dept_data = dept_dict[dept.id]
                # 如果是根部门（没有父部门）
                if dept.parent_id is None:
                    tree.append(dept_data)
                # 如果有父部门
                elif dept.parent_id in dept_dict:
                    parent = dept_dict[dept.parent_id]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(dept_data)
            
            # 如果指定了parent_id，只返回该部门的子树
            if parent_id is not None:
                for dept in tree:
                    if dept['id'] == parent_id:
                        return [dept]
                return []
            
            # 缓存完整树
            if cache_key:
                self.cache.set(cache_key, tree, expire=3600)
            
            return tree
            
        except Exception as e:
            logger.error(f"获取部门树失败: {str(e)}")
            raise DatabaseError(detail="获取部门树失败")

    async def get_all_departments(self) -> List[DepartmentRegister]:
        """获取所有部门
        
        Returns:
            List[Department]: 部门列表
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            # 尝试从缓存获取
            cache_key = "all:departments"
            cached_depts = self.cache.get(cache_key)
            if cached_depts:
                self.metrics.track_cache_metrics(hit=True)
                return cached_depts

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取
            statement = select(Department).order_by(Department.id)
            departments = self.db.exec(statement).all()
            
            # 缓存结果
            if departments:
                self.cache.set(cache_key, departments, expire=3600)
            
            return departments
            
        except Exception as e:
            logger.error(f"获取所有部门失败: {str(e)}")
            raise DatabaseError(detail="获取部门列表失败")

    async def get_department_by_id(self, department_id: int) -> Department:
        """根据ID获取部门
        
        Args:
            department_id: 部门ID
            
        Returns:
            Department: 部门对象
            
        Raises:
            NotFoundError: 部门不存在
            DatabaseError: 数据库操作失败
        """
        department = await self._get_department_by_id(department_id)
        if not department:
            raise NotFoundError(detail=f"部门 {department_id} 不存在")
        return department

    async def get_parent_departments(self, department_id: int) -> List[Department]:
        """获取父部门链
        
        Args:
            department_id: 部门ID
            
        Returns:
            List[Department]: 父部门链（从上到下）
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            result = []
            current_dept = await self._get_department_by_id(department_id)
            
            while current_dept and current_dept.parent_id:
                parent = await self._get_department_by_id(current_dept.parent_id)
                if parent:
                    result.insert(0, parent)
                current_dept = parent
                
            return result
            
        except Exception as e:
            logger.error(f"获取父部门链失败: {str(e)}")
            raise DatabaseError(detail="获取父部门链失败")

    async def get_department_tree_for_register(self) -> List[DepartmentTreeNode]:
        """获取用于注册的部门树结构
        
        Returns:
            List[DepartmentTreeNode]: 部门树结构
        """
        try:
            # 尝试从缓存获取
            cache_key = "department:tree:register"
            cached_tree = self.cache.get(cache_key)
            if cached_tree:
                self.metrics.track_cache_metrics(hit=True)
                return cached_tree

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取所有部门
            statement = select(Department).order_by(Department.id)
            departments = self.db.exec(statement).all()

            # 转换为树节点格式
            dept_nodes = [
                DepartmentTreeNode(
                    label=dept.department_name,
                    value=str(dept.id),
                    parentId=str(dept.parent_id) if dept.parent_id else None,
                    children=[]
                ) for dept in departments
            ]

            # 构建树结构
            dept_map = {dept.value: dept for dept in dept_nodes}
            tree = []

            for dept in dept_nodes:
                if dept.parentId is None:
                    # 根节点
                    tree.append(dept)
                else:
                    # 子节点，添加到父节点的children中
                    parent = dept_map.get(dept.parentId)
                    if parent:
                        if parent.children is None:
                            parent.children = []
                        parent.children.append(dept)

            # 缓存结果
            if tree:
                self.cache.set(cache_key, tree, expire=3600)

            return tree

        except Exception as e:
            logger.error(f"获取部门注册树失败: {str(e)}")
            raise DatabaseError(detail="获取部门树失败")

# 创建全局部门服务实例
department_service = DepartmentService(None, None)  # 在应用启动时需要注入实际的 db 和 cache 