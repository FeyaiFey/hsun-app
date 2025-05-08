from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import Query
from pydantic import BaseModel,Field



class SaleTableQuery(BaseModel):
    """销售表查询"""
    year: Optional[int] = Query(default=None, description="年份")
    month: Optional[int] = Query(default=None, description="月份")
    yearmonth: Optional[str] = Query(default=None, description="年月")
    pageIndex: Optional[int] = Query(default=1, description="页码")
    pageSize: Optional[int] = Query(default=20, description="每页数量")

class SaleTable(BaseModel):
    Id: UUID = Field(..., description="销售目标ID")
    Year: int = Field(..., description="年份")
    Month: int = Field(..., description="月份")
    YearMonth: str = Field(..., description="年月")
    MonthlyTarget: int = Field(..., description="月度目标")
    AnnualTarget: int = Field(..., description="年度目标")
    CreatedBy: str = Field(..., description="创建人")
    CreatedAt: datetime = Field(..., description="创建时间")
    UpdatedAt: datetime = Field(..., description="更新时间")

class SaleTableResponse(BaseModel):
    """销售表响应"""
    list: List[SaleTable] = Field(..., description="销售表列表")
    total: int = Field(..., description="总数量")

class SaleTargetCreate(BaseModel):
    """销售目标创建"""
    year: Optional[int] = Field(..., description="年份")
    month: Optional[int] = Field(..., description="月份")
    yearmonth: Optional[str] = Field(..., description="年月")
    monthly_target: Optional[int] = Field(..., description="月度目标")
    annual_target: Optional[int] = Field(..., description="年度目标")

class SaleTargetUpdate(BaseModel):
    """销售目标更新"""
    id: UUID = Field(..., description="销售目标ID")
    year: Optional[int] = Field(..., description="年份")
    month: Optional[int] = Field(..., description="月份")
    yearmonth: Optional[str] = Field(..., description="年月")
    monthly_target: Optional[int] = Field(..., description="月度目标")
    annual_target: Optional[int] = Field(..., description="年度目标")


