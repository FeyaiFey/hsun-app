from typing import Any, Optional, List, Set, TypeVar, Type, Callable
from datetime import datetime, timedelta
from app.core.cache import MemoryCache
from app.core.logger import logger
from app.core.monitor import track_cache_metrics
from sqlmodel import Session
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message

T = TypeVar('T')

class CacheService:
    """缓存服务类"""
    
    def __init__(self, cache: MemoryCache):
        self.cache = cache

    async def get_or_set(
        self,
        key: str,
        func: Callable[[], Any],
        expire: int = 3600,
        force_update: bool = False
    ) -> Any:
        """获取或设置缓存
        
        Args:
            key: 缓存键
            func: 获取数据的函数
            expire: 过期时间(秒)
            force_update: 是否强制更新
            
        Returns:
            Any: 缓存的数据
            
        Raises:
            CustomException: 缓存操作失败
        """
        try:
            if not force_update:
                cached_data = self.cache.get(key)
                if cached_data is not None:
                    track_cache_metrics(hit=True)
                    logger.debug(f"缓存命中: {key}")
                    return cached_data
                    
            track_cache_metrics(hit=False)
            data = await func()
            if data is not None:
                if not self.cache.set(key, data, expire=expire):
                    raise CustomException(
                        message=get_error_message(ErrorCode.DB_ERROR)
                    )
                logger.debug(f"缓存更新: {key}")
            return data
        except Exception as e:
            logger.error(f"缓存操作失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_model_by_id(
        self,
        db: Session,
        model_type: Type[T],
        model_id: int,
        prefix: str,
        expire: int = 3600
    ) -> Optional[T]:
        """获取模型实例（使用缓存）
        
        Args:
            db: 数据库会话
            model_type: 模型类型
            model_id: 模型ID
            prefix: 缓存前缀
            expire: 过期时间(秒)
            
        Returns:
            Optional[T]: 模型实例
        """
        cache_key = f"{prefix}:{model_id}"
        
        async def get_model():
            return db.get(model_type, model_id)
            
        return await self.get_or_set(
            key=cache_key,
            func=get_model,
            expire=expire
        )

    async def get_list_by_ids(
        self,
        db: Session,
        model_type: Type[T],
        ids: List[int],
        prefix: str,
        expire: int = 3600
    ) -> List[T]:
        """获取模型列表（使用缓存）
        
        Args:
            db: 数据库会话
            model_type: 模型类型
            ids: ID列表
            prefix: 缓存前缀
            expire: 过期时间(秒)
            
        Returns:
            List[T]: 模型列表
        """
        result = []
        for id in ids:
            item = await self.get_model_by_id(
                db=db,
                model_type=model_type,
                model_id=id,
                prefix=prefix,
                expire=expire
            )
            if item:
                result.append(item)
        return result

    def clear_model_cache(self, model_id: int, prefixes: List[str]) -> None:
        """清除模型相关的缓存
        
        Args:
            model_id: 模型ID
            prefixes: 缓存前缀列表
        """
        try:
            for prefix in prefixes:
                cache_key = f"{prefix}:{model_id}"
                if not self.cache.delete(cache_key):
                    raise CustomException(
                        message=get_error_message(ErrorCode.DB_ERROR)
                    )
            logger.debug(f"清除模型 {model_id} 的缓存: {prefixes}")
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    def clear_list_cache(self, prefixes: List[str]) -> None:
        """清除列表缓存
        
        Args:
            prefixes: 缓存前缀列表
        """
        try:
            for prefix in prefixes:
                if not self.cache.delete(prefix):
                    raise CustomException(
                        message=get_error_message(ErrorCode.DB_ERROR)
                    )
            logger.debug(f"清除列表缓存: {prefixes}")
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    def clear_all(self) -> None:
        """清除所有缓存"""
        try:
            self.cache.clear()
            logger.info("清除所有缓存")
        except Exception as e:
            logger.error(f"清除所有缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建全局缓存服务实例
cache_service = CacheService(MemoryCache()) 