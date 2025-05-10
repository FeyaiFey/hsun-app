from datetime import datetime, date
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field
from pydantic import validator

class PurchaseOrderQuery(BaseModel):
    """采购订单查询参数"""
    receipt_close: Optional[Union[int, str]] = Field(default=None, description="已结束？")
    doc_no: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    supplier: Optional[str] = None
    purchase_date_start: Optional[date] = None
    purchase_date_end: Optional[date] = None
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")

    @validator('receipt_close')
    def validate_int_or_empty(cls, v):
        if v is None or v == '':
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

class PurchaseOrder(BaseModel):
    """采购订单"""
    SUPPLIER_FULL_NAME: Optional[str] = Field(None, description="供应商全称")
    DOC_NO: Optional[str] = Field(None, description="采购订单号")
    PURCHASE_DATE: Optional[date] = Field(None, description="采购日期")
    REMARK: Optional[str] = Field(None, description="备注")
    ITEM_CODE: Optional[str] = Field(None, description="品号")
    ITEM_NAME: Optional[str] = Field(None, description="品名")
    SHORTCUT: Optional[str] = Field(None, description="简称")
    BUSINESS_QTY: Optional[int] = Field(None, description="业务数量")
    SECOND_QTY: Optional[int] = Field(None, description="第二数量")
    RECEIPTED_BUSINESS_QTY: Optional[int] = Field(None, description="收货数量")
    WIP_QTY: Optional[int] = Field(None, description="在制数量")
    PRICE: Optional[float] = Field(None, description="单价")
    AMOUNT: Optional[float] = Field(None, description="金额")
    RECEIPT_CLOSE: Optional[int] = Field(None, description="收货关闭")

class PurchaseOrderResponse(BaseModel):
    """采购订单响应"""
    list: List[PurchaseOrder] = Field(..., description="采购订单列表")
    total: int = Field(..., description="总条数")

class PurchaseWipQuery(BaseModel):
    """采购在制查询参数"""
    purchase_order: Optional[str] = Field(None, description="采购订单号")
    item_name: Optional[str] = Field(None, description="品名")
    supplier: Optional[str] = Field(None, description="供应商")
    status: Optional[str] = Field(None, description="状态")
    is_finished: Optional[Union[int, str]] = Field(None, description="是否完成")
    is_stranded: Optional[Union[int, str]] = Field(None, description="是否滞留")
    days: Optional[int] = Field(None, description="某日内产出预计")
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")

    @validator('is_finished', 'is_stranded')
    def validate_int_or_empty(cls, v):
        if v is None or v == '':
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

class PurchaseWip(BaseModel):
    """采购在制"""
    purchaseOrder: Optional[str] = Field(..., description="采购订单")
    itemName: Optional[str] = Field(..., description="品名")
    lot: Optional[str] = Field(..., description="批号")
    qty: Optional[int] = Field(..., description="在制数量")
    status: Optional[str] = Field(..., description="状态")
    stage: Optional[str] = Field(..., description="阶段")
    layerCount: Optional[int] = Field(..., description="层数")
    remainLayerCount: Optional[int] = Field(..., description="剩余层数")
    currentPosition: Optional[int] = Field(..., description="当前位置")
    forecastDate: Optional[date] = Field(..., description="预计完成日期")
    supplier: Optional[str] = Field(..., description="供应商")
    finished_at: Optional[date] = Field(..., description="完成日期")
    stranded: Optional[int] = Field(..., description="滞留天数")

class PurchaseWipResponse(BaseModel):
    """采购在制响应"""
    list: List[PurchaseWip] = Field(..., description="采购在制列表")
    total: int = Field(..., description="总条数")

class PurchaseWipSupplierResponse(BaseModel):
    """采购在制供应商响应"""
    label: List[str] = Field(..., description="供应商")
    value: List[str] = Field(..., description="供应商值")

class PurchaseSupplierResponse(BaseModel):
    """采购供应商响应"""
    label: List[str] = Field(..., description="供应商")
    value: List[str] = Field(..., description="供应商值")