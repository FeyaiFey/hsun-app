from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any, List
from datetime import timedelta

from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.user import (
    UserLogin,
    UserResponse,
    UserCreate,
    Token,
    UserInfoType,
    UserInfoResponse
)
from app.models.user import User
from app.schemas.department import DepartmentTreeNode
from app.core.deps import get_current_user, get_current_active_user
from app.core.rate_limit import SimpleRateLimiter
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.config import settings
from app.services.auth_service import AuthService, UserInfoResponse
from app.services.menu_service import menu_service
from app.services.department_service import department_service
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

router = APIRouter()

# 创建限流器实例
rate_limiter = SimpleRateLimiter(limit=5, window=60)  # 每分钟最多5次请求

# 创建缓存实例
cache = MemoryCache()

@router.get("/department", response_model=IResponse[List[DepartmentTreeNode]])
@monitor_request
async def get_department_list(
    db: Session = Depends(get_db)
) -> Any:
    """获取部门列表"""
    try:
        # 初始化部门服务
        department_service.db = db
        department_service.cache = cache
        
        # 获取部门树
        departments = await department_service.get_department_tree_for_register()
        
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

@router.post("/login", response_model=IResponse[UserInfoType])
@monitor_request
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    try:
        # 检查限流
        if rate_limiter.is_limited(login_data.email):
            logger.warning(f"登录请求过于频繁: {login_data.email}")
            return CustomResponse.error(
                code=status.HTTP_429_TOO_MANY_REQUESTS,
                message="登录请求过于频繁，请稍后再试",
                name="RateLimitError"
            )
            
        auth_service = AuthService(db, cache)
        
        # 认证用户并获取用户信息
        auth_result = await auth_service.authenticate(login_data.email, login_data.password)
        
        # 构建响应数据
        return CustomResponse.success(data=UserInfoType(**auth_result))
            
    except CustomException as e:
        rate_limiter.increment(login_data.email)
        return CustomResponse.error(
            code=status.HTTP_401_UNAUTHORIZED,
            message=e.message,
            name="AuthenticationError"
        )
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/register", response_model=IResponse[UserResponse])
@monitor_request
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册"""
    try:
        auth_service = AuthService(db, cache)
        user = await auth_service.create_user(user_in)
        return CustomResponse.success(data=user)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="RegistrationError"
        )
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/routes")
@monitor_request
async def get_routes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户动态路由"""
    try:
        # 初始化菜单服务
        menu_service.db = db
        menu_service.cache = cache
        
        # 尝试从缓存获取
        cache_key = f"user:routes:{current_user.id}"
        cached_routes = cache.get(cache_key)
        if cached_routes:
            return CustomResponse.success(data=cached_routes)
        
        # 获取用户菜单
        # 如果是超级管理员id=1，则获取所有菜单
        if current_user.id == 1:
            menus = await menu_service.get_menu_tree()
        else:
            menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return CustomResponse.success(data=menus)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="RouteError"
        )
    except Exception as e:
        logger.error(f"获取用户路由失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.post("/logout", response_model=IResponse[bool])
@monitor_request
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """用户登出"""
    try:
        # 清除用户相关的缓存
        cache_key_routes = f"user:routes:{current_user.id}"
        cache_key_menus = f"user:menus:{current_user.id}"
        cache.delete(cache_key_routes)
        cache.delete(cache_key_menus)
        
        return CustomResponse.success(data=True)
    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/me", response_model=IResponse[UserInfoResponse])
@monitor_request
async def get_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户信息"""
    try:
        return CustomResponse.success(data=current_user)
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="UserInfoError"
        )
    
@router.get("/userinfo", response_model=IResponse[UserInfoResponse])
@monitor_request
async def get_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户信息"""
    try:
        auth_service = AuthService(db, cache)
        user_info = await auth_service.get_entire_user_info(current_user.id)
        return CustomResponse.success(data=user_info)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="UserInfoError"
        )
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/menus")
@monitor_request
async def get_user_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户菜单列表"""
    try:
        auth_service = AuthService(db, cache)
        
        # 尝试从缓存获取
        cache_key = f"user:menus:{current_user.id}"
        cached_menus = cache.get(cache_key)
        if cached_menus:
            return CustomResponse.success(data=cached_menus)
        
        # 获取用户菜单
        menu_service.db = db
        menu_service.cache = cache
        menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return CustomResponse.success(data=menus)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="MenuError"
        )
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/permissions")
@monitor_request
async def get_user_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户权限列表"""
    try:
        auth_service = AuthService(db, cache)
        permissions = await auth_service.get_user_permissions(current_user.id)
        return CustomResponse.success(data=permissions)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="PermissionError"
        )
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/refresh-token", response_model=IResponse[Token])
@monitor_request
async def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """刷新访问令牌"""
    try:
        auth_service = AuthService(db, cache)
        
        # 生成新令牌
        access_token = await auth_service.create_access_token(
            current_user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = await auth_service.create_refresh_token(current_user.id)
        
        return CustomResponse.success(
            data=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="TokenError"
        )
    except Exception as e:
        logger.error(f"刷新令牌失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
