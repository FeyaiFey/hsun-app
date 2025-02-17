from typing import Dict, Any, Optional, List
from sqlmodel import Session
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.models.wip import FabWip
from app.schemas.wip import FabWipQuery
from app.crud.wip import CRUDFabWip

class WipService:
    """WIP服务类"""
    
    def __init__(self, db: Optional[Session] = None, cache: Optional[MemoryCache] = None):
        self._db = db
        self._cache = cache
        self.crud_fab_wip = CRUDFabWip(FabWip)

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if not self._db:
            raise CustomException("数据库会话未注入")
        return self._db
    
    @db.setter
    def db(self, value: Session):
        """设置数据库会话"""
        self._db = value
        
    @property
    def cache(self) -> MemoryCache:
        """获取缓存实例"""
        if not self._cache:
            raise CustomException("缓存实例未注入")
        return self._cache
    
    @cache.setter
    def cache(self, value: MemoryCache):
        """设置缓存实例"""
        self._cache = value

    def _clear_wip_cache(self) -> None:
        """清除WIP相关缓存"""
        try:
            cache_keys = [
                "wip:fab:list",
                "wip:assy:list"
            ]
            for key in cache_keys:
                self.cache.delete(key)
        except Exception as e:
            logger.error(f"清除WIP缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_fab_wip_list(
        self,
        query_params: Optional[FabWipQuery] = None
    ) -> List[FabWip]:
        """获取晶圆厂WIP列表
        
        Args:
            query_params: 查询参数
            
        Returns:
            List[FabWip]: WIP列表
        """
        try:
            # 如果没有查询参数，尝试从缓存获取
            if not query_params:
                cached_data = self.cache.get("wip:fab:list")
                if cached_data:
                    return cached_data

            # 从数据库查询
            result = self.crud_fab_wip.get_fab_wip(self.db, query_params=query_params)
            
            # 如果没有查询参数，缓存结果
            if not query_params:
                self.cache.set("wip:fab:list", result)
                
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取晶圆厂WIP列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建服务实例
wip_service = WipService(None, None)  # 在应用启动时注入实际的 db 和 cache 