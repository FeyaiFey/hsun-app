from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.schemas.response import IResponse
from app.core.logger import logger
from typing import Any, Dict, Optional

class APIException(HTTPException):
    """API异常基类"""
    def __init__(
        self,
        status_code: int,
        detail: str = None,
        error_code: int = None,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or status_code
        self.data = data or {}

class DatabaseError(APIException):
    """数据库操作异常"""
    def __init__(self, detail: str = "数据库操作失败", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, detail=detail, error_code=50001, data=data)

class AuthenticationError(APIException):
    """认证异常"""
    def __init__(self, detail: str = "认证失败", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, detail=detail, error_code=40100, data=data)

class PermissionError(APIException):
    """权限异常"""
    def __init__(self, detail: str = "权限不足", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=403, detail=detail, error_code=40300, data=data)

class NotFoundError(APIException):
    """资源不存在异常"""
    def __init__(self, detail: str = "资源不存在", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, detail=detail, error_code=40400, data=data)

class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, detail: str = "数据验证失败", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, detail=detail, error_code=40000, data=data)

class ConflictError(APIException):
    """数据冲突异常"""
    def __init__(self, detail: str = "数据已存在", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, detail=detail, error_code=40900, data=data)

class UserError(APIException):
    """用户相关异常"""
    def __init__(self, detail: str = "用户操作失败", data: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, detail=detail, error_code=40001, data=data)

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: JSON响应
    """
    if isinstance(exc, APIException):
        logger.warning(
            f"API异常 - 路径: {request.url.path} "
            f"状态码: {exc.status_code} "
            f"错误码: {exc.error_code} "
            f"详情: {exc.detail} "
            f"数据: {exc.data}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=IResponse(
                code=exc.error_code,
                msg=exc.detail,
                data=exc.data
            ).model_dump()
        )
    
    # 处理其他未知异常
    logger.error(f"未知异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=IResponse(
            code=500,
            msg="服务器内部错误",
            data={"detail": str(exc)}
        ).model_dump()
    ) 