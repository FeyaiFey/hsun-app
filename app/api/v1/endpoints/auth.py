from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Any, List
from datetime import timedelta

from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.user import (
    UserLogin,
    UserResponse,
    UserCreate,
    Token
)
from app.models.user import User
from app.schemas.menu import DepartmentResponse
from app.core.deps import get_current_user, get_current_active_user
from app.core.rate_limit import SimpleRateLimiter
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.config import settings
from app.services.auth_service import AuthService
from app.services.menu_service import menu_service
from app.services.department_service import department_service
from app.services.cache_service import cache_service
from app.core.exceptions import (
    DatabaseError,
    AuthenticationError,
    NotFoundError,
    ValidationError
)

router = APIRouter()

# 创建限流器实例
rate_limiter = SimpleRateLimiter(limit=5, window=60)  # 每分钟最多5次请求

# 创建缓存实例
cache = MemoryCache()

@router.get("/department", response_model=IResponse[List[DepartmentResponse]])
@monitor_request
async def get_department_list(
    db: Session = Depends(get_db)
) -> Any:
    """获取部门列表
    
    Returns:
        IResponse[List[DepartmentResponse]]: 部门树形结构
    """
    try:
        # 初始化部门服务
        department_service.db = db
        department_service.cache = cache
        
        # 获取部门树
        departments = await department_service.get_department_tree()
        return IResponse(code=200, data=departments)
        
    except DatabaseError as e:
        logger.error(f"获取部门列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取部门列表异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门列表失败"
        )

@router.post("/login", response_model=IResponse[Token])
@monitor_request
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """用户登录
    
    Args:
        form_data: 登录表单数据
        
    Returns:
        IResponse[Token]: 登录令牌
    """
    try:
        # 检查限流
        if rate_limiter.is_limited(form_data.username):
            logger.warning(f"登录请求过于频繁: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="登录请求过于频繁，请稍后再试"
            )
            
        auth_service = AuthService(db, cache)
        
        try:
            user = await auth_service.authenticate(form_data.username, form_data.password)
        except AuthenticationError as e:
            rate_limiter.increment(form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        
        # 更新最后登录时间
        await auth_service.update_user_login(user.id)
        
        # 生成令牌
        access_token = await auth_service.create_access_token(
            user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = await auth_service.create_refresh_token(user.id)
        
        return IResponse(
            code=200,
            data=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )

@router.post("/register", response_model=IResponse[UserResponse])
@monitor_request
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册
    
    Args:
        user_in: 用户注册信息
        
    Returns:
        IResponse[UserResponse]: 注册成功的用户信息
    """
    try:
        auth_service = AuthService(db, cache)
        user = await auth_service.create_user(user_in)
        return IResponse(code=200, data=user)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败"
        )

@router.get("/routes")
@monitor_request
async def get_routes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户动态路由
    
    Returns:
        Any: 用户可访问的路由列表
    """
    try:
        # 初始化菜单服务
        menu_service.db = db
        menu_service.cache = cache
        
        # 尝试从缓存获取
        cache_key = f"user:routes:{current_user.id}"
        cached_routes = cache.get(cache_key)
        if cached_routes:
            return IResponse(code=200, data=cached_routes)
        
        # 获取用户菜单
        menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return IResponse(code=200, data=menus)
        
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取用户路由失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取路由失败"
        )

@router.get("/me", response_model=IResponse[UserResponse])
@monitor_request
async def get_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户信息
    
    Returns:
        IResponse[UserResponse]: 当前用户信息
    """
    try:
        return IResponse(code=200, data=current_user)
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )

@router.get("/menus")
@monitor_request
async def get_user_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户菜单列表
    
    Returns:
        Any: 用户可访问的菜单列表
    """
    try:
        auth_service = AuthService(db, cache)
        
        # 尝试从缓存获取
        cache_key = f"user:menus:{current_user.id}"
        cached_menus = cache.get(cache_key)
        if cached_menus:
            return IResponse(code=200, data=cached_menus)
        
        # 获取用户菜单
        menu_service.db = db
        menu_service.cache = cache
        menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return IResponse(code=200, data=menus)
        
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单失败"
        )

@router.get("/permissions")
@monitor_request
async def get_user_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户权限列表
    
    Returns:
        Any: 用户权限列表
    """
    try:
        auth_service = AuthService(db, cache)
        permissions = await auth_service.get_user_permissions(current_user.id)
        return IResponse(code=200, data=permissions)
        
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取权限失败"
        )

@router.post("/refresh-token", response_model=IResponse[Token])
@monitor_request
async def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """刷新访问令牌
    
    Returns:
        IResponse[Token]: 新的访问令牌
    """
    try:
        auth_service = AuthService(db, cache)
        
        # 生成新令牌
        access_token = await auth_service.create_access_token(
            current_user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = await auth_service.create_refresh_token(current_user.id)
        
        return IResponse(
            code=200,
            data=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"刷新令牌失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌失败"
        )
