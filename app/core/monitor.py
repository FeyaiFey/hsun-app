from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client.exposition import start_http_server
import time
from functools import wraps
from typing import Callable, Optional, Dict, Any
from app.core.logger import logger
from datetime import datetime

# API请求监控
REQUEST_COUNT = Counter(
    'app_request_count',
    'API请求总数',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'API请求延迟',
    ['method', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)

REQUEST_IN_PROGRESS = Gauge(
    'app_requests_in_progress',
    '正在处理的请求数',
    ['method', 'endpoint']
)

# 用户相关监控
ACTIVE_USERS = Gauge(
    'app_active_users',
    '活跃用户数'
)

USER_LOGIN_COUNT = Counter(
    'app_user_login_count',
    '用户登录次数',
    ['status', 'reason']
)

USER_REGISTER_COUNT = Counter(
    'app_user_register_count',
    '用户注册次数',
    ['status']
)

# 缓存监控
CACHE_OPERATIONS = Counter(
    'app_cache_operations_total',
    '缓存操作总数',
    ['operation', 'status']
)

CACHE_HIT_RATIO = Gauge(
    'app_cache_hit_ratio',
    '缓存命中率'
)

CACHE_SIZE = Gauge(
    'app_cache_size',
    '缓存大小',
    ['type']
)

# 数据库监控
DB_CONNECTIONS = Gauge(
    'app_db_connections',
    '数据库连接数',
    ['status']
)

DB_OPERATION_LATENCY = Histogram(
    'app_db_operation_latency_seconds',
    '数据库操作延迟',
    ['operation'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, float('inf'))
)

DB_OPERATIONS = Counter(
    'app_db_operations_total',
    '数据库操作总数',
    ['operation', 'status']
)

# 系统监控
SYSTEM_MEMORY = Gauge(
    'app_system_memory_bytes',
    '系统内存使用',
    ['type']
)

SYSTEM_CPU = Gauge(
    'app_system_cpu_usage',
    'CPU使用率',
    ['type']
)

def track_cache_metrics(hit: bool) -> None:
    """跟踪缓存指标
    
    Args:
        hit: 是否命中缓存
    """
    status = "hit" if hit else "miss"
    CACHE_OPERATIONS.labels(
        operation="get",
        status=status
    ).inc()

class MetricsManager:
    """指标管理类"""
    
    _instance = None
    _metrics_started = False
    _start_time = datetime.now()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def start_metrics_server(cls, port: int = 9090, addr: str = '') -> None:
        """启动指标服务器
        
        Args:
            port: 服务端口
            addr: 绑定地址
        """
        if not cls._metrics_started:
            try:
                start_http_server(port, addr)
                cls._metrics_started = True
                logger.info(f"指标服务器启动成功 - 端口: {port}")
            except Exception as e:
                logger.error(f"启动指标服务器失败: {str(e)}")
                raise

    @staticmethod
    def track_request_metrics(
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ) -> None:
        """跟踪请求指标
        
        Args:
            method: 请求方法
            endpoint: 请求路径
            status: 状态码
            duration: 请求耗时
        """
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    @staticmethod
    def track_auth_metrics(success: bool, reason: Optional[str] = None) -> None:
        """跟踪认证指标
        
        Args:
            success: 是否成功
            reason: 失败原因
        """
        status = "success" if success else "failure"
        USER_LOGIN_COUNT.labels(
            status=status,
            reason=reason or "unknown"
        ).inc()

    @staticmethod
    def track_cache_metrics(hit: bool) -> None:
        """跟踪缓存指标
        
        Args:
            hit: 是否命中
        """
        track_cache_metrics(hit)

    @staticmethod
    def track_db_metrics(
        operation: str,
        success: bool,
        duration: float
    ) -> None:
        """跟踪数据库指标
        
        Args:
            operation: 操作类型
            success: 是否成功
            duration: 操作耗时
        """
        status = "success" if success else "failure"
        DB_OPERATIONS.labels(
            operation=operation,
            status=status
        ).inc()
        
        DB_OPERATION_LATENCY.labels(
            operation=operation
        ).observe(duration)

    @staticmethod
    def update_system_metrics(
        memory_used: float,
        memory_total: float,
        cpu_usage: float
    ) -> None:
        """更新系统指标
        
        Args:
            memory_used: 已用内存
            memory_total: 总内存
            cpu_usage: CPU使用率
        """
        SYSTEM_MEMORY.labels(type="used").set(memory_used)
        SYSTEM_MEMORY.labels(type="total").set(memory_total)
        SYSTEM_CPU.labels(type="usage").set(cpu_usage)

    @staticmethod
    def update_cache_metrics(
        total_keys: int,
        hit_ratio: float,
        memory_usage: float
    ) -> None:
        """更新缓存指标
        
        Args:
            total_keys: 缓存键总数
            hit_ratio: 命中率
            memory_usage: 内存使用
        """
        CACHE_SIZE.labels(type="keys").set(total_keys)
        CACHE_HIT_RATIO.set(hit_ratio)
        CACHE_SIZE.labels(type="memory").set(memory_usage)

def monitor_request(func: Callable) -> Callable:
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
        
        REQUEST_IN_PROGRESS.labels(
            method=method,
            endpoint=endpoint
        ).inc()
        
        start_time = time.time()
        try:
            response = await func(*args, **kwargs)
            status = getattr(response, 'status_code', 200)
            duration = time.time() - start_time
            
            MetricsManager.track_request_metrics(
                method=method,
                endpoint=endpoint,
                status=status,
                duration=duration
            )
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            MetricsManager.track_request_metrics(
                method=method,
                endpoint=endpoint,
                status=500,
                duration=duration
            )
            raise e
        finally:
            REQUEST_IN_PROGRESS.labels(
                method=method,
                endpoint=endpoint
            ).dec()
    
    return wrapper

def monitor_db_operation(operation: str):
    """数据库操作监控装饰器
    
    Args:
        operation: 操作类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                MetricsManager.track_db_metrics(
                    operation=operation,
                    success=True,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                MetricsManager.track_db_metrics(
                    operation=operation,
                    success=False,
                    duration=duration
                )
                raise e
        return wrapper
    return decorator

# 创建全局指标管理实例
metrics_manager = MetricsManager() 