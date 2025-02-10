from typing import Any, Optional, Dict, List, Set
from datetime import datetime, timedelta
from app.core.logger import logger
from app.core.monitor import track_cache_metrics
import json
import pickle
from pydantic import BaseModel

class MemoryCache:
    """基于内存的缓存实现"""
    _instance = None
    _cache: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def _serialize(self, value: Any) -> bytes:
        """序列化数据
        
        Args:
            value: 要序列化的数据
            
        Returns:
            bytes: 序列化后的字节串
        """
        try:
            if isinstance(value, BaseModel):
                return pickle.dumps(value.model_dump())
            elif isinstance(value, list):
                return pickle.dumps([
                    item.model_dump() if isinstance(item, BaseModel) else item
                    for item in value
                ])
            elif isinstance(value, dict):
                return pickle.dumps({
                    k: v.model_dump() if isinstance(v, BaseModel) else v
                    for k, v in value.items()
                })
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"序列化数据失败: {str(e)}")
            return pickle.dumps(str(value))

    def _deserialize(self, value: bytes) -> Any:
        """反序列化数据
        
        Args:
            value: 要反序列化的数据
            
        Returns:
            Any: 反序列化后的数据
        """
        try:
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"反序列化数据失败: {str(e)}")
            return None

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        try:
            if key not in self._cache:
                track_cache_metrics(hit=False)
                return None
                
            cache_data = self._cache[key]
            if cache_data["expire_time"] and datetime.now() > cache_data["expire_time"]:
                self.delete(key)
                track_cache_metrics(hit=False)
                return None
                
            track_cache_metrics(hit=True)
            return self._deserialize(cache_data["value"])
            
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
            
        Returns:
            bool: 是否设置成功
        """
        try:
            expire_time = datetime.now() + timedelta(seconds=expire) if expire else None
            self._cache[key] = {
                "value": self._serialize(value),
                "expire_time": expire_time
            }
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if key in self._cache:
                del self._cache[key]
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False

    def clear(self) -> bool:
        """清除所有缓存
        
        Returns:
            bool: 是否清除成功
        """
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            return False

    def clean_expired(self) -> None:
        """清理过期缓存"""
        try:
            now = datetime.now()
            expired_keys = [
                key for key, data in self._cache.items()
                if data["expire_time"] and now > data["expire_time"]
            ]
            for key in expired_keys:
                self.delete(key)
            if expired_keys:
                logger.info(f"已清理 {len(expired_keys)} 个过期缓存")
        except Exception as e:
            logger.error(f"清理过期缓存失败: {str(e)}")

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值
        
        Args:
            keys: 缓存键列表
            
        Returns:
            Dict[str, Any]: 缓存值字典
        """
        return {key: self.get(key) for key in keys}

    def set_many(self, mapping: Dict[str, Any], expire: int = 3600) -> bool:
        """批量设置缓存值
        
        Args:
            mapping: 键值对字典
            expire: 过期时间(秒)
            
        Returns:
            bool: 是否全部设置成功
        """
        try:
            for key, value in mapping.items():
                if not self.set(key, value, expire):
                    return False
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {str(e)}")
            return False

    def delete_many(self, keys: List[str]) -> bool:
        """批量删除缓存
        
        Args:
            keys: 缓存键列表
            
        Returns:
            bool: 是否全部删除成功
        """
        try:
            for key in keys:
                if not self.delete(key):
                    return False
            return True
        except Exception as e:
            logger.error(f"批量删除缓存失败: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            total = len(self._cache)
            expired = len([
                1 for data in self._cache.values()
                if data["expire_time"] and datetime.now() > data["expire_time"]
            ])
            return {
                "total_keys": total,
                "expired_keys": expired,
                "active_keys": total - expired
            }
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {str(e)}")
            return {}

# 全局缓存实例
cache = MemoryCache()