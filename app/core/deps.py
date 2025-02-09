from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.core.security import verify_token
from app.db.session import get_db
from app.crud.user import user as user_crud
from app.core.cache import MemoryCache
from app.core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_cache() -> MemoryCache:
    """获取缓存实例"""
    return MemoryCache()

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
        HTTPException: 认证失败时抛出
    """
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("令牌中缺少用户ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证令牌失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.get(db, id=int(user_id))
    if user is None:
        logger.warning(f"用户不存在: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """获取当前活动用户
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 当前活动用户对象
        
    Raises:
        HTTPException: 用户被禁用时抛出
    """
    if not current_user.status:
        logger.warning(f"用户已被禁用: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user