from fastapi import Request
from app.schemas.response import IResponse
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
import time

class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            
            # 记录请求处理时间
            process_time = time.time() - start_time
            logger.info(
                f"请求处理完成 - 路径: {request.url.path} "
                f"方法: {request.method} "
                f"处理时间: {process_time:.2f}s"
            )
            
            # 如果已经是 JSONResponse，直接返回
            if isinstance(response, JSONResponse):
                return response
                
            # 处理其他响应
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await response.json()
                    return JSONResponse(
                        content=IResponse(
                            code=response.status_code,
                            data=body
                        ).model_dump(),
                        status_code=response.status_code
                    )
                except:
                    # JSON 解析失败，返回原响应
                    return response
            
            # 非 JSON 响应直接返回
            return response
            
        except Exception as e:
            logger.error(f"请求处理异常: {str(e)}")
            return JSONResponse(
                content=IResponse(
                    code=500,
                    data={"error": str(e), "detail": "服务器内部错误"}
                ).model_dump(),
                status_code=500
            )
