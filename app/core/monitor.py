from prometheus_client import Counter, Histogram, start_http_server
import time
from functools import wraps
from typing import Callable
from app.core.logger import logger

# 定义监控指标
REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)

def start_metrics_server(port: int = 9090):
    """启动Prometheus指标服务器"""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {str(e)}")

def monitor_request(func: Callable):
    """请求监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            for arg in args:
                if hasattr(arg, 'method') and hasattr(arg, 'url'):
                    request = arg
                    break
        
        if not request:
            return await func(*args, **kwargs)
            
        method = request.method
        endpoint = request.url.path
        
        start_time = time.time()
        try:
            response = await func(*args, **kwargs)
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=getattr(response, 'status_code', 200)
            ).inc()
            return response
        finally:
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
    
    return wrapper 