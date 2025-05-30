from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator, computed_field
from app.schemas.response import IResponse

class InvoiceCreate(BaseModel):
    """创建发票的数据结构"""
    file_name: str = Field(..., description="文件名")
    invoice_type: Optional[str] = Field(None, description="发票类型")
    invoice_number: str = Field(..., description="发票号码")
    issue_date: Optional[date] = Field(None, description="开票日期")
    issuer: Optional[str] = Field(None, description="开票人")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_number: Optional[str] = Field(None, description="购买方税号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_number: Optional[str] = Field(None, description="销售方税号")
    total_amount: Optional[Decimal] = Field(None, description="总金额")
    total_tax: Optional[Decimal] = Field(None, description="总税额")
    total_amount_in_words: Optional[str] = Field(None, description="总金额大写")
    total_amount_in_numbers: Optional[Decimal] = Field(None, description="总金额数字")
    status: int = Field(1, description="发票状态：0-作废，1-正常", ge=0, le=1)

class InvoiceUpdate(BaseModel):
    """更新发票的数据结构"""
    file_name: Optional[str] = Field(None, description="文件名")
    invoice_type: Optional[str] = Field(None, description="发票类型")
    invoice_number: Optional[str] = Field(None, description="发票号码")
    issue_date: Optional[date] = Field(None, description="开票日期")
    issuer: Optional[str] = Field(None, description="开票人")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_number: Optional[str] = Field(None, description="购买方税号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_number: Optional[str] = Field(None, description="销售方税号")
    total_amount: Optional[Decimal] = Field(None, description="总金额")
    total_tax: Optional[Decimal] = Field(None, description="总税额")
    total_amount_in_words: Optional[str] = Field(None, description="总金额大写")
    total_amount_in_numbers: Optional[Decimal] = Field(None, description="总金额数字")
    status: Optional[int] = Field(None, description="发票状态：0-作废，1-正常", ge=0, le=1)

class InvoiceResponse(BaseModel):
    """发票响应数据结构"""
    invoice_id: int = Field(..., description="发票ID")
    file_name: str = Field(..., description="文件名")
    invoice_type: Optional[str] = Field(None, description="发票类型")
    invoice_number: str = Field(..., description="发票号码")
    issue_date: Optional[date] = Field(None, description="开票日期")
    issuer: Optional[str] = Field(None, description="开票人")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_number: Optional[str] = Field(None, description="购买方税号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_number: Optional[str] = Field(None, description="销售方税号")
    total_amount: Optional[Decimal] = Field(None, description="总金额")
    total_tax: Optional[Decimal] = Field(None, description="总税额")
    total_amount_in_words: Optional[str] = Field(None, description="总金额大写")
    total_amount_in_numbers: Optional[Decimal] = Field(None, description="总金额数字")
    status: int = Field(..., description="发票状态：0-作废，1-正常")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @computed_field
    @property
    def status_text(self) -> str:
        """获取状态文本描述"""
        return "正常" if self.status == 1 else "作废"

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,
            date: lambda v: v.strftime('%Y-%m-%d') if v else None,
            Decimal: lambda v: float(v) if v else None
        }

class InvoiceStatusUpdate(BaseModel):
    """发票状态更新数据结构"""
    status: int = Field(..., description="新状态：0-作废，1-正常", ge=0, le=1)
    reason: Optional[str] = Field(None, description="状态变更原因")

class InvoiceStatusBatchUpdate(BaseModel):
    """批量更新发票状态数据结构"""
    invoice_ids: List[int] = Field(..., description="发票ID列表")
    status: int = Field(..., description="新状态：0-作废，1-正常", ge=0, le=1)
    reason: Optional[str] = Field(None, description="状态变更原因")

class InvoiceExtractData(BaseModel):
    """PDF提取的发票数据"""
    发票类型: str = Field("", description="发票类型")
    发票号码: str = Field("", description="发票号码")
    开票日期: str = Field("", description="开票日期")
    开票人: str = Field("", description="开票人")
    购买方名称: str = Field("", description="购买方名称")
    购买方税号: str = Field("", description="购买方税号")
    销售方名称: str = Field("", description="销售方名称")
    销售方税号: str = Field("", description="销售方税号")
    合计金额: str = Field("", description="合计金额")
    合计税额: str = Field("", description="合计税额")
    价税合计大写: str = Field("", description="价税合计大写")
    价税合计小写: str = Field("", description="价税合计小写")
    文件名: str = Field("", description="文件名")

class InvoiceExtractResponse(BaseModel):
    """PDF提取结果响应"""
    success: bool = Field(..., description="是否成功")
    data: List[InvoiceExtractData] = Field(..., description="提取的发票数据")
    errors: List[str] = Field(default_factory=list, description="错误信息")

class InvoiceConfirmData(BaseModel):
    """前端确认的发票数据"""
    file_name: str = Field(..., description="文件名")
    invoice_type: Optional[str] = Field(None, description="发票类型")
    invoice_number: str = Field(..., description="发票号码")
    issue_date: Optional[str] = Field(None, description="开票日期")
    issuer: Optional[str] = Field(None, description="开票人")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_number: Optional[str] = Field(None, description="购买方税号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_number: Optional[str] = Field(None, description="销售方税号")
    total_amount: Optional[str] = Field(None, description="总金额")
    total_tax: Optional[str] = Field(None, description="总税额")
    total_amount_in_words: Optional[str] = Field(None, description="总金额大写")
    total_amount_in_numbers: Optional[str] = Field(None, description="总金额数字")
    status: int = Field(1, description="发票状态：0-作废，1-正常", ge=0, le=1)
    
    @validator('issue_date', pre=True)
    def parse_issue_date(cls, v):
        """解析开票日期"""
        if not v:
            return None
        # 处理中文日期格式 "2024年1月1日" -> "2024-01-01"
        import re
        if '年' in str(v) and '月' in str(v) and '日' in str(v):
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', str(v))
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return v

class InvoiceBatchConfirmRequest(BaseModel):
    """批量确认发票数据请求"""
    invoices: List[InvoiceConfirmData] = Field(..., description="确认的发票数据列表")
    folder_id: Optional[int] = Field(None, description="文件夹ID")

class InvoiceBatchConfirmResponse(BaseModel):
    """批量确认发票数据响应"""
    success_count: int = Field(..., description="成功数量")
    error_count: int = Field(..., description="失败数量")
    success_invoices: List[InvoiceResponse] = Field(..., description="成功的发票")
    error_details: List[Dict[str, Any]] = Field(..., description="错误详情")

class InvoiceSearchRequest(BaseModel):
    """发票搜索请求"""
    invoice_number: Optional[str] = Field(None, description="发票号码")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    issue_date_start: Optional[date] = Field(None, description="开票日期开始")
    issue_date_end: Optional[date] = Field(None, description="开票日期结束")
    amount_min: Optional[Decimal] = Field(None, description="最小金额")
    amount_max: Optional[Decimal] = Field(None, description="最大金额")
    status: Optional[int] = Field(None, description="发票状态：0-作废，1-正常，不传则查询所有", ge=0, le=1)

    @validator('invoice_number', 'buyer_name', 'seller_name', pre=True)
    def empty_string_to_none(cls, v):
        """将空字符串转换为None"""
        if v == "":
            return None
        return v
    
    @validator('issue_date_start', 'issue_date_end', pre=True)
    def parse_date_fields(cls, v):
        """处理日期字段，将空字符串转换为None"""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            try:
                # 尝试解析日期字符串
                from datetime import datetime
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                # 如果解析失败，返回None
                return None
        return v
    
    @validator('amount_min', 'amount_max', pre=True)
    def parse_amount_fields(cls, v):
        """处理金额字段，将空字符串转换为None"""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                return None
        return v

class InvoiceStatistics(BaseModel):
    """发票统计信息"""
    total_count: int = Field(..., description="总数量")
    active_count: int = Field(..., description="正常状态数量")
    void_count: int = Field(..., description="作废状态数量")
    total_amount: Decimal = Field(..., description="总金额")
    total_tax: Decimal = Field(..., description="总税额")
    average_amount: Decimal = Field(..., description="平均金额")
    this_month_count: int = Field(..., description="本月数量")
    this_month_amount: Decimal = Field(..., description="本月金额")

class InvoiceStatusHistoryResponse(BaseModel):
    """发票状态变更历史响应"""
    invoice_id: int = Field(..., description="发票ID")
    invoice_number: str = Field(..., description="发票号码")
    old_status: int = Field(..., description="原状态")
    new_status: int = Field(..., description="新状态")
    reason: Optional[str] = Field(None, description="变更原因")
    updated_by: int = Field(..., description="操作用户ID")
    updated_at: datetime = Field(..., description="变更时间")

    class Config:
        from_attributes = True 