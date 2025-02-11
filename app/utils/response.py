from fastapi import Request
from app.schemas.response import IResponse
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
from app.core.error_codes import HttpStatusCode, ErrorCode
import time
import json

class ResponseMiddleware(BaseHTTPMiddleware):
    """响应处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求和响应
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
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
                    # 尝试获取响应内容
                    body = await response.body()
                    if not body:
                        return response
                        
                    data = json.loads(body)
                    
                    # 如果响应已经是 IResponse 格式，直接返回
                    if isinstance(data, dict) and all(key in data for key in ["code", "data"]):
                        return response
                        
                    # 否则包装成 IResponse 格式
                    return JSONResponse(
                        content=IResponse(
                            code=response.status_code,
                            data=data
                        ).model_dump(),
                        status_code=response.status_code
                    )
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                    # JSON 解析失败，返回原响应
                    return response
            
            # 非 JSON 响应直接返回
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"请求处理异常 - 路径: {request.url.path} "
                f"方法: {request.method} "
                f"处理时间: {process_time:.2f}s "
                f"错误: {str(e)}"
            )
            return JSONResponse(
                status_code=HttpStatusCode.InternalServerError,
                content=IResponse(
                    code=HttpStatusCode.InternalServerError,
                    data=None
                ).model_dump()
            )

    def _get_status_text(self, status_code: int) -> str:
        """获取状态码对应的文本描述"""
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            429: "Too Many Requests",
            500: "Internal Server Error"
        }
        return status_texts.get(status_code, "Unknown Status")
