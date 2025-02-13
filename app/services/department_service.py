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

    async def get_departments_list_with_params(self, params: dict) -> DepartmentTableListResponse:
        """根据参数获取部门列表
        
        Args:
            params: 查询参数字典
                - department_name: 部门名称
                - status: 状态
                - pageIndex: 页码
                - pageSize: 每页数量
                - order_by: 排序字段
                
        Returns:
            DepartmentTableListResponse: 包含部门列表数据和总记录数的响应
        """
        try:
            if not self.db:
                raise CustomException(message="数据库会话未初始化")

            # 构建缓存键
            cache_key = f"department:list:{hash(frozenset(params.items()))}"
            
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
            
            # 缓存结果
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

# 创建全局部门服务实例
department_service = DepartmentService(None, None)  # 在应用启动时需要注入实际的 db 和 cache 