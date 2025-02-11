from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.schemas.response import IResponse
from app.core.logger import logger
from typing import Any, Dict, Optional
from app.core.error_codes import ErrorCode, HttpStatusCode, get_status_text

class CustomException(Exception):
    """自定义异常基类"""
    def __init__(
        self,
        code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "Bad Request",
    ):
        self.code = code
        self.message = message
        super().__init__(message)

class AuthenticationException(CustomException):
    """认证异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            code=status.HTTP_401_UNAUTHORIZED,
            message=message
        )

class PermissionDeniedException(CustomException):
    """权限异常"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            code=status.HTTP_403_FORBIDDEN,
            message=message
        )

class NotFoundException(CustomException):
    """资源不存在异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            code=status.HTTP_404_NOT_FOUND,
            message=message
        )

class ValidationException(CustomException):
    """数据验证异常"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message
        )

class DatabaseException(CustomException):
    """数据库操作异常"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message
        )

class BusinessException(CustomException):
    """业务逻辑异常"""
    def __init__(self, message: str = "Business logic error"):
        super().__init__(
            code=status.HTTP_400_BAD_REQUEST,
            message=message
        )

def get_error_response(status_code: int, message: str, error_code: str) -> Dict[str, Any]:
    """构建错误响应"""
    return {
        "code": status_code,
        "data": {
            "message": message,
            "error_code": error_code
        }
    }

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    if isinstance(exc, CustomException):
        logger.warning(
            f"API异常 - 路径: {request.url.path} "
            f"状态码: {exc.code} "
            f"详情: {exc.message}"
        )
        return JSONResponse(
            status_code=exc.code,
            content=get_error_response(
                status_code=exc.code,
                message=exc.message,
                error_code=ErrorCode.ERR_INTERNAL_SERVER
            )
        )
    
    # 处理其他未知异常
    logger.error(f"未知异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=HttpStatusCode.InternalServerError,
        content=get_error_response(
            status_code=HttpStatusCode.InternalServerError,
            message=str(exc),
            error_code=ErrorCode.ERR_INTERNAL_SERVER
        )
    )

async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """数据库异常处理器"""
    logger.error(f"数据库异常: {str(exc.message)}")
    return JSONResponse(
        status_code=HttpStatusCode.InternalServerError,
        content=get_error_response(
            status_code=HttpStatusCode.InternalServerError,
            message=exc.message,
            error_code=ErrorCode.ERR_INTERNAL_SERVER
        )
    )

async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """验证异常处理器"""
    logger.warning(f"数据验证失败: {str(exc.message)}")
    return JSONResponse(
        status_code=HttpStatusCode.BadRequest,
        content=get_error_response(
            status_code=HttpStatusCode.BadRequest,
            message=exc.message,
            error_code=ErrorCode.ERR_BAD_REQUEST
        )
    ) 