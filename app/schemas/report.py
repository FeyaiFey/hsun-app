from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class GlobalReport(BaseModel):
    """综合报表"""
    ROW: Optional[int] = Field(None, description="行号")
    RN: Optional[int] = Field(None, description="主芯片序号")
    MAIN_CHIP_COUNT: Optional[int] = Field(None, description="主芯片数量")
    MAIN_CHIP: Optional[str] = Field(None, description="主芯片")
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
