from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.core.security import verify_token
from app.db.session import get_db
from app.crud.user import user as user_crud
from app.core.cache import MemoryCache
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_cache() -> MemoryCache:
    """获取缓存实例"""
    try:
        return MemoryCache()
    except Exception as e:
        logger.error(f"获取缓存实例失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取当前用户
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        CustomException: 认证失败时抛出
    """
    try:
        # 验证token
        payload = verify_token(token)
        user_id = payload.get("sub")

        # 检查user_id是否存在
        if not user_id:
            logger.warning("令牌中缺少用户ID")
            raise CustomException(
                code=status.HTTP_401_UNAUTHORIZED,
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )
        
        # 尝试转换user_id为整数
        try:
            user_id_int = int(user_id)
        except ValueError:
            logger.warning(f"无效的用户ID格式: {user_id}")
            raise CustomException(
                code=status.HTTP_401_UNAUTHORIZED,
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )
            
        # 查询用户
        user = user_crud.get(db, id=user_id_int)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            raise CustomException(
                code=status.HTTP_404_NOT_FOUND,
                message=get_error_message(ErrorCode.USER_NOT_FOUND)
            )
            
        return user
        
    except CustomException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR)
        )

async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """获取当前活动用户
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 当前活动用户对象
        
    Raises:
        CustomException: 用户被禁用时抛出
    """
    if not current_user.status:
        logger.warning(f"用户已被禁用: {current_user.id}")
        raise CustomException(
            code=status.HTTP_403_FORBIDDEN,
            message=get_error_message(ErrorCode.ACCOUNT_LOCKED)
        )
    return current_user