from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.schemas.response import IResponse
from app.core.logger import logger
from typing import Any, Dict, Optional
from enum import Enum

class ErrorCode(str, Enum):
    """错误代码枚举"""
    ERR_NETWORK = "ERR_NETWORK"
    ERR_BAD_REQUEST = "ERR_BAD_REQUEST"
    ERR_BAD_RESPONSE = "ERR_BAD_RESPONSE"
    ERR_NOT_SUPPORT = "ERR_NOT_SUPPORT"
    ERR_INVALID_URL = "ERR_INVALID_URL"
    ERR_CANCELED = "ERR_CANCELED"
    ECONNABORTED = "ECONNABORTED"
    ETIMEDOUT = "ETIMEDOUT"
    ERR_UNAUTHORIZED = "ERR_UNAUTHORIZED"
    ERR_FORBIDDEN = "ERR_FORBIDDEN"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_CONFLICT = "ERR_CONFLICT"
    ERR_INTERNAL_SERVER = "ERR_INTERNAL_SERVER"

class BaseCustomException(HTTPException):
    """自定义异常基类"""
    def __init__(
        self,
        detail: str = None,
        status_code: int = 500,
        code: str = ErrorCode.ERR_INTERNAL_SERVER
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.name = self.__class__.__name__
        self.code = code

class DatabaseError(BaseCustomException):
    """数据库操作异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "数据库操作失败",
            status_code=500,
            code=ErrorCode.ERR_INTERNAL_SERVER
        )

class AuthenticationError(BaseCustomException):
    """认证异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "认证失败",
            status_code=401,
            code=ErrorCode.ERR_UNAUTHORIZED
        )

class NotFoundError(BaseCustomException):
    """资源不存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "资源不存在",
            status_code=404,
            code=ErrorCode.ERR_NOT_FOUND
        )

class ValidationError(BaseCustomException):
    """数据验证异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "数据验证失败",
            status_code=400,
            code=ErrorCode.ERR_BAD_REQUEST
        )

class ConflictError(BaseCustomException):
    """资源冲突异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "资源冲突",
            status_code=409,
            code=ErrorCode.ERR_CONFLICT
        )

class PermissionError(BaseCustomException):
    """权限异常"""
    def __init__(self, detail: str = None):
        super().__init__(
            detail=detail or "权限不足",
            status_code=403,
            code=ErrorCode.ERR_FORBIDDEN
        )

def get_error_response(status_code: int, message: str, error_code: str) -> Dict[str, Any]:
    """构建错误响应"""
    return {
        "isAxiosError": True,
        "name": "AxiosError",
        "message": message,
        "code": error_code,
        "status": status_code,
        "response": {
            "data": {
                "code": status_code,
                "message": message,
                "status": status_code,
                "statusText": get_status_text(status_code)
            }
        }
    }

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    if isinstance(exc, BaseCustomException):
        logger.warning(
            f"API异常 - 路径: {request.url.path} "
            f"状态码: {exc.status_code} "
            f"详情: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=get_error_response(
                status_code=exc.status_code,
                message=str(exc.detail),
                error_code=exc.code
            )
        )
    
    # 处理其他未知异常
    logger.error(f"未知异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=get_error_response(
            status_code=500,
            message=str(exc),
            error_code=ErrorCode.ERR_INTERNAL_SERVER
        )
    )

def get_status_text(status_code: int) -> str:
    """获取状态码对应的文本描述"""
    status_texts = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        500: "Internal Server Error"
    }
    return status_texts.get(status_code, "Unknown Error")

async def database_exception_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """数据库异常处理器"""
    logger.error(f"数据库异常: {str(exc.detail)}")
    return JSONResponse(
        status_code=500,
        content=get_error_response(
            status_code=500,
            message=str(exc.detail),
            error_code=ErrorCode.ERR_INTERNAL_SERVER
        )
    )

async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """验证异常处理器"""
    logger.warning(f"数据验证失败: {str(exc.detail)}")
    return JSONResponse(
        status_code=400,
        content=get_error_response(
            status_code=400,
            message=str(exc.detail),
            error_code=ErrorCode.ERR_BAD_REQUEST
        )
    ) 