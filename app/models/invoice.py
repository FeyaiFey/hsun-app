from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, Date, DECIMAL, Integer, func, Index

class Invoice(SQLModel, table=True):
    """发票模型"""
    __tablename__ = "huaxinAdmin_Invoices"

    # 主键
    invoice_id: Optional[int] = Field(
        default=None,
        sa_column=Column("InvoiceID", Integer, primary_key=True, autoincrement=True),
        description="发票ID"
    )
    
    # 基本信息
    file_name: str = Field(
        sa_column=Column("FileName", String(255), nullable=False),
        description="文件名"
    )
    invoice_type: Optional[str] = Field(
        sa_column=Column("InvoiceType", String(100), nullable=True),
        default=None,
        description="发票类型"
    )
    invoice_number: str = Field(
        sa_column=Column("InvoiceNumber", String(50), unique=True, nullable=False),
        description="发票号码"
    )
    issue_date: Optional[date] = Field(
        sa_column=Column("IssueDate", Date, nullable=True),
        default=None,
        description="开票日期"
    )
    issuer: Optional[str] = Field(
        sa_column=Column("Issuer", String(100), nullable=True),
        default=None,
        description="开票人"
    )
    
    # 购买方信息
    buyer_name: Optional[str] = Field(
        sa_column=Column("BuyerName", String(255), nullable=True),
        default=None,
        description="购买方名称"
    )
    buyer_tax_number: Optional[str] = Field(
        sa_column=Column("BuyerTaxNumber", String(50), nullable=True),
        default=None,
        description="购买方税号"
    )
    
    # 销售方信息
    seller_name: Optional[str] = Field(
        sa_column=Column("SellerName", String(255), nullable=True),
        default=None,
        description="销售方名称"
    )
    seller_tax_number: Optional[str] = Field(
        sa_column=Column("SellerTaxNumber", String(50), nullable=True),
        default=None,
        description="销售方税号"
    )
    
    # 金额信息
    total_amount: Optional[Decimal] = Field(
        sa_column=Column("TotalAmount", DECIMAL(18, 2), nullable=True),
        default=None,
        description="总金额"
    )
    total_tax: Optional[Decimal] = Field(
        sa_column=Column("TotalTax", DECIMAL(18, 2), nullable=True),
        default=None,
        description="总税额"
    )
    total_amount_in_words: Optional[str] = Field(
        sa_column=Column("TotalAmountInWords", String(255), nullable=True),
        default=None,
        description="总金额大写"
    )
    total_amount_in_numbers: Optional[Decimal] = Field(
        sa_column=Column("TotalAmountInNumbers", DECIMAL(18, 2), nullable=True),
        default=None,
        description="总金额数字"
    )
    
    # 状态字段：0-作废，1-正常
    status: int = Field(
        sa_column=Column("Status", Integer, nullable=False, server_default="1"),
        default=1,
        description="发票状态：0-作废，1-正常"
    )
    
    # 系统字段
    created_at: datetime = Field(
        sa_column=Column(
            "CreatedAt",
            DateTime,
            server_default=func.getdate(),
            nullable=False
        ),
        description="创建时间"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            "UpdatedAt",
            DateTime,
            server_default=func.getdate(),
            nullable=False
        ),
        description="更新时间"
    )

    # 定义索引 - 使用数据库中的实际列名
    __table_args__ = (
        Index('IX_Invoices_InvoiceNumber', 'InvoiceNumber'),
        Index('IX_Invoices_IssueDate', 'IssueDate'),
        Index('IX_Invoices_BuyerName', 'BuyerName'),
        Index('IX_Invoices_SellerName', 'SellerName'),
        Index('IX_Invoices_Status', 'Status'),
    )

    class Config:
        """模型配置"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,
            date: lambda v: v.strftime('%Y-%m-%d') if v else None,
            Decimal: lambda v: float(v) if v else None
        }

    @property
    def status_text(self) -> str:
        """获取状态文本描述"""
        return "正常" if self.status == 1 else "作废"
    
    def is_active(self) -> bool:
        """判断发票是否为正常状态"""
        return self.status == 1
    
    def is_void(self) -> bool:
        """判断发票是否为作废状态"""
        return self.status == 0 