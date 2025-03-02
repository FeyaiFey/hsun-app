from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class PurchaseOrderQuery(BaseModel):
    """采购订单查询参数"""
    receipt_close: Optional[int] = Field(default=None, description="已结束？")
    doc_no: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    supplier: Optional[str] = None
    purchase_date_start: Optional[date] = None
    purchase_date_end: Optional[date] = None
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")

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
    is_finished: Optional[int] = Field(None, description="是否完成")
    is_stranded: Optional[int] = Field(None, description="是否滞留")
    days: Optional[int] = Field(None, description="某日内产出预计")
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")

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
    leadTime: Optional[int] = Field(..., description="提前期,交货期")

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

class AssyOrderQuery(BaseModel):
    """封装订单查询参数"""
    doc_no: Optional[str] = Field(None, description="封装订单号")
    item_code: Optional[List[str]] = Field(None, description="品号")
    item_name: Optional[List[str]] = Field(None, description="品名")
    supplier: Optional[List[str]] = Field(None, description="供应商")
    package_type: Optional[List[str]] = Field(None, description="封装类型")
    is_closed: Optional[int] = Field(None, description="是否关闭")
    order_date_start: Optional[date] = Field(None, description="工单日期开始")
    order_date_end: Optional[date] = Field(None, description="工单日期结束")
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=50, ge=1, le=100, description="每页数量")
    
class AssyOrder(BaseModel):
    """封装订单"""
    DOC_NO: Optional[str] = Field(None, description="封装订单号")
    ITEM_CODE: Optional[str] = Field(None, description="品号")
    Z_PROCESSING_PURPOSE_NAME: Optional[str] = Field(None, description="加工方式")
    Z_ASSEMBLY_CODE: Optional[str] = Field(None, description="打线图号")
    LOT_CODE: Optional[str] = Field(None, description="批号")
    BUSINESS_QTY: Optional[int] = Field(None, description="业务数量")
    RECEIPTED_PRICE_QTY: Optional[int] = Field(None, description="收货数量")
    WIP_QTY: Optional[int] = Field(None, description="在制数量")
    PRICE: Optional[float] = Field(None, description="单价")
    Z_PACKAGE_TYPE_NAME: Optional[str] = Field(None, description="封装类型")
    REMARK: Optional[str] = Field(None, description="备注")
    Z_LOADING_METHOD_NAME: Optional[str] = Field(None, description="装片方式")
    Z_WIRE_NAME: Optional[str] = Field(None, description="线材")
    Z_FEATURE_GROUP_NAME: Optional[str] = Field(None, description="品号群组")
    CLOSE: Optional[int] = Field(None, description="是否关闭")
    PURCHASE_DATE: Optional[date] = Field(None, description="采购日期")
    SUPPLIER_FULL_NAME: Optional[str] = Field(None, description="供应商全称")

class AssyOrderResponse(BaseModel):
    """封装订单响应"""
    list: List[AssyOrder] = Field(..., description="封装订单列表")
    total: int = Field(..., description="总条数")

class AssyWipQuery(BaseModel):
    """封装在制查询参数"""
    doc_no: Optional[str] = Field(None, description="封装订单号")
    item_code: Optional[str] = Field(None, description="品号")
    supplier: Optional[str] = Field(None, description="供应商")
    current_process: Optional[str] = Field(None, description="当前工序")
    is_finished: Optional[int] = Field(None, description="是否完成")
    is_stranded: Optional[int] = Field(None, description="是否滞留")
    days: Optional[int] = Field(None, description="某日内产出预计")
    pageIndex: Optional[int] = Field(default=1, ge=1, description="页码")
    pageSize: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")

class AssyWip(BaseModel):
    """封装在制"""
    DOC_NO: Optional[str] = Field(..., description="订单号")
    ITEM_CODE: Optional[str] = Field(..., description="品号")
    Z_PROCESSING_PURPOSE_NAME: Optional[str] = Field(..., description="加工方式")
    STRANDED: Optional[int] = Field(..., description="滞留天数")
    CURRENT_PROCESS: Optional[str] = Field(..., description="当前工序")
    EXPECTED_DELIVERY_DATE: Optional[date] = Field(..., description="预计交期")
    FINISHED_AT: Optional[date] = Field(..., description="完成日期")
    ONLINE_TOTAL: Optional[int] = Field(..., description="在线合计")
    WAREHOUSE_INVENTORY: Optional[int] = Field(..., description="仓库库存")
    HOLD_INFO: Optional[str] = Field(..., description="扣留信息")
    NEXT_DAY_EXPECTED: Optional[int] = Field(..., description="次日预计")
    THREE_DAY_EXPECTED: Optional[int] = Field(..., description="三日预计")
    SEVEN_DAY_EXPECTED: Optional[int] = Field(..., description="七日预计")
    POLISHING:Optional[int] = Field(..., description="研磨")
    CUTTING:Optional[int] = Field(..., description="切割")
    WAITING_FOR_INSTALLATION:Optional[int] = Field(..., description="待装片")
    INSTALLATION:Optional[int] = Field(..., description="装片")
    SILVER_GLUE_CURE:Optional[int] = Field(..., description="银胶固化")
    PLASMA_CLEANING_1:Optional[int] = Field(..., description="等离子清洗1")
    BONDING:Optional[int] = Field(..., description="键合")
    THREE_POINT_INSPECTION:Optional[int] = Field(..., description="三目检查")
    PLASMA_CLEANING_2:Optional[int] = Field(..., description="等离子清洗2")
    SEALING:Optional[int] = Field(..., description="塑封")
    POST_CURE:Optional[int] = Field(..., description="后固化")
    REFLOW_SOLDERING:Optional[int] = Field(..., description="回流焊")
    ELECTROPLATING:Optional[int] = Field(..., description="电镀")
    PRINTING:Optional[int] = Field(..., description="打印")
    POST_CUTTING:Optional[int] = Field(..., description="后切割")
    CUTTING_AND_SHAPING:Optional[int] = Field(..., description="切筋成型")
    MEASUREMENT_AND_PRINTING:Optional[int] = Field(..., description="测编打印")
    APPEARANCE_INSPECTION:Optional[int] = Field(..., description="外观检")
    PACKING:Optional[int] = Field(..., description="包装")
    WAITING_FOR_WAREHOUSE_INVENTORY:Optional[int] = Field(..., description="待入库")

class AssyWipResponse(BaseModel):
    """封装在制响应"""
    list: List[AssyWip] = Field(..., description="封装在制列表")
    total: int = Field(..., description="总条数")
