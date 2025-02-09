from fastapi import Request
from app.schemas.response import IResponse
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
import time

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
                    body = await response.json()
                    # 如果响应已经是 IResponse 格式，直接返回
                    if isinstance(body, dict) and all(key in body for key in ["code", "msg", "data"]):
                        return response
                    # 否则包装成 IResponse 格式
                    return JSONResponse(
                        content=IResponse(
                            code=response.status_code,
                            msg="success",
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
            process_time = time.time() - start_time
            logger.error(
                f"请求处理异常 - 路径: {request.url.path} "
                f"方法: {request.method} "
                f"处理时间: {process_time:.2f}s "
                f"错误: {str(e)}"
            )
            return JSONResponse(
                content=IResponse(
                    code=500,
                    msg="服务器内部错误",
                    data={"error": str(e)}
                ).model_dump(),
                status_code=500
            )
