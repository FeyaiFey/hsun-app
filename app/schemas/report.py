from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class GlobalReport(BaseModel):
    """综合报表"""
    ROW: Optional[int] = Field(None, description="行号")
    RN: Optional[int] = Field(None, description="主芯片序号")
    MAIN_CHIP_COUNT: Optional[int] = Field(None, description="主芯片数量")
    MAIN_CHIP: Optional[str] = Field(None, description="主芯片")
    WAFER_CODE: Optional[str] = Field(None, description="晶圆编码")
    CHIP_NAME: Optional[str] = Field(None, description="芯片名称")
    TOTAL_FINISHED_GOODS: Optional[int] = Field(None, description="产成品数量")
    TOP_FINISHED_GOODS: Optional[int] = Field(None, description="产成品正印数量")
    BACK_FINISHED_GOODS: Optional[int] = Field(None, description="产成品背印数量")
    TOTAL_SEMI_MANUFACTURED: Optional[int] = Field(None, description="半成品数量")
    TOP_SEMI_MANUFACTURED: Optional[int] = Field(None, description="半成品正印数量")
    BACK_SEMI_MANUFACTURED: Optional[int] = Field(None, description="半成品背印数量")
    PACKAGE_WIP_QTY: Optional[int] = Field(None, description="封装在制数量")
    PACKAGE_TOP_WIP_QTY: Optional[int] = Field(None, description="封装正印在制数量")
    PACKAGE_BACK_WIP_QTY: Optional[int] = Field(None, description="封装背印在制数量")
    SG_QTY: Optional[int] = Field(None, description="苏工院库存数量")
    SG_FINISHED_GOODS: Optional[int] = Field(None, description="苏工院产成品数量")
    SG_SEMI_MANUFACTURED: Optional[int] = Field(None, description="苏工院半成品数量")
    SECONDARY_OUTSOURCING_WIP_QTY: Optional[int] = Field(None, description="二次委外在制数量")
    PURCHASE_WIP_QTY: Optional[int] = Field(None, description="采购在制数量")
    TOTAL_RAW_MATERIALS: Optional[float] = Field(None, description="圆片总数")
    CP_WIP_QTY: Optional[int] = Field(None, description="中测在制数量")
    NO_TESTED_WAFER: Optional[float] = Field(None, description="未测试圆片数量")
    TESTED_WAFER: Optional[float] = Field(None, description="已测圆片数量")
    DEPUTY_CHIP: Optional[str] = Field(None, description="副芯片")
    OUTSOURCING_WIP_QTY: Optional[int] = Field(None, description="外购在途数量")
    TOTAL_B_RAW_MATERIALS: Optional[float] = Field(None, description="B芯圆片数量")

class SopAnalyzeResponse(BaseModel):
    """SOP分析"""
    ID: Optional[int] = Field(None, description="ID")
    ITEM_NAME: Optional[str] = Field(None, description="品名")
    ABTR: Optional[str] = Field(None, description="管装/编带")
    SAFE_STOCK: Optional[int] = Field(None, description="安全库存")
    LAST_MONTH_SALE: Optional[int] = Field(None, description="上月销量")
    CP_QTY: Optional[int] = Field(None, description="产成品数量")
    BC_QTY: Optional[int] = Field(None, description="半成品数量")
    WIP_QTY_WITHOUT_STOCK: Optional[int] = Field(None, description="在制数量")
    ASSY_STOCK: Optional[int] = Field(None, description="委外仓库存")
    TOTAL_STOCK: Optional[int] = Field(None, description="库存合计")
    INVENTORT_GAP: Optional[int] = Field(None, description="库存缺口")

class ChipInfoTraceQuery(BaseModel):
    """芯片信息追溯"""
    CHIP_LOT_CODE: Optional[str] = Field(None, description="芯片批次号")
    WAFER_LOT_CODE: Optional[str] = Field(None, description="晶圆批次号")
    SUPPLIER: Optional[str] = Field(None, description="供应商")
    CHIP_NAME: Optional[str] = Field(None, description="芯片名称")
    WAFER_NAME: Optional[str] = Field(None, description="晶圆名称")
    TESTING_PROGRAM_NAME: Optional[str] = Field(None, description="测试程序名称")
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=50, ge=1, le=100, description="每页数量")

class ChipInfoTrace(BaseModel):
    """芯片信息追溯"""
    ID: Optional[int] = Field(None, description="ID")
    DOC_NO: Optional[str] = Field(None, description="单据号")
    ITEM_CODE: Optional[str] = Field(None, description="品号")
    Z_PACKAGE_TYPE_NAME: Optional[str] = Field(None, description="封装类型")
    LOT_CODE: Optional[str] = Field(None, description="批次号")
    BUSINESS_QTY: Optional[int] = Field(None, description="业务数量")
    RECEIPTED_PRICE_QTY: Optional[int] = Field(None, description="收货数量")
    WIP_QTY: Optional[int] = Field(None, description="在制数量")
    Z_PROCESSING_PURPOSE_NAME: Optional[str] = Field(None, description="加工方式")
    Z_TESTING_PROGRAM_NAME: Optional[str] = Field(None, description="测试程序")
    Z_ASSEMBLY_CODE: Optional[str] = Field(None, description="打线图号")
    Z_WIRE_NAME: Optional[str] = Field(None, description="线材")
    REMARK: Optional[str] = Field(None, description="备注")
    PURCHASE_DATE: Optional[date] = Field(None, description="采购日期")
    FIRST_ARRIVAL_DATE: Optional[date] = Field(None, description="首次到料日期")
    SUPPLIER_FULL_NAME: Optional[str] = Field(None, description="供应商全称")
    MAIN_CHIP: Optional[str] = Field(None, description="主芯片")
    CHIP_CODE: Optional[str] = Field(None, description="芯片编码")
    LOT_CODE_NAME: Optional[str] = Field(None, description="晶圆批次号")
    WAFER_QTY: Optional[float] = Field(None, description="晶圆数量")
    S_QTY: Optional[float] = Field(None, description="晶圆片数")
    WAFER_ID: Optional[str] = Field(None, description="晶圆片号")
    PROGRESS_NAME: Optional[str] = Field(None, description="测试流程")
    TESTING_PROGRAM_NAME: Optional[str] = Field(None, description="测试程序")
    SUPPLIER: Optional[str] = Field(None, description="CP供应商")


class ChipInfoTraceResponse(BaseModel):
    """芯片信息追溯"""
    list: List[ChipInfoTrace] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
