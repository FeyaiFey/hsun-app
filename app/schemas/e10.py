from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class PurchaseOrderQuery(BaseModel):
    """采购订单查询参数"""
    doc_no: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    supplier: Optional[str] = None
    purchase_date: Optional[date] = None


class PurchaseOrder(BaseModel):
    """采购订单"""
    SUPPLIER_FULL_NAME: str = Field(..., description="供应商全称")
    DOC_NO: str = Field(..., description="采购订单号")
    PURCHASE_DATE: date = Field(..., description="采购日期")
    REMARK: str = Field(..., description="备注")
    ITEM_CODE: str = Field(..., description="品号")
    ITEM_NAME: str = Field(..., description="品名")
    SHORTCUT: str = Field(..., description="简称")
    BUSINESS_QTY: int = Field(..., description="业务数量")
    SECOND_QTY: int = Field(..., description="第二数量")
    RECEIPTED_BUSINESS_QTY: int = Field(..., description="收货数量")
    PRICE: float = Field(..., description="单价")
    AMOUNT: float = Field(..., description="金额")
    RECEIPT_CLOSE: int = Field(..., description="收货关闭")

