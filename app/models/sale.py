from uuid import UUID
from datetime import datetime
from sqlmodel import SQLModel, Field

class Sale(SQLModel, table=True):
    """销售"""
    __tablename__ = "huaxinAdmin_SaleTarget"

    Id: str = Field(default=None, primary_key=True, nullable=False, description="销售目标ID")
    Year: int = Field(default=None, nullable=False, description="年份")
    Month: int = Field(default=None, nullable=False, description="月份")
    AdminUnitName: str = Field(default=None, nullable=False, description="行政部门")
    EmployeeName: str = Field(default=None, nullable=False, description="业务员")
    MonthlyTarget: int = Field(default=None, nullable=False, description="月度目标")
    CreatedBy: str = Field(default=None, nullable=False, description="创建人")
    CreatedAt: datetime = Field(default=None, nullable=False, description="创建时间")
    UpdatedAt: datetime = Field(default=None, nullable=False, description="更新时间")


