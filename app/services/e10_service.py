from typing import Dict, Any, Optional, List
from sqlmodel import Session
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.core.monitor import MetricsManager
from app.schemas.purchase import (PurchaseOrder, PurchaseOrderQuery, PurchaseWip, PurchaseWipQuery, PurchaseWipSupplierResponse, PurchaseSupplierResponse)
from app.schemas.assy import (AssyOrder, AssyOrderQuery, AssyWip, AssyWipQuery, AssyOrderItemsQuery, AssyOrderItems,
                             AssyOrderPackageTypeQuery, AssyOrderPackageType, AssyOrderSupplierQuery, AssyOrderSupplier,
                             AssyBomQuery, AssyBom, AssyAnalyzeTotalResponse, AssyAnalyzeLoadingResponse, AssyYearTrendResponse,
                             AssySupplyAnalyzeResponse, ItemWaferInfoResponse, AssySubmitOrdersRequest, AssySubmitOrdersResponse,
                             CpTestOrdersQuery, CpTestOrdersResponse, AssyRequireOrdersQuery, AssyRequireOrdersCancel)
from app.schemas.stock import (StockQuery, Stock, WaferIdQtyDetailQuery, WaferIdQtyDetail, StockSummaryQuery, StockSummary)
from app.schemas.report import GlobalReport,SopAnalyzeResponse,ChipInfoTraceQuery,ChipInfoTraceResponse
from app.schemas.e10 import (FeatureGroupName, FeatureGroupNameQuery, ItemCode, ItemCodeQuery, ItemName, ItemNameQuery,
                             WarehouseName, WarehouseNameQuery, TestingProgram, TestingProgramQuery, BurningProgram, BurningProgramQuery,
                             LotCode, LotCodeQuery, SaleUnitResponse, SalesResponse, SaleUnit, Sales)
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_feature_group_name(self.db,params)
            # 转换为响应格式
            items = [FeatureGroupName(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_item_code(self.db,params)
            # 转换为响应格式
            items = [ItemCode(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_item_name(self.db,params)
            # 转换为响应格式
            items = [ItemName(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_lot_code(self.db,params)
            # 转换为响应格式
            items = [LotCode(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_warehouse_name(self.db,params)
            # 转换为响应格式
            items = [WarehouseName(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_testing_program(self.db,params)
            # 转换为响应格式
            items = [TestingProgram(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_burning_program(self.db,params)
            # 转换为响应格式
            items = [BurningProgram(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_purchase_order_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"],
                "total": db_result["total"]
            }
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_purchase_wip_by_params(self.db, params)
            # 构造返回结果
            result = { 
                "list": db_result["list"],
                "total": db_result["total"]
            }
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"],
                "total": db_result["total"]
            }
            return result
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取封装订单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def export_assy_order(self, params: AssyOrderQuery) -> bytes:
        """导出封装订单数据到Excel"""
        try:
            return self.crud_e10.export_assy_order_to_excel(self.db, params)
        except Exception as e:
            logger.error(f"导出封装订单失败: {str(e)}")
            raise CustomException("导出封装订单失败") 
    
    async def get_assy_bom_by_params(self,params:AssyBomQuery) -> Dict[str,Any]:
        """根据参数获取封装订单BOM"""
        try:
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_bom_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"]
            }
            return result
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取封装订单BOM失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
        
    async def get_assy_wip_by_params(
        self,
        params: AssyWipQuery
    ) -> Dict[str, Any]:
        """根据参数获取封装在制"""
        try:
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_wip_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"],
                "total": db_result["total"]
            }
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_items(self.db, params)
            # 转换为响应格式
            items = [AssyOrderItems(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_package_type(self.db, params)
            # 转换为响应格式
            package_types = [AssyOrderPackageType(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_assy_order_supplier(self.db, params)
            # 转换为响应格式
            suppliers = [AssyOrderSupplier(**item) for item in db_result["list"]]
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
            # 从数据库获取数据
            db_result = self.crud_e10.get_stock_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"],
                "total": db_result["total"]
            }
            return result
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
             # 从数据库获取数据
            db_result = self.crud_e10.get_wafer_id_qty_detail_by_params(self.db, params)
            # 构造返回结果
            result = {
                "list": db_result["list"]
            }
            return result
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取晶圆ID数量明细失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_stock_summary_by_params(self,params:StockSummaryQuery) -> Dict[str,Any]:
        """获取库存汇总"""
        try:
            # 从数据库获取数据
            db_result = self.crud_e10.get_stock_summary_by_params(self.db, params)
            return db_result
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取库存汇总失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def export_stock_by_params(self, params: StockQuery) -> bytes:
        """导出库存数据到Excel"""
        try:
            return self.crud_e10.export_stock_by_params(self.db, params)
        except Exception as e:
            logger.error(f"导出库存失败: {str(e)}")
            raise CustomException("导出库存失败")
        
    async def get_global_report(self) -> List[GlobalReport]:
        """获取综合报表"""
        try:        
            # 获取所有数据
            report = self.crud_e10.get_global_report(self.db)
            
            return report
        
        except Exception as e:
            logger.error(f"获取综合报表失败: {str(e)}")
            raise CustomException("获取综合报表失败")
    
    async def export_global_report(self) -> bytes:
        """导出综合报表"""
        try:
            return self.crud_e10.export_global_report(self.db)
        except Exception as e:
            logger.error(f"导出综合报表失败: {str(e)}")
            raise CustomException("导出综合报表失败")
    
    async def get_assy_analyze_total(self) -> List[AssyAnalyzeTotalResponse]:
        """获取封装分析总表"""
        try:
            return self.crud_e10.get_assy_analyze_total(self.db)
        except Exception as e:
            logger.error(f"获取封装分析总表失败: {str(e)}")
            raise CustomException("获取封装分析总表失败")
        
    async def get_assy_analyze_loading(self,range_type:str) -> List[AssyAnalyzeLoadingResponse]:
        """获取封装分析装载"""
        try:
            db_result = self.crud_e10.get_assy_analyze_loading(self.db,range_type)
            return db_result
        except Exception as e:
            logger.error(f"获取封装分析装载失败: {str(e)}")
            raise CustomException("获取封装分析装载失败")
    
    async def get_assy_year_trend(self) -> List[AssyYearTrendResponse]:
        """获取封装年趋势"""
        try:
            return self.crud_e10.get_assy_year_trend(self.db)
        except Exception as e:
            logger.error(f"获取封装年趋势失败: {str(e)}")
            raise CustomException("获取封装年趋势失败")
        
    async def get_assy_supply_analyze(self) -> List[AssySupplyAnalyzeResponse]:
        """获取封装供应分析"""
        try:
            return self.crud_e10.get_assy_supply_analyze(self.db)
        except Exception as e:
            logger.error(f"获取封装供应分析失败: {str(e)}")
            raise CustomException("获取封装供应分析失败")
        
    async def get_sop_analyze(self) -> List[SopAnalyzeResponse]:
        """获取SOP分析"""
        try:
            return self.crud_e10.get_sop_analyze(self.db)
        except Exception as e:
            logger.error(f"获取SOP分析失败: {str(e)}")
            raise CustomException("获取SOP分析失败")
        
    async def export_sop_report(self) -> bytes:
        """导出SOP报表"""
        try:
            return self.crud_e10.export_sop_report(self.db)
        except Exception as e:
            logger.error(f"导出SOP报表失败: {str(e)}")
            raise CustomException("导出SOP报表失败")
    
    async def get_item_wafer_info(self,item_name:str) -> List[ItemWaferInfoResponse]:
        """获取晶圆信息"""
        try:
            return self.crud_e10.get_item_wafer_info(self.db,item_name)
        except Exception as e:
            logger.error(f"获取晶圆信息失败: {str(e)}")
            raise CustomException("获取晶圆信息失败")
    
    async def get_sales(self,admin_unit_name:str) -> Dict[str,Any]:
        """获取销售员名称"""
        try:
            db_result = self.crud_e10.get_sales(self.db,admin_unit_name)
            sales = [Sales(**item) for item in db_result["list"]]
            return {"list": sales}
        except Exception as e:
            logger.error(f"获取销售员名称失败: {str(e)}")
            raise CustomException("获取销售员名称失败")
    
    async def get_sale_unit(self) -> Dict[str,Any]:
        """获取销售单位"""
        try:
            db_result = self.crud_e10.get_sale_unit(self.db)
            sale_unit = [SaleUnit(**item) for item in db_result["list"]]
            return {"list": sale_unit}
        except Exception as e:
            logger.error(f"获取销售单位失败: {str(e)}")
            raise CustomException("获取销售单位失败")
    
    async def batch_submit_assy_orders(self,data:AssySubmitOrdersRequest,current_user:str) -> AssySubmitOrdersResponse:
        """批量提交封装单"""
        try:
            return self.crud_e10.batch_submit_assy_orders(self.db,data,current_user)
        except Exception as e:
            logger.error(f"批量提交封装单失败: {str(e)}")
            raise CustomException("批量提交封装单失败")
            
    async def export_assy_orders(self) -> bytes:
        """导出封装单"""
        try:
            return self.crud_e10.export_assy_orders(self.db)
        except Exception as e:
            logger.error(f"导出封装单失败: {str(e)}")
            raise CustomException("导出封装单失败")
        
    async def get_cptest_orders_by_params(self,params:CpTestOrdersQuery) -> Dict[str,Any]:
        """获取CP测试单"""
        try:
            return self.crud_e10.get_cptest_orders_by_params(self.db,params)
        except Exception as e:
            logger.error(f"获取CP测试单失败: {str(e)}")
            raise CustomException("获取CP测试单失败")
    
    async def export_cptest_orders_excel(self,params:CpTestOrdersQuery) -> bytes:
        """导出CP测试单Excel"""
        try:
            return self.crud_e10.export_cptest_orders_excel(self.db,params)
        except Exception as e:
            logger.error(f"导出CP测试单Excel失败: {str(e)}")
            raise CustomException("导出CP测试单Excel失败")

    async def get_chipInfo_trace_by_params(self,params:ChipInfoTraceQuery) -> Dict[str,Any]:
        """获取芯片信息追溯"""
        try:
            return self.crud_e10.get_chipInfo_trace_by_params(self.db,params)
        except Exception as e:
            logger.error(f"获取芯片信息追溯失败: {str(e)}")
            raise CustomException("获取芯片信息追溯失败")
    
    async def get_assy_require_orders(self,params:AssyRequireOrdersQuery) -> Dict[str,Any]:
        """获取封装需求单"""
        try:
            return self.crud_e10.get_assy_require_orders(self.db,params)
        except Exception as e:
            logger.error(f"获取封装需求单失败: {str(e)}")
            raise CustomException("获取封装需求单失败")
    
    async def cancel_assy_require_orders(self,data:AssyRequireOrdersCancel) -> str:
        try:
            return self.crud_e10.cancel_assy_require_orders(self.db,data)
        except Exception as e:
            logger.error(f"取消封装需求单失败: {str(e)}")
            raise CustomException("取消封装需求单失败")
    
    async def delete_assy_require_orders(self,data:AssyRequireOrdersCancel) -> str:
        try:
            return self.crud_e10.delete_assy_require_orders(self.db,data)
        except Exception as e:
            logger.error(f"删除封装需求单失败: {str(e)}")
            raise CustomException("删除封装需求单失败")

    async def change_assy_order_status(self) -> str:
        try:
            return self.crud_e10.change_assy_order_status(self.db)
        except Exception as e:
            logger.error(f"提交封装需求单失败: {str(e)}")
            raise CustomException("提交封装需求单失败")
    
    async def export_chip_trace_by_params(self,params:ChipInfoTraceQuery) -> bytes:
        """导出芯片追溯Excel"""
        try:
            return self.crud_e10.export_chip_trace(self.db,params)
        except Exception as e:
            logger.error(f"导出芯片追溯Excel失败: {str(e)}")
            raise CustomException("导出芯片追溯Excel失败")

e10_service = E10Service(None, None)  # 在应用启动时注入实际的 db 和 cache
