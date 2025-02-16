from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any, List
from datetime import timedelta

from app.crud.department import department
from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.department import (
    DepartmentListResponse,
    DepartmentTableListResponse,
    BatchDeleteRequest
)
from app.core.rate_limit import SimpleRateLimiter
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.services.department_service import department_service
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

router = APIRouter()

# 创建限流器实例
rate_limiter = SimpleRateLimiter(limit=5, window=60)  # 每分钟最多5次请求

# 创建缓存实例
cache = MemoryCache()

@router.get("/list", response_model=IResponse[DepartmentListResponse])
@monitor_request
async def get_department_list(
    # current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取部门列表
    
    Returns:
        IResponse[DepartmentListResponse]: 树形结构的部门列表响应
    """
    try:
        # 注入数据库会话和缓存
        department_service.db = db
        department_service.cache = cache
        
        # 获取树形结构的部门列表
        departments = await department_service.get_department_tree()
        return CustomResponse.success(data=departments)
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="DepartmentError"
        )
    except Exception as e:
        logger.error(f"获取部门列表异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    

@router.get("/table/list", response_model=IResponse[DepartmentTableListResponse])
@monitor_request
async def get_department_table_list(
    department_name: str = None,
    status: int = None,
    pageIndex: int = 1,
    pageSize: int = 10,
    order_by: str = None,
    use_cache: bool = True,
    # current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取部门表格列表数据
    
    Args:
        department_name: 部门名称，可选
        status: 状态，可选（1-启用，0-禁用）
        pageIndex: 页码，默认1
        pageSize: 每页数量，默认10
        order_by: 排序字段，可选
        use_cache: 是否使用缓存，默认True
        db: 数据库会话
        
    Returns:
        IResponse[DepartmentTableListResponse]: 包含部门列表数据和总记录数的响应
    """
    try:
        # 注入数据库会话和缓存
        department_service.db = db
        department_service.cache = cache
        
        # 构建查询参数
        query_params = {
            "department_name": department_name,
            "status": status,
            "pageIndex": pageIndex,
            "pageSize": pageSize,
            "order_by": order_by
        }
        
        # 获取部门列表
        departments = await department_service.get_departments_list_with_params(
            query_params,
            use_cache=use_cache
        )
        return CustomResponse.success(data=departments)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="DepartmentError"
        )
    except Exception as e:
        logger.error(f"获取部门列表异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/save", response_model=IResponse)
@monitor_request
async def save_department(
    department_data: dict,
    db: Session = Depends(get_db)
) -> Any:
    """保存部门信息
    
    Args:
        department_data: 部门数据，包含：
            - id: 部门ID（可选，更新时需要）
            - department_name: 部门名称
            - parent_id: 父部门ID（可选）
            - status: 状态（1-启用，0-禁用）
            
    Returns:
        IResponse: 保存结果，包含更新后的部门列表数据
    """
    try:
        # 注入数据库会话和缓存
        department_service.db = db
        department_service.cache = cache
        
        # 保存部门信息
        await department_service.save_department(department_data)
        
        # 清除缓存并重新查询部门列表
        departments = await department_service.get_department_tree()
        
        # 根据操作类型返回不同的成功消息
        message = "更新成功" if "id" in department_data else "创建成功"
        return CustomResponse.success(data=departments, message=message)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="DepartmentError"
        )
    except Exception as e:
        logger.error(f"保存部门信息异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.delete("/{id}", response_model=IResponse)
@monitor_request
async def delete_department(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """删除部门
    
    Args:
        id: 部门ID
        
    Returns:
        IResponse: 删除结果
    """
    try:
        # 注入数据库会话
        department_service.db = db
        
        # 删除部门
        await department_service.delete_department(id)
        return CustomResponse.success(message="删除成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="DepartmentError"
        )
    except Exception as e:
        logger.error(f"删除部门异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/batch/delete", response_model=IResponse)
@monitor_request
async def batch_delete_departments(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db)
) -> Any:
    """批量删除部门
    
    Args:
        data: 包含部门ID列表的请求数据
        db: 数据库会话
        
    Returns:
        IResponse: 删除结果
    """
    try:
        # 注入数据库会话
        department_service.db = db
        print(data.ids)
        
        # 批量删除部门
        await department_service.batch_delete_departments(data.ids)
        return CustomResponse.success(message="删除成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="DepartmentError"
        )
    except Exception as e:
        logger.error(f"批量删除部门异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )