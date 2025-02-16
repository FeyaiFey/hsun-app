from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional

from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.role import RoleItem, UpdateRoleRequest
from app.models.user import User, UserRole
from app.models.role import Role
from app.crud.role import role as crud_role
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.core.deps import get_current_user

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/table", response_model=IResponse[List[RoleItem]])
@monitor_request
async def get_role_table(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取角色列表"""
    try:
        roles = crud_role.get_all_roles(db)
        return CustomResponse.success(data=roles)
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="RoleError"
        )
    except Exception as e:
        logger.error(f"获取角色列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/update", response_model=IResponse[bool])
@monitor_request
async def update_user_roles(
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新用户角色
    
    Args:
        request: 更新请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        更新结果
    """
    try:
        result = crud_role.update_user_roles(db, request=request)
        return CustomResponse.success(data=result)
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="RoleError"
        )
    except Exception as e:
        logger.error(f"更新用户角色失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )



