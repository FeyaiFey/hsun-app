from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.schemas.response import IResponse
from app.core.logger import logger

class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str = None,
        error_code: int = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or status_code

class DatabaseError(APIException):
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(status_code=500, detail=detail, error_code=50001)

class AuthenticationError(APIException):
    def __init__(self, detail: str = "认证失败"):
        super().__init__(status_code=401, detail=detail, error_code=40100)

class PermissionError(APIException):
    def __init__(self, detail: str = "权限不足"):
        super().__init__(status_code=403, detail=detail, error_code=40300)

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    if isinstance(exc, APIException):
        logger.warning(
            f"API异常 - 路径: {request.url.path} "
            f"状态码: {exc.status_code} "
            f"详情: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=IResponse(
                code=exc.error_code,
                data={"detail": exc.detail}
            ).model_dump()
        )
    
    # 处理其他未知异常
    logger.error(f"未知异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=IResponse(
            code=500,
            data={"detail": "服务器内部错误"}
        ).model_dump()
    ) 