from collections import defaultdict
import time

class SimpleRateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        # 清理过期请求
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        if len(self.requests[key]) >= limit:
            return False
            
        self.requests[key].append(now)
        return True 