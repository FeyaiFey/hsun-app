from typing import List, Dict, Any, Optional
from sqlmodel import Session, select

from app.crud.department import department as crud_department
from app.models.department import Department
from app.schemas.department import DepartmentList, DepartmentResponse, DepartmentUserInfo, DepartmentRegister, DepartmentTreeNode, DepartmentListResponse
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.monitor import MetricsManager
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message

class DepartmentService:
    """部门服务类"""
    
    def __init__(self, db: Session, cache: MemoryCache):
        self.db = db
        self.cache = cache
        self.metrics = MetricsManager()

    def _clear_department_cache(self, department_id: Optional[int] = None) -> None:
        """清除部门缓存"""
        try:
            if department_id is None:
                # 清除所有部门相关缓存
                cache_keys = ["all:departments", "department:tree", "department:register", "department:tree:register","department:list"]
                logger.debug("清除所有部门缓存")
            else:
                # 清除特定部门缓存
                cache_keys = [
                    f"department:{department_id}",
                    "department:tree",  # 树结构可能受影响，也需要清除
                    "department:tree:register"  # 注册树结构也需要清除
                    "department:list"
                ]
                logger.debug(f"清除部门 {department_id} 的缓存")
                
            for key in cache_keys:
                if not self.cache.delete(key):
                    raise CustomException(
                        message=get_error_message(ErrorCode.DB_ERROR)
                    )
        except Exception as e:
            logger.error(f"清除部门缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def _get_department_by_id(self, department_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        try:
            # 先从缓存获取
            cache_key = f"department:{department_id}"
            cached_dept = self.cache.get(cache_key)
            if cached_dept:
                self.metrics.track_cache_metrics(hit=True)
                # 如果是字典，转换为 Department 实例
                if isinstance(cached_dept, dict):
                    return Department(**cached_dept)
                return cached_dept

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取
            statement = select(Department).where(Department.id == department_id)
            department = self.db.exec(statement).first()
            
            # 缓存结果
            if department:
                self.cache.set(cache_key, department.model_dump(), expire=3600)
                
            return department
            
        except Exception as e:
            logger.error(f"获取部门失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def _get_children_departments(self, parent_id: Optional[int] = None) -> List[Department]:
        """获取子部门列表"""
        try:
            query = select(Department)
            if parent_id is not None:
                query = query.where(Department.parent_id == parent_id)
            else:
                query = query.where(Department.parent_id.is_(None))
                
            return self.db.exec(query).all()
            
        except Exception as e:
            logger.error(f"获取子部门失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    def _build_department_tree(self, departments: List[Department]) -> List[Dict[str, Any]]:
        """构建部门树"""
        dept_map = {dept.id: dept.model_dump() for dept in departments}
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

    async def get_departments_list(self) -> List[DepartmentList]:
        """前端获取部门列表"""
        try:
            cache_key = "department:list"
            cached_depts = self.cache.get(cache_key)
            if cached_depts:
                self.metrics.track_cache_metrics(hit=True)
                # 从缓存数据重建模型实例
                return [DepartmentList(**dept) for dept in cached_depts]

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库中获取
            departments = crud_department.get_all(self.db)
            
            # 转换为响应模型列表
            department_list = [
                DepartmentList(
                    id=dept.id,
                    pid=dept.parent_id,
                    department_name=dept.department_name,
                    status=dept.status,
                    created_at=dept.created_at
                ) for dept in departments
            ]
            
            # 缓存结果 - 存储序列化后的数据
            if department_list:
                cache_data = [dept.model_dump() for dept in department_list]
                self.cache.set(cache_key, cache_data, expire=3600)
            
            return department_list
            
        except Exception as e:
            logger.error(f"获取所有部门列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_department_tree_list(self) -> DepartmentListResponse:
        """获取树形结构的部门列表
        
        Returns:
            DepartmentListResponse: 树形结构的部门列表，包含父子关系
            
        Raises:
            CustomException: 当获取部门列表失败时抛出
        """
        try:
            # 尝试从缓存获取
            cache_key = "department:tree:list"
            cached_tree = self.cache.get(cache_key)
            if cached_tree:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return DepartmentListResponse(**cached_tree)

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取树形结构
            tree_response = crud_department.get_department_tree_list(self.db)
            
            # 缓存结果
            try:
                if tree_response:
                    cache_data = tree_response.model_dump()
                    success = self.cache.set(cache_key, cache_data, expire=3600)
                    if success:
                        logger.debug(f"成功设置缓存: {cache_key}")
                    else:
                        logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
            
            return tree_response
            
        except Exception as e:
            logger.error(f"获取部门树形列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_department_register_list(self) -> List[DepartmentRegister]:
        """获取部门注册列表"""
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
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_department_tree(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取部门树结构"""
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
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_all_departments(self) -> List[DepartmentRegister]:
        """获取所有部门"""
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
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_department_by_id(self, department_id: int) -> Department:
        """根据ID获取部门"""
        department = await self._get_department_by_id(department_id)
        if not department:
            raise CustomException(
                message=get_error_message(ErrorCode.RESOURCE_NOT_FOUND)
            )
        return department

    async def get_parent_departments(self, department_id: int) -> List[Department]:
        """获取父部门链"""
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
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_department_tree_for_register(self) -> List[DepartmentTreeNode]:
        """获取用于注册的部门树结构"""
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
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_departments_list_with_params(self, params: dict) -> List[DepartmentList]:
        """根据参数获取部门列表
        
        Args:
            params: 查询参数字典
                - department_name: 部门名称
                - status: 状态
                - page: 页码
                - page_size: 每页数量
                - order_by: 排序字段
        """
        try:
            if not self.db:
                raise CustomException(message="数据库会话未初始化")

            # 构建缓存键
            cache_key = f"department:list:{hash(frozenset(params.items()))}"
            
            try:
                cached_depts = self.cache.get(cache_key)
                if cached_depts:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return [DepartmentList(**dept) for dept in cached_depts]
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库中获取并应用过滤条件
            query = select(Department)
            
            # 应用过滤条件
            if params.get("department_name"):
                query = query.where(Department.department_name.like(f"%{params['department_name']}%"))
            if params.get("status") is not None:
                query = query.where(Department.status == params["status"])
                
            # 应用排序
            if params.get("order_by"):
                order_field = getattr(Department, params["order_by"].lstrip("-"), None)
                if order_field:
                    query = query.order_by(
                        order_field.desc() if params["order_by"].startswith("-") else order_field
                    )
            else:
                # 默认按 id 排序
                query = query.order_by(Department.id)
                
            # 应用分页
            page = params.get("page", 1)
            page_size = params.get("page_size", 10)
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            # 执行查询
            departments = self.db.exec(query).all()
            
            # 转换为响应模型列表
            department_list = [
                DepartmentList(
                    id=dept.id,
                    pid=dept.parent_id,
                    department_name=dept.department_name,
                    status=dept.status,
                    created_at=dept.created_at
                ) for dept in departments
            ]
            
            # 缓存结果
            try:
                if department_list:
                    cache_data = [dept.model_dump() for dept in department_list]
                    success = self.cache.set(cache_key, cache_data, expire=3600)
                    if success:
                        logger.debug(f"成功设置缓存: {cache_key}")
                    else:
                        logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
            
            return department_list
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取部门列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建全局部门服务实例
department_service = DepartmentService(None, None)  # 在应用启动时需要注入实际的 db 和 cache 