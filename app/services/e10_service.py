from typing import Dict, Any, Optional, List
from sqlmodel import Session
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.core.monitor import MetricsManager
from app.schemas.e10 import PurchaseOrder, PurchaseOrderQuery, PurchaseWip, PurchaseWipQuery, PurchaseWipSupplierResponse
from app.crud.e10 import CRUDE10

class E10Service:
    """E10服务类"""
    
    def __init__(self, db: Optional[Session] = None, cache: Optional[MemoryCache] = None):
        self._db = db
        self._cache = cache
        self.crud_e10 = CRUDE10()
        self.metrics = MetricsManager()

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

    def _clear_e10_cache(self) -> None:
        """清除E10相关缓存"""
        try:
            cache_keys = [
                "e10:purchase_orders",
                "e10:purchase_orders:params"
            ]
            for key in cache_keys:
                if not self.cache.delete(key):
                    logger.warning(f"删除缓存失败: {key}")
        except Exception as e:
            logger.error(f"清除E10缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_purchase_order_by_params(
        self,
        params: PurchaseOrderQuery
    ) -> Dict[str, Any]:
        """根据参数获取采购订单
        
        Args:
            params: 查询参数
            
        Returns:
            Dict[str, Any]: 包含采购订单列表和总数的字典
        """
        try:
            # 构建缓存键
            cache_key = f"e10:purchase_orders:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {
                        "list": [PurchaseOrder(**item) for item in cached_data["list"]],
                        "total": cached_data["total"]
                    }
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取数据
            db_result = self.crud_e10.get_purchase_order_by_params(self.db, params)
            
            # 构造返回结果
            result = {
                "list": db_result["list"],
                "total": db_result["total"]
            }
            
            # 缓存结果
            try:
                cache_data = {
                    "list": [item.model_dump() for item in result["list"]],
                    "total": result["total"]
                }
                success = self.cache.set(cache_key, cache_data, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
            
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取采购订单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_purchase_wip_by_params(
        self,
        params: PurchaseWipQuery
    ) -> Dict[str, Any]:
        """根据参数获取采购在途
        
        Args:
            params: 查询参数
            
        Returns:
            Dict[str, Any]: 包含采购在途列表和总数的字典
        """
        try:
            # 构建缓存键
            cache_key = f"e10:purchase_wips:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {
                        "list": [PurchaseWip(**item) for item in cached_data["list"]],
                        "total": cached_data["total"]
                    }
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取数据
            db_result = self.crud_e10.get_purchase_wip_by_params(self.db, params)
            
            # 构造返回结果
            result = { 
                "list": db_result["list"],
                "total": db_result["total"]
            }
            
            # 缓存结果
            try:
                cache_data = {
                    "list": [item.model_dump() for item in result["list"]],
                    "total": result["total"]
                }
                success = self.cache.set(cache_key, cache_data, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取采购在途失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_purchase_wip_supplier(self) -> List[PurchaseWipSupplierResponse]:
        """获取采购在制供应商"""
        try:
            # 从数据库获取供应商列表
            suppliers = self.crud_e10.get_purchase_wip_supplier(self.db)
            # 转换为Element Plus选择框需要的格式
            options = [{"value": supplier, "label": supplier} for supplier in suppliers]
            return options
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取采购在制供应商失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建服务实例
e10_service = E10Service(None, None)  # 在应用启动时注入实际的 db 和 cache
