from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional

from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.user import (
    UserUpdate, 
    UserInfoResponse, 
    UserCreate,
    UserTableListResponse,
    UpdatePasswordRequest,
    BatchDeleteRequest
)
from app.models.user import User
from app.core.deps import get_current_active_user
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.services.auth_service import AuthService
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.core.deps import get_current_user
from app.services.user_service import user_service
from app.services.department_service import department_service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.put("/update", response_model=IResponse[UserInfoResponse])
@monitor_request
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户基本信息"""
    try:
        # 确保不包含密码字段
        if hasattr(user_data, "password"):
            delattr(user_data, "password")
            
        # 注入数据库会话和缓存
        auth_service = AuthService(db, cache)
        
        # 更新用户信息
        user = await auth_service.update_user(current_user.id, user_data)
        
        # 获取完整的用户信息
        user_info = await auth_service.get_entire_user_info(user.id)
        return CustomResponse.success(data=user_info, message="更新成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"更新用户信息异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/password", response_model=IResponse)
@monitor_request
async def update_password(
    password_data: UpdatePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户密码"""
    try:
        from app.core.security import verify_password
        
        # 验证旧密码
        if not verify_password(password_data.old_password, current_user.password_hash):
            return CustomResponse.error(
                code=status.HTTP_400_BAD_REQUEST,
                message="旧密码错误",
                name="PasswordError"
            )
            
        # 创建更新数据
        update_data = UserUpdate(password=password_data.new_password)
        
        # 注入数据库会话和缓存
        auth_service = AuthService(db, cache)
        
        # 更新密码
        await auth_service.update_user(current_user.id, update_data)
        return CustomResponse.success(message="密码更新成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"更新用户密码异常: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/list", response_model=IResponse[UserTableListResponse])
@monitor_request
async def get_user_list(
    username: Optional[str] = Query(None, description="用户名"),
    email: Optional[str] = Query(None, description="邮箱"),
    department_id: Optional[int] = Query(None, description="部门ID"),
    account_status: Optional[int] = Query(None, description="状态"),
    pageIndex: int = Query(1, description="页码"),
    pageSize: int = Query(10, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序字段"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取用户列表"""
    try:
        # 注入数据库会话和缓存
        user_service.db = db
        user_service.cache = cache
        
        # 注入部门服务的依赖
        department_service.db = db
        department_service.cache = cache
        
        # 构建查询参数
        params = {
            "username": username,
            "email": email,
            "department_id": department_id,
            "status": account_status,
            "pageIndex": pageIndex,
            "pageSize": pageSize,
            "order_by": order_by
        }
        
        # 获取用户列表
        result = await user_service.get_users_list_with_params(params)
        return CustomResponse.success(data=result)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/save", response_model=IResponse)
@monitor_request
async def save_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """创建用户"""
    try:
        # 注入数据库会话
        user_service.db = db
        
        # 创建用户
        await user_service.create_user(user_in)
        return CustomResponse.success(message="创建成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/{user_id}", response_model=IResponse)
@monitor_request
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新用户"""
    try:
        # 注入数据库会话
        user_service.db = db
        
        # 更新用户
        await user_service.update_user(user_id, user_in)
        return CustomResponse.success(message="更新成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.delete("/{user_id}", response_model=IResponse)
@monitor_request
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除用户"""
    try:
        # 注入数据库会话
        user_service.db = db
        
        # 删除用户
        await user_service.delete_user(user_id)
        return CustomResponse.success(message="删除成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/batch/delete", response_model=IResponse)
@monitor_request
async def batch_delete_users(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """批量删除用户"""
    try:
        # 注入数据库会话
        user_service.db = db
        
        # 批量删除用户
        await user_service.batch_delete_users(data.ids)
        return CustomResponse.success(message="删除成功")
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="UserError"
        )
    except Exception as e:
        logger.error(f"批量删除用户失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )