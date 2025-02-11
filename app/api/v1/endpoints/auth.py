from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
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
    UserType
)
from app.models.user import User
from app.schemas.department import DepartmentTreeNode
from app.core.deps import get_current_user, get_current_active_user
from app.core.rate_limit import SimpleRateLimiter
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.config import settings
from app.services.auth_service import AuthService
from app.services.menu_service import menu_service
from app.services.department_service import department_service
from app.core.exceptions import (
    DatabaseError,
    AuthenticationError,
    ValidationError,
    get_error_response
)
from app.core.error_codes import ErrorCode, HttpStatusCode

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
    """获取部门列表
    
    Returns:
        IResponse[List[DepartmentResponse]]: 部门树形结构
    """
    try:
        # 初始化部门服务
        department_service.db = db
        department_service.cache = cache
        
        # 获取部门树
        departments = await department_service.get_department_tree_for_register()
        
        return IResponse(
            code=HttpStatusCode.Ok,
            data=departments
        )
        
    except DatabaseError as e:
        logger.error(f"获取部门列表失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"获取部门列表异常: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "获取部门列表失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )

@router.post("/login", response_model=IResponse[UserInfoType])
@monitor_request
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录
    
    Args:
        login_data: 登录表单数据
        
    Returns:
        IResponse[UserInfoType]: 用户信息和令牌
    """
    try:
        # 检查限流
        if rate_limiter.is_limited(login_data.email):
            logger.warning(f"登录请求过于频繁: {login_data.email}")
            return JSONResponse(
                status_code=HttpStatusCode.TooManyRequests,
                content={
                    "isAxiosError": True,
                    "name": "AxiosError",
                    "message": "登录请求过于频繁，请稍后再试",
                    "code": ErrorCode.ERR_BAD_REQUEST,
                    "status": HttpStatusCode.TooManyRequests,
                    "response": {
                        "status": HttpStatusCode.TooManyRequests,
                        "statusText": "Too Many Requests",
                        "data": None
                    }
                }
            )
            
        auth_service = AuthService(db, cache)
        
        try:
            # 认证用户并获取用户信息
            auth_result = await auth_service.authenticate(login_data.email, login_data.password)
            
            # 构建响应数据
            return IResponse(
                code=HttpStatusCode.Ok,
                data=UserInfoType(**auth_result)
            )
            
        except AuthenticationError as e:
            rate_limiter.increment(login_data.email)
            return JSONResponse(
                status_code=HttpStatusCode.Unauthorized,
                content={
                    "isAxiosError": True,
                    "name": "AxiosError",
                    "message": str(e.detail),
                    "code": ErrorCode.ERR_UNAUTHORIZED,
                    "status": HttpStatusCode.Unauthorized,
                    "response": {
                        "status": HttpStatusCode.Unauthorized,
                        "statusText": "Unauthorized",
                        "data": None
                    }
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "登录失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
        return IResponse(
            code=HttpStatusCode.Ok,
            data=user
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=HttpStatusCode.BadRequest,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_BAD_REQUEST,
                "status": HttpStatusCode.BadRequest,
                "response": {
                    "status": HttpStatusCode.BadRequest,
                    "statusText": "Bad Request",
                    "data": None
                }
            }
        )
    except DatabaseError as e:
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "注册失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
            return IResponse(
                code=HttpStatusCode.Ok,
                data=cached_routes
            )
        
        # 获取用户菜单
        menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return IResponse(
            code=HttpStatusCode.Ok,
            data=menus
        )
        
    except DatabaseError as e:
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"获取用户路由失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "获取路由失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
        return IResponse(
            code=HttpStatusCode.Ok,
            data=current_user
        )
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "获取用户信息失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
            return IResponse(
                code=HttpStatusCode.Ok,
                data=cached_menus
            )
        
        # 获取用户菜单
        menu_service.db = db
        menu_service.cache = cache
        menus = await menu_service.get_user_menus(current_user.id)
        
        # 缓存结果
        cache.set(cache_key, menus, expire=3600)
        
        return IResponse(
            code=HttpStatusCode.Ok,
            data=menus
        )
        
    except DatabaseError as e:
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "获取菜单失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
        return IResponse(
            code=HttpStatusCode.Ok,
            data=permissions
        )
        
    except DatabaseError as e:
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "获取用户权限失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
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
            code=HttpStatusCode.Ok,
            data=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except DatabaseError as e:
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": str(e.detail),
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
    except Exception as e:
        logger.error(f"刷新令牌失败: {str(e)}")
        return JSONResponse(
            status_code=HttpStatusCode.InternalServerError,
            content={
                "isAxiosError": True,
                "name": "AxiosError",
                "message": "刷新令牌失败",
                "code": ErrorCode.ERR_INTERNAL_SERVER,
                "status": HttpStatusCode.InternalServerError,
                "response": {
                    "status": HttpStatusCode.InternalServerError,
                    "statusText": "Internal Server Error",
                    "data": None
                }
            }
        )
