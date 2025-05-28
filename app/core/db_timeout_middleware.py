import asyncio
import time
import threading
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.logger import logger
from app.db.session import active_connections, connection_lock, cleanup_expired_connections


class DatabaseTimeoutMiddleware(BaseHTTPMiddleware):
    """数据库超时中间件"""
    
    def __init__(self, app, timeout: int = None):
        super().__init__(app)
        self.timeout = timeout or settings.DB_QUERY_TIMEOUT
        self.active_requests = {}
        self.request_lock = threading.Lock()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并监控数据库操作超时"""
        request_id = id(request)
        start_time = time.time()
        
        # 记录请求开始
        with self.request_lock:
            self.active_requests[request_id] = {
                'start_time': start_time,
                'path': request.url.path,
                'method': request.method
            }
        
        try:
            # 在后台启动超时监控任务
            timeout_task = asyncio.create_task(
                self._monitor_request_timeout(request_id, start_time)
            )
            
            # 执行请求
            response = await call_next(request)
            
            # 取消超时监控
            timeout_task.cancel()
            
            # 记录请求完成时间
            execution_time = time.time() - start_time
            
            # 如果执行时间超过阈值，记录警告
            if execution_time > self.timeout:
                logger.warning(
                    f"请求执行时间超过阈值: {request.method} {request.url.path} "
                    f"执行时间: {execution_time:.2f}秒 > {self.timeout}秒"
                )
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"请求超时: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=408,
                content={
                    "code": 408,
                    "message": "请求超时，数据库操作时间过长",
                    "data": None
                }
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"请求执行失败: {request.method} {request.url.path} "
                f"执行时间: {execution_time:.2f}秒, 错误: {str(e)}"
            )
            raise
        finally:
            # 清理请求记录
            with self.request_lock:
                self.active_requests.pop(request_id, None)
            
            # 定期清理过期连接
            if time.time() % 30 < 1:  # 每30秒清理一次
                cleanup_expired_connections()
    
    async def _monitor_request_timeout(self, request_id: int, start_time: float):
        """监控请求超时"""
        try:
            await asyncio.sleep(self.timeout)
            
            # 检查请求是否仍在执行
            with self.request_lock:
                if request_id in self.active_requests:
                    request_info = self.active_requests[request_id]
                    execution_time = time.time() - start_time
                    
                    logger.warning(
                        f"检测到长时间运行的请求: {request_info['method']} {request_info['path']} "
                        f"已运行: {execution_time:.2f}秒"
                    )
                    
                    # 强制清理相关的数据库连接
                    self._force_cleanup_connections()
                    
        except asyncio.CancelledError:
            # 请求正常完成，取消监控
            pass
    
    def _force_cleanup_connections(self):
        """强制清理长时间运行的数据库连接"""
        current_time = time.time()
        force_close_connections = []
        
        with connection_lock:
            for conn_id, conn_info in active_connections.items():
                # 如果连接活跃时间超过超时阈值，强制关闭
                if current_time - conn_info['last_activity'] > self.timeout:
                    force_close_connections.append((conn_id, conn_info))
        
        # 强制关闭连接
        for conn_id, conn_info in force_close_connections:
            try:
                conn_info['connection'].close()
                logger.warning(f"强制断开长时间运行的连接，连接ID: {conn_id}")
            except Exception as e:
                logger.error(f"强制关闭连接失败: {str(e)}")
    
    def get_active_connections_info(self) -> Dict[str, Any]:
        """获取活跃连接信息"""
        current_time = time.time()
        connections_info = []
        
        with connection_lock:
            for conn_id, conn_info in active_connections.items():
                connections_info.append({
                    'connection_id': conn_id,
                    'created_at': conn_info['created_at'],
                    'last_activity': conn_info['last_activity'],
                    'active_duration': current_time - conn_info['created_at'],
                    'idle_duration': current_time - conn_info['last_activity']
                })
        
        return {
            'total_connections': len(connections_info),
            'connections': connections_info
        }
    
    def get_active_requests_info(self) -> Dict[str, Any]:
        """获取活跃请求信息"""
        current_time = time.time()
        requests_info = []
        
        with self.request_lock:
            for request_id, request_info in self.active_requests.items():
                requests_info.append({
                    'request_id': request_id,
                    'path': request_info['path'],
                    'method': request_info['method'],
                    'start_time': request_info['start_time'],
                    'duration': current_time - request_info['start_time']
                })
        
        return {
            'total_requests': len(requests_info),
            'requests': requests_info
        } 