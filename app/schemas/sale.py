from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import Query
from pydantic import BaseModel,Field



class SaleTableQuery(BaseModel):
    """销售表查询"""
    year: Optional[int] = Query(default=None, description="年份")
    month: Optional[int] = Query(default=None, description="月份")
    admin_unit_name: Optional[str] = Query(default=None, description="行政部门")
    employee_name: Optional[str] = Query(default=None, description="业务员")
    pageIndex: Optional[int] = Query(default=1, description="页码")
    pageSize: Optional[int] = Query(default=20, description="每页数量")

class SaleTable(BaseModel):
    Id: str = Field(..., description="销售目标ID")
    Year: int = Field(..., description="年份")
    Month: int = Field(..., description="月份")
    AdminUnitName: str = Field(..., description="行政部门")
    EmployeeName: str = Field(..., description="业务员")
    MonthlyTarget: int = Field(..., description="月度目标")
    CreatedBy: str = Field(..., description="创建人")
    CreatedAt: datetime = Field(..., description="创建时间")
    UpdatedAt: datetime = Field(..., description="更新时间")

class SaleTableResponse(BaseModel):
    """销售表响应"""
    list: List[SaleTable] = Field(..., description="销售表列表")
    total: int = Field(..., description="总数量")

class SaleTargetCreate(BaseModel):
    """销售目标创建"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    admin_unit_name: str = Field(..., description="行政部门")
    employee_name: str = Field(..., description="业务员")
    monthly_target: int = Field(..., description="月度目标")

class SaleTargetUpdate(BaseModel):
    """销售目标更新"""
    id: str = Field(..., description="销售目标ID")
    year: Optional[int] = Field(default=None, description="年份")
    month: Optional[int] = Field(default=None, description="月份")
    admin_unit_name: Optional[str] = Field(default=None, description="行政部门")
    employee_name: Optional[str] = Field(default=None, description="业务员")
    monthly_target: Optional[int] = Field(default=None, description="月度目标")

class SaleTargetSummaryQuery(BaseModel):
    """销售目标汇总查询"""
    year: Optional[int] = Field(default=None, description="年份")
    month: Optional[int] = Field(default=None, description="月份")

class SaleTargetSummary(BaseModel):
    """销售目标汇总响应"""
    YEAR: int = Field(..., description="年份")
    MONTH: int = Field(..., description="月份")
    ADMIN_UNIT_NAME: str = Field(..., description="行政单位")
    EMPLOYEE_NAME: str = Field(..., description="业务员")
    FORECAST_QTY: int = Field(..., description="预测销量")
    PRICE_QTY: int = Field(..., description="实际销量")
    PERCENTAGE: float = Field(..., description="完成率")

class SaleTargetSummaryResponse(BaseModel):
    """销售目标汇总响应"""
    list: List[SaleTargetSummary] = Field(..., description="销售目标汇总列表")

class SaleTargetDetailQuery(BaseModel):
    """销售目标详情查询"""
    year: Optional[int] = Field(default=None, description="年份")
    month: Optional[int] = Field(default=None, description="月份")
    employee_name: Optional[str] = Field(default=None, description="业务员")

class SaleTargetDetail(BaseModel):
    """销售目标详情响应"""
    YEAR: Optional[int] = Field(default=None, description="年份")
    MONTH: Optional[int] = Field(default=None, description="月份")
    ADMIN_UNIT_NAME: Optional[str] = Field(default=None, description="行政单位")
    EMPLOYEE_NAME: Optional[str] = Field(default=None, description="业务员")
    SHORTCUT: Optional[str] = Field(default=None, description="类别")
    ITEM_NAME: Optional[str] = Field(default=None, description="芯片名称")
    FORECAST_QTY: Optional[int] = Field(default=None, description="预测销量")
    PRICE_QTY: Optional[int] = Field(default=None, description="实际销量")
    PERCENTAGE: Optional[float] = Field(default=None, description="完成率")

class SaleTargetDetailResponse(BaseModel):
    """销售目标详情响应"""
    list: List[SaleTargetDetail] = Field(..., description="销售目标详情列表")

class SaleAmountAnalyzeQuery(BaseModel):
    """销售金额分析查询参数"""
    year: Optional[str] = Field(None, description="年份")
    month: Optional[str] = Field(None, description="月份")
    shortcut: Optional[str] = Field(None, description="产品类型")
    admin_unit_name: Optional[str] = Field(None, description="部门名称")
    employee_name: Optional[str] = Field(None, description="销售员姓名")
    item_name: Optional[str] = Field(None, description="产品名称")
    
    # 添加分组字段标志
    group_by_year: bool = Field(True, description="是否按年份分组")
    group_by_month: bool = Field(False, description="是否按月份分组")
    group_by_shortcut: bool = Field(False, description="是否按产品类型分组")
    group_by_admin_unit_name: bool = Field(False, description="是否按部门分组")
    group_by_employee_name: bool = Field(False, description="是否按销售员分组")
    group_by_item_name: bool = Field(False, description="是否按产品名称分组")

class SaleAmountAnalyze(BaseModel):
    """销售金额分析响应项"""
    YEAR: Optional[int] = Field(None, description="年份")
    MONTH: Optional[int] = Field(None, description="月份")
    SHORTCUT: Optional[str] = Field(None, description="产品类型")
    ADMIN_UNIT_NAME: Optional[str] = Field(None, description="部门名称")
    EMPLOYEE_NAME: Optional[str] = Field(None, description="销售员姓名")
    ITEM_NAME: Optional[str] = Field(None, description="产品名称")
    PRICE_QTY: Optional[int] = Field(None, description="销量")
    AMOUNT: Optional[float] = Field(None, description="销售金额")

class SaleAmountAnalyzeResponse(BaseModel):
    """销售金额分析响应"""
    list: List[SaleAmountAnalyze] = Field([], description="销售金额分析列表")

class SaleAnalysisPannel(BaseModel):
    """销售分析面板"""
    this_year_sale_qty: int = Field(..., description="本年销量")
    this_year_sale_amount: float = Field(..., description="本年销售额")
    this_month_sale_qty: int = Field(..., description="本月销量")
    this_month_sale_amount: float = Field(..., description="本月销售额")
    last_year_sale_qty: int = Field(..., description="去年销量")
    last_year_sale_amount: float = Field(..., description="去年销售额")
    last_month_sale_qty: int = Field(..., description="上月销量")
    last_month_sale_amount: float = Field(..., description="上月销售额")
    last_last_month_sale_qty: int = Field(..., description="上上月销量")
    last_last_month_sale_amount: float = Field(..., description="上上月销售额")
    month_on_month_qty: float = Field(..., description="环比销量")
    month_on_month_amount: float = Field(..., description="环比金额")
    year_on_year_qty: float = Field(..., description="同比销量")
    year_on_year_amount: float = Field(..., description="同比金额")

class SaleAnalysisPannelResponse(BaseModel):
    """销售分析面板响应"""
    list: List[SaleAnalysisPannel] = Field(..., description="销售分析面板列表")

class SaleForecastResponse(BaseModel):
    """销售预测"""
    YearForecast: int = Field(..., description="年份")
    MonthForecast: int = Field(..., description="月份")

class SaleAmountQuery(BaseModel):
    """销售金额查询"""
    year: Optional[str] = Field(None, description="年份")
    month: Optional[str] = Field(None, description="月份")
    admin_unit_name: Optional[str] = Field(None, description="部门名称")
    employee_name: Optional[str] = Field(None, description="销售员")
    group_by_year: bool = Field(True, description="是否按年份分组")
    group_by_month: bool = Field(False, description="是否按月份分组")
    group_by_admin_unit_name: bool = Field(False, description="是否按部门分组")
    group_by_employee_name: bool = Field(False, description="是否按销售员分组")

class SaleAmount(BaseModel):
    """销售金额详情"""
    YEAR: Optional[int] = Field(None, description="年份")
    MONTH: Optional[int] = Field(None, description="月份")
    ADMIN_UNIT_NAME: Optional[str] = Field(None, description="部门名称")
    EMPLOYEE_NAME: Optional[str] = Field(None, description="销售员")
    FORECAST_AMOUNT: Optional[float] = Field(None, description="预测金额")
    PRICE_AMOUNT: Optional[float] = Field(None, description="实际金额")
    PERCENTAGE: Optional[float] = Field(None, description="完成率")

class SaleAmountResponse(BaseModel):
    """销售金额详情响应"""
    list: List[SaleAmount] = Field([], description="销售金额详情列表")

class SaleAmountBarChartQuery(BaseModel):
    """销售金额柱状图查询"""
    year: Optional[str] = Field(None, description="年份")
    month: Optional[str] = Field(None, description="月份")

class SaleAmountBarChartEChartsDataItem(BaseModel):
    """ECharts单个数据项"""
    name: str          # 数据项名称（如部门、业务员等）
    value: float       # 数据值（如金额）
    group_id: str      # 所属组ID
    child_group_id: Optional[str] = None  # 子组ID（可选，用于下钻）

class SaleAmountBarChartEChartsLevelData(BaseModel):
    """ECharts某一层级的数据"""
    level_id: str           # 层级ID
    items: List[SaleAmountBarChartEChartsDataItem]  # 该层级的所有数据项

class SaleAmountBarChartEChartsResponse(BaseModel):
    """ECharts数据的完整响应"""
    list: List[SaleAmountBarChartEChartsLevelData] = Field(..., description="ECharts数据列表")
