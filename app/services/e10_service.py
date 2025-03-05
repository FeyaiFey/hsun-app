from typing import Dict, Any, Optional, List
from sqlmodel import Session
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.core.monitor import MetricsManager
from app.schemas.purchase import (PurchaseOrder, PurchaseOrderQuery, PurchaseWip, PurchaseWipQuery, PurchaseWipSupplierResponse, PurchaseSupplierResponse)
from app.schemas.assy import (AssyOrder, AssyOrderQuery, AssyWip, AssyWipQuery, AssyOrderItemsQuery, AssyOrderItems,
                             AssyOrderPackageTypeQuery, AssyOrderPackageType, AssyOrderSupplierQuery, AssyOrderSupplier
                             )
from app.schemas.stock import (StockQuery, Stock, WaferIdQtyDetailQuery, WaferIdQtyDetail)
from app.schemas.e10 import (FeatureGroupName, FeatureGroupNameQuery, ItemCode, ItemCodeQuery, ItemName, ItemNameQuery,
                             WarehouseName, WarehouseNameQuery, TestingProgram, TestingProgramQuery, BurningProgram, BurningProgramQuery,
                             LotCode, LotCodeQuery
                             )
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
    
    async def get_feature_group_name(self,params:FeatureGroupNameQuery) -> Dict[str,List[FeatureGroupName]]:
        """获取品号群组"""
        try:
            # 构建缓存键
            cache_key = f"e10:feature_group_names:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [FeatureGroupName(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_feature_group_name(self.db,params)
            
            # 转换为响应格式
            items = [FeatureGroupName(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取品号群组失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_item_code(self,params:ItemCodeQuery) -> Dict[str,List[ItemCode]]:
        """获取品号"""
        try:
            # 构建缓存键
            cache_key = f"e10:item_codes:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [ItemCode(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_item_code(self.db,params)
            
            # 转换为响应格式
            items = [ItemCode(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取品号失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_item_name(self,params:ItemNameQuery) -> Dict[str,List[ItemName]]:
        """获取品名"""
        try:
            # 构建缓存键
            cache_key = f"e10:item_names:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [ItemName(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_item_name(self.db,params)
            
            # 转换为响应格式
            items = [ItemName(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取品名失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_lot_code(self,params:LotCodeQuery) -> Dict[str,List[LotCode]]:
        """获取批号"""
        try:
            # 构建缓存键
            cache_key = f"e10:lot_codes:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [LotCode(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_lot_code(self.db,params)
            
            # 转换为响应格式
            items = [LotCode(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取批号失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_warehouse_name(self,params:WarehouseNameQuery) -> Dict[str,List[WarehouseName]]:
        """获取仓库"""
        try:
            # 构建缓存键
            cache_key = f"e10:warehouse_names:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [WarehouseName(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_warehouse_name(self.db,params)
            
            # 转换为响应格式
            items = [WarehouseName(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取仓库失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_testing_program(self,params:TestingProgramQuery) -> Dict[str,List[TestingProgram]]:
        """获取测试程序"""
        try:
            # 构建缓存键
            cache_key = f"e10:testing_programs:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [TestingProgram(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_testing_program(self.db,params)
            
            # 转换为响应格式
            items = [TestingProgram(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取测试程序失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_burning_program(self,params:BurningProgramQuery) -> Dict[str,List[BurningProgram]]:
        """获取烧录程序"""
        try:
            # 构建缓存键
            cache_key = f"e10:burning_programs:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {"list": [BurningProgram(**item) for item in cached_data["list"]]}
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_burning_program(self.db,params)
            
            # 转换为响应格式
            items = [BurningProgram(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")

            return {"list": items}
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取烧录程序失败: {str(e)}")
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

    async def get_purchase_supplier(self) -> List[PurchaseSupplierResponse]:
        """获取采购供应商"""
        try:
            # 从数据库获取供应商列表
            suppliers = self.crud_e10.get_purchase_supplier(self.db)
            # 转换为Element Plus选择框需要的格式
            options = [{"value": supplier, "label": supplier} for supplier in suppliers]
            return options
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取采购供应商失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_assy_order_by_params(
        self,
        params: AssyOrderQuery
    ) -> Dict[str, Any]:
        """根据参数获取封装订单"""
        try:
            # 构建缓存键 - 处理列表类型参数
            params_dict = params.model_dump()
            cache_params = {}
            
            for key, value in params_dict.items():
                if isinstance(value, list):
                    # 将列表转换为排序后的元组，因为元组是可哈希的
                    cache_params[key] = tuple(sorted(value)) if value else None
                else:
                    cache_params[key] = value
                    
            # 使用可哈希的键值对生成缓存键
            cache_key = f"e10:assy_orders:params:{hash(frozenset(cache_params.items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {
                        "list": [AssyOrder(**item) for item in cached_data["list"]],
                        "total": cached_data["total"]
                    }
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_by_params(self.db, params)
            
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
            logger.error(f"获取封装订单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def get_assy_wip_by_params(
        self,
        params: AssyWipQuery
    ) -> Dict[str, Any]:
        """根据参数获取封装在制"""
        try:
            # 构建缓存键
            cache_key = f"e10:assy_wips:params:{hash(frozenset(params.model_dump().items()))}"
            
            # 尝试从缓存获取
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    self.metrics.track_cache_metrics(hit=True)
                    logger.debug(f"命中缓存: {cache_key}")
                    return {
                        "list": [AssyWip(**item) for item in cached_data["list"]],
                        "total": cached_data["total"]
                    }
            except Exception as cache_error:
                logger.warning(f"缓存获取失败: {str(cache_error)}")

            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_wip_by_params(self.db, params)
            
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
            logger.error(f"获取封装在制失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_assy_order_items(self,params:AssyOrderItemsQuery) -> Dict[str, List[AssyOrderItems]]:
        """获取封装在制品号"""
        try:
            # 构建缓存键
            cache_key = f"e10:assy_order_items:params:{hash(frozenset(params.model_dump().items()))}"

            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return {"list": [AssyOrderItems(**item) for item in cached_data["list"]]}
            
            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_items(self.db, params)
            
            # 转换为响应格式
            items = [AssyOrderItems(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in items]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                
            return {"list": items}
        
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取封装在制品号失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_assy_order_package_type(self,params:AssyOrderPackageTypeQuery) -> Dict[str,Any]:
        """获取封装订单类型"""
        try:
            # 构建缓存键
            cache_key = f"e10:assy_order_package_type:params:{hash(frozenset(params.model_dump().items()))}"

            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return {"list": [AssyOrderPackageType(**item) for item in cached_data["list"]]}
            
            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_package_type(self.db, params)
            
            # 转换为响应格式
            package_types = [AssyOrderPackageType(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in package_types]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                
            return {"list": package_types}
        
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取封装订单类型失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def get_assy_order_supplier(self,params:AssyOrderSupplierQuery) -> Dict[str,Any]:
        """获取封装订单供应商"""
        try:
            # 构建缓存键
            cache_key = f"e10:assy_order_supplier:params:{hash(frozenset(params.model_dump().items()))}"

            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return {"list": [AssyOrderSupplier(**item) for item in cached_data["list"]]}
            
            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_supplier(self.db, params)
            
            # 转换为响应格式
            suppliers = [AssyOrderSupplier(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in suppliers]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                
            return {"list": suppliers}
        
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取封装订单供应商失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def get_stock_by_params(self,params:StockQuery) -> Dict[str,Any]:
        """获取库存"""
        try:
            # 构建缓存键
            cache_key = f"e10:stock:params:{hash(frozenset(params.model_dump().items()))}"

            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return {"list": [Stock(**item) for item in cached_data["list"]]}
            
            self.metrics.track_cache_metrics(hit=False)

            # 从数据库获取数据
            db_result = self.crud_e10.get_stock_by_params(self.db, params)
            
            # 转换为响应格式
            stocks = [Stock(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in stocks]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                
            return {"list": stocks}
        
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取库存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def get_wafer_id_qty_detail_by_params(self,params:WaferIdQtyDetailQuery) -> Dict[str,Any]:
        """获取晶圆ID数量明细"""
        try:
            # 构建缓存键
            cache_key = f"e10:wafer_id_qty_detail:params:{hash(frozenset(params.model_dump().items()))}"

            # 尝试从缓存获取
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.metrics.track_cache_metrics(hit=True)
                logger.debug(f"命中缓存: {cache_key}")
                return {"list": [WaferIdQtyDetail(**item) for item in cached_data["list"]]}
            
            self.metrics.track_cache_metrics(hit=False)
            
            # 从数据库获取数据
            db_result = self.crud_e10.get_wafer_id_qty_detail_by_params(self.db, params)
            
            # 转换为响应格式
            wafer_id_qty_details = [WaferIdQtyDetail(**item) for item in db_result["list"]]
            
            # 缓存结果
            try:
                success = self.cache.set(cache_key, {"list": [item.model_dump() for item in wafer_id_qty_details]}, expire=3600)  # 缓存1小时
                if success:
                    logger.debug(f"成功设置缓存: {cache_key}")
                else:
                    logger.warning(f"设置缓存失败: {cache_key}")
            except Exception as cache_error:
                logger.warning(f"缓存设置失败: {str(cache_error)}")
                    
            return {"list": wafer_id_qty_details}
        
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取晶圆ID数量明细失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
# 创建服务实例
e10_service = E10Service(None, None)  # 在应用启动时注入实际的 db 和 cache
