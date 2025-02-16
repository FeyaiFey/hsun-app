from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, func

from app.crud.department import department as crud_department
from app.models.department import Department
from app.schemas.department import DepartmentList, DepartmentListResponse, DepartmentTableListResponse
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.monitor import MetricsManager
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message

class DepartmentService:
    """部门服务类"""
    
    def __init__(self, db: Optional[Session] = None, cache: Optional[MemoryCache] = None):
        self._db = db
        self._cache = cache
        self.metrics = MetricsManager()

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if not self._db:
            raise CustomException("数据库会话未注入")
        return self._db
    
    @db.setter
    def db(self, value: Session):
        """设置数据库会话"""
        self._db = value
        
    @property
    def cache(self) -> MemoryCache:
        """获取缓存实例"""
        if not self._cache:
            raise CustomException("缓存实例未注入")
        return self._cache
    
    @cache.setter
    def cache(self, value: MemoryCache):
        """设置缓存实例"""
        self._cache = value
    
    def _clear_department_cache(self, department_id: Optional[int] = None) -> None:
        """清除部门缓存"""
        try:
            if department_id is None:
                # 清除所有部门相关缓存
                cache_keys = ["all:departments", "department:tree", "department:register", "department:tree:register", "department:list"]
                logger.debug("清除所有部门缓存")
            else:
                # 清除特定部门缓存
                cache_keys = [
                    f"department:{department_id}",
                    "department:tree",  # 树结构可能受影响，也需要清除
                    "department:tree:register",  # 注册树结构也需要清除
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
    
    async def get_department_by_id(self, department_id: int) -> Optional[Department]:
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

    async def get_department_tree(self) -> DepartmentListResponse:
        """获取树形结构的部门列表
        
        Returns:
            DepartmentListResponse: 树形结构的部门列表，包含父子关系
            
        Raises:
            CustomException: 当获取部门列表失败时抛出
        """
        try:
            # 尝试从缓存获取
            # cache_key = "department:tree:list"
            # cached_tree = self.cache.get(cache_key)
            # if cached_tree:
            #     self.metrics.track_cache_metrics(hit=True)
            #     logger.debug(f"命中缓存: {cache_key}")
            #     return DepartmentListResponse(**cached_tree)

            # self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取树形结构
            tree_response = crud_department.get_department_tree_list(self.db)
            
            # 缓存结果
            # try:
            #     if tree_response:
            #         cache_data = tree_response.model_dump()
            #         success = self.cache.set(cache_key, cache_data, expire=3600)
            #         if success:
            #             logger.debug(f"成功设置缓存: {cache_key}")
            #         else:
            #             logger.warning(f"设置缓存失败: {cache_key}")
            # except Exception as cache_error:
            #     logger.warning(f"缓存设置失败: {str(cache_error)}")
            
            return tree_response
            
        except Exception as e:
            logger.error(f"获取部门树形列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_departments_list_with_params(
        self, 
        params: dict,
        use_cache: bool = True
    ) -> DepartmentTableListResponse:
        """根据参数获取部门列表
        
        Args:
            params: 查询参数字典
                - department_name: 部门名称
                - status: 状态
                - pageIndex: 页码
                - pageSize: 每页数量
                - order_by: 排序字段
            use_cache: 是否使用缓存，默认为True
                
        Returns:
            DepartmentTableListResponse: 包含部门列表数据和总记录数的响应
        """
        try:
            if not self.db:
                raise CustomException(message="数据库会话未初始化")

            # 构建缓存键
            cache_key = f"department:list:{hash(frozenset(params.items()))}"
            
            # 如果启用缓存，尝试从缓存获取
            if use_cache:
                try:
                    cached_data = self.cache.get(cache_key)
                    if cached_data:
                        self.metrics.track_cache_metrics(hit=True)
                        logger.debug(f"命中缓存: {cache_key}")
                        return DepartmentTableListResponse(**cached_data)
                except Exception as cache_error:
                    logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 计算分页参数
            page = params.get("pageIndex", 1)
            page_size = params.get("pageSize", 10)
            skip = (page - 1) * page_size
            
            # 获取部门列表数据
            response_data = crud_department.get_department_table_list(
                self.db,
                skip=skip,
                limit=page_size,
                department_name=params.get("department_name"),
                status=params.get("status"),
                order_by=params.get("order_by")
            )
            
            # 如果启用缓存，缓存结果
            if use_cache:
                try:
                    cache_data = response_data.model_dump()
                    success = self.cache.set(cache_key, cache_data, expire=3600)
                    if success:
                        logger.debug(f"成功设置缓存: {cache_key}")
                    else:
                        logger.warning(f"设置缓存失败: {cache_key}")
                except Exception as cache_error:
                    logger.warning(f"缓存设置失败: {str(cache_error)}")
            
            return response_data
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取部门列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def save_department(self, department_data: Dict[str, Any]) -> None:
        """保存部门信息
        
        Args:
            department_data: 部门数据，包含：
                - id: 部门ID（可选，更新时需要）
                - department_name: 部门名称
                - parent_id: 父部门ID（可选）
                - status: 状态（1-启用，0-禁用）
        """
        try:
            # 检查部门名称是否已存在
            existing = self.db.exec(
                select(Department).where(
                    Department.department_name == department_data["department_name"]
                )
            ).first()
            
            # 如果存在ID，执行更新操作
            if "id" in department_data:
                department = self.db.get(Department, department_data["id"])
                if not department:
                    raise CustomException("部门不存在")
                
                # 检查部门名称是否被其他部门使用
                if existing and existing.id != department_data["id"]:
                    raise CustomException("部门名称已存在")
                
                # 如果有父部门ID，检查父部门是否存在
                if department_data.get("parent_id"):
                    parent = self.db.get(Department, department_data["parent_id"])
                    if not parent:
                        raise CustomException("父部门不存在")
                
                # 更新部门信息
                for key, value in department_data.items():
                    if key != "id":  # 不更新ID字段
                        setattr(department, key, value)
                
                self.db.add(department)
                
            # 否则执行新增操作
            else:
                # 检查部门名称是否已存在
                if existing:
                    raise CustomException("部门名称已存在")
                
                # 如果有父部门ID，检查父部门是否存在
                if department_data.get("parent_id"):
                    parent = self.db.get(Department, department_data["parent_id"])
                    if not parent:
                        raise CustomException("父部门不存在")
                
                # 创建新部门
                department = Department(**department_data)
                self.db.add(department)
            
            # 提交事务
            self.db.commit()
            
            # 清除缓存
            await self.clear_cache()
            
        except CustomException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"保存部门信息失败: {str(e)}")
            raise CustomException("保存部门信息失败")
    
    async def delete_department(self, id: int) -> None:
        """删除部门
        
        Args:
            id: 部门ID
        """
        try:
            # 检查部门是否存在
            dept = self.db.get(Department, id)
            if not dept:
                raise CustomException("部门不存在")
            
            # 检查是否有子部门
            sub_departments = self.db.exec(
                select(Department).where(Department.parent_id == id)
            ).all()
            if sub_departments:
                raise CustomException("请先删除子部门")
            
            # 删除部门
            self.db.delete(dept)
            self.db.commit()
            
            # 清除缓存
            await self.clear_cache()
            
        except CustomException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除部门失败: {str(e)}")
            raise CustomException("删除部门失败")
    
    async def batch_delete_departments(self, ids: List[int]) -> None:
        """批量删除部门
        
        Args:
            ids: 部门ID列表
        """
        try:
            for id in ids:
                await self.delete_department(id)
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"批量删除部门失败: {str(e)}")
            raise CustomException("批量删除部门失败")
    
    async def clear_cache(self) -> None:
        """清除部门相关的缓存"""
        try:
            self.cache.delete("department_tree")
            self.cache.delete("department_list")
        except Exception as e:
            logger.error(f"清除部门缓存失败: {str(e)}")
            raise CustomException("清除部门缓存失败")

# 创建服务实例
department_service = DepartmentService() 