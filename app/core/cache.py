from typing import Any, Optional
from app.core.logger import logger

class MemoryCache:
    """基于内存的简单缓存实现"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_cache'):
            self._cache = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            return self._cache.get(key)
        return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            self._cache[key] = value
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False

    def clear(self):
        """清除所有缓存"""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            return False

cache = MemoryCache()