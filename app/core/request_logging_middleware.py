import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import log_request, log_error

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """简化的请求日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录关键日志"""
        start_time = time.time()
        
        # 处理请求
        response = None
        error = None
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            # 记录异常详情
            log_error(f"请求处理异常: {request.method} {request.url.path}")
            raise
        finally:
            # 计算处理时间
            duration = time.time() - start_time
            
            # 记录请求日志
            status_code = response.status_code if response else 500
            error_msg = str(error) if error else None
            
            log_request(
                method=request.method,
                path=request.url.path,
                duration=duration,
                status_code=status_code,
                error=error_msg
            )
        
        return response 