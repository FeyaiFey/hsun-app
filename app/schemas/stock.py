from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class StockQuery(BaseModel):
    """库存查询参数"""
    feature_group_name: Optional[List[str]] = Field(None, description="品号群组")
    item_code: Optional[List[str]] = Field(None, description="品号")
    item_name: Optional[List[str]] = Field(None, description="品名")
    lot_code: Optional[List[str]] = Field(None, description="批号")
    warehouse_name: Optional[List[str]] = Field(None, description="仓库")
    testing_program: Optional[List[str]] = Field(None, description="测试程序")
    burning_program: Optional[List[str]] = Field(None, description="烧录程序")

class Stock(BaseModel):
    """库存"""
    FEATURE_GROUP_NAME: Optional[str] = Field(None, description="品号群组")
    ITEM_CODE: Optional[str] = Field(None, description="品号")
    ITEM_NAME: Optional[str] = Field(None, description="品名")
    LOT_CODE: Optional[str] = Field(None, description="批号")
    WAREHOUSE_NAME: Optional[str] = Field(None, description="仓库")
    INVENTORY_QTY: Optional[int] = Field(None, description="库存数量")
    SECOND_QTY: Optional[float] = Field(None, description="第二数量")
    Z_BIN_LEVEL_NAME: Optional[str] = Field(None, description="BIN等级")
    Z_TESTING_PROGRAM_NAME: Optional[str] = Field(None, description="测试程序")
    Z_BURNING_PROGRAM_NAME: Optional[str] = Field(None, description="烧录程序")

class StockResponse(BaseModel):
    """库存响应"""
    list: List[Stock] = Field(..., description="库存列表")
    
class WaferIdQtyDetailQuery(BaseModel):
    """晶圆ID数量明细查询参数"""
    item_code: Optional[str] = Field(None, description="品号")
    lot_code: Optional[str] = Field(None, description="批号")

class WaferIdQtyDetail(BaseModel):
    """晶圆ID数量明细"""
    ITEM_CODE: Optional[str] = Field(None, description="品号")
    LOT_CODE: Optional[str] = Field(None, description="批号")
    WF_ID: Optional[str] = Field(None, description="晶圆ID")
    INVENTORY_QTY: Optional[int] = Field(None, description="库存数量")
    SECOND_QTY: Optional[float] = Field(None, description="第二数量")
    Z_BIN_LEVEL_NAME: Optional[str] = Field(None, description="BIN等级")
    Z_TESTING_PROGRAM_NAME: Optional[str] = Field(None, description="测试程序")
    WAREHOUSE_NAME: Optional[str] = Field(None, description="仓库")

class WaferIdQtyDetailResponse(BaseModel):
    """晶圆ID数量明细响应"""
    list: List[WaferIdQtyDetail] = Field(..., description="晶圆ID数量明细列表")

class StockSummaryQuery(BaseModel):
    """库存汇总查询参数"""
    item_name: Optional[str] = Field(None, description="品名")
    warehouse_name: Optional[str] = Field(None, description="仓库")
    feature_group_name: Optional[str] = Field(None, description="品号群组")

class StockSummary(BaseModel):
    FEATURE_GROUP_NAME: str = Field(..., description="品号群组")
    ITEM_NAME: str = Field(..., description="品名")
    WAREHOUSE_NAME: str = Field(..., description="仓库")
    INVENTORY_QTY: float = Field(..., description="库存数量")
    AVERAGE_STOCK_AGE: int = Field(..., description="平均库存天数")

class StockSummaryResponse(BaseModel):
    list: List[StockSummary] = Field(..., description="库存汇总列表")
