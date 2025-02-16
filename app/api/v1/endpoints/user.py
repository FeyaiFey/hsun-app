from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.user import UserUpdate, UserInfoResponse
from app.models.user import User
from app.core.deps import get_current_active_user
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.services.auth_service import AuthService
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

class UpdatePasswordRequest(BaseModel):
    """更新密码请求模型"""
    old_password: str
    new_password: str

@router.put("/update", response_model=IResponse[UserInfoResponse])
@monitor_request
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户基本信息
    
    Args:
        user_data: 用户更新数据，包含：
            - username: 用户名（可选）
            - email: 邮箱（可选）
            - department_id: 部门ID（可选）
            - status: 状态（可选）
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        IResponse[UserInfoResponse]: 更新后的用户信息
    """
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
    """更新用户密码
    
    Args:
        password_data: 密码更新数据，包含：
            - old_password: 旧密码
            - new_password: 新密码
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        IResponse: 更新结果
    """
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
