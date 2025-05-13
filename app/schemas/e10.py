from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class FeatureGroupNameQuery(BaseModel):
    """品号群组查询参数"""
    feature_group_name: Optional[str] = Field(None, description="品号群组")

class FeatureGroupName(BaseModel):
    label: str = Field(..., description="品号群组")
    value: str = Field(..., description="品号群组值")

class FeatureGroupNameResponse(BaseModel):
    """品号群组响应"""
    list: List[FeatureGroupName] = Field(..., description="品号群组列表")

class ItemCodeQuery(BaseModel):
    """品号查询参数"""
    item_code: Optional[str] = Field(None, description="品号")

class ItemCode(BaseModel):
    label: str = Field(..., description="品号")
    value: str = Field(..., description="品号值")

class ItemCodeResponse(BaseModel):
    """品号响应"""
    list: List[ItemCode] = Field(..., description="品号列表")

class ItemNameQuery(BaseModel):
    """品名查询参数"""
    item_name: Optional[str] = Field(None, description="品名")

class ItemName(BaseModel):
    label: str = Field(..., description="品名")
    value: str = Field(..., description="品名值")

class ItemNameResponse(BaseModel):
    """品名响应"""
    list: List[ItemName] = Field(..., description="品名列表")

class LotCodeQuery(BaseModel):
    """批号查询参数"""
    lot_code: Optional[str] = Field(None, description="批号")

class LotCode(BaseModel):
    label: str = Field(..., description="批号")
    value: str = Field(..., description="批号值")

class LotCodeResponse(BaseModel):
    """批号响应"""
    list: List[LotCode] = Field(..., description="批号列表")

class WarehouseNameQuery(BaseModel):
    """仓库查询参数"""
    warehouse_name: Optional[str] = Field(None, description="仓库")

class WarehouseName(BaseModel):
    label: str = Field(..., description="仓库")
    value: str = Field(..., description="仓库值")

class WarehouseNameResponse(BaseModel):
    """仓库响应"""
    list: List[WarehouseName] = Field(..., description="仓库列表")

class TestingProgramQuery(BaseModel):
    """测试程序查询参数"""
    testing_program: Optional[str] = Field(None, description="测试程序")

class TestingProgram(BaseModel):
    label: str = Field(..., description="测试程序")
    value: str = Field(..., description="测试程序值")

class TestingProgramResponse(BaseModel):
    """测试程序响应"""
    list: List[TestingProgram] = Field(..., description="测试程序列表")

class BurningProgramQuery(BaseModel):
    """烧录程序查询参数"""
    burning_program: Optional[str] = Field(None, description="烧录程序")

class BurningProgram(BaseModel):
    label: str = Field(..., description="烧录程序")
    value: str = Field(..., description="烧录程序值")

class BurningProgramResponse(BaseModel):
    """烧录程序响应"""
    list: List[BurningProgram] = Field(..., description="烧录程序列表")

class SaleUnit(BaseModel):
    """销售单位"""
    label: str = Field(..., description="销售单位")
    value: str = Field(..., description="销售单位值")

class SaleUnitResponse(BaseModel):
    """销售单位响应"""
    list: List[SaleUnit] = Field(..., description="销售单位列表")

class Sales(BaseModel):
    """销售员"""
    label: str = Field(..., description="销售员名称")
    value: str = Field(..., description="销售员名称值")

class SalesResponse(BaseModel):
    """销售员响应"""
    list: List[Sales] = Field(..., description="销售员列表")
