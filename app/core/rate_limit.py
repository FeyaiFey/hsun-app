from collections import defaultdict
import time
from typing import Dict, List
from app.core.logger import logger

class SimpleRateLimiter:
    """简单的内存限流器实现"""
    
    def __init__(self, limit: int = 5, window: int = 60):
        """初始化限流器
        
        Args:
            limit: 时间窗口内允许的最大请求数
            window: 时间窗口大小(秒)
        """
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.limit = limit
        self.window = window

    def is_limited(self, key: str) -> bool:
        """检查是否被限流
        
        Args:
            key: 限流键(如用户ID、IP等)
            
        Returns:
            bool: 是否被限流
        """
        now = time.time()
        
        # 清理过期请求
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window
        ]
        
        # 检查是否超过限制
        return len(self.requests[key]) >= self.limit

    def increment(self, key: str) -> None:
        """增加请求计数
        
        Args:
            key: 限流键
        """
        now = time.time()
        self.requests[key].append(now)
        
        # 记录日志
        count = len(self.requests[key])
        if count >= self.limit:
            logger.warning(f"请求被限流: {key}, 当前请求数: {count}")

    def reset(self, key: str) -> None:
        """重置请求计数
        
        Args:
            key: 限流键
        """
        if key in self.requests:
            del self.requests[key]
            logger.info(f"重置限流计数: {key}")

    def clean_expired(self) -> None:
        """清理所有过期的请求记录"""
        now = time.time()
        cleaned = 0
        
        for key in list(self.requests.keys()):
            original_len = len(self.requests[key])
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window
            ]
            cleaned += original_len - len(self.requests[key])
            
            # 如果没有请求记录了，删除这个键
            if not self.requests[key]:
                del self.requests[key]
        
        if cleaned > 0:
            logger.info(f"清理了 {cleaned} 条过期的限流记录") 