from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.schemas.response import IResponse
from app.core.logger import logger
from typing import Any, Dict, Optional

class BaseCustomException(HTTPException):
    """自定义异常基类"""
    def __init__(self, detail: str = None):
        super().__init__(status_code=500, detail=detail)

class DatabaseError(BaseCustomException):
    """数据库操作异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "数据库操作失败")

class AuthenticationError(BaseCustomException):
    """认证异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "认证失败")

class NotFoundError(BaseCustomException):
    """资源不存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "资源不存在")

class ValidationError(BaseCustomException):
    """数据验证异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "数据验证失败")

class ConflictError(BaseCustomException):
    """资源冲突异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "资源冲突")

class PermissionError(BaseCustomException):
    """权限异常"""
    def __init__(self, detail: str = None):
        super().__init__(detail=detail or "权限不足")

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: JSON响应
    """
    if isinstance(exc, BaseCustomException):
        logger.warning(
            f"API异常 - 路径: {request.url.path} "
            f"状态码: {exc.status_code} "
            f"详情: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=IResponse(
                code=500,
                data={"error": exc.detail}
            ).model_dump()
        )
    
    # 处理其他未知异常
    logger.error(f"未知异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=IResponse(
            code=500,
            data={"error": str(exc)}
        ).model_dump()
    )

async def database_exception_handler(request, exc):
    """数据库异常处理器"""
    return JSONResponse(
        status_code=500,
        content=IResponse(
            code=500,
            data={"error": str(exc.detail)}
        ).model_dump()
    )

async def validation_exception_handler(request, exc):
    """验证异常处理器"""
    return JSONResponse(
        status_code=400,
        content=IResponse(
            code=400,
            data={"error": str(exc.detail)}
        ).model_dump()
    ) 