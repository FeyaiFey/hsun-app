from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class FabWipQuery(BaseModel):
    """晶圆厂WIP查询参数"""
    purchaseOrder: Optional[str] = None
    lot: Optional[str] = None
    itemName: Optional[str] = None
    forecastDate: Optional[date] = None
    supplier: Optional[str] = None

class AssyWipItem(BaseModel):
    """封装厂WIP响应"""
    订单号: Optional[str] = Field(..., description="订单号")
    封装厂: Optional[str] = Field(..., description="封装厂")
    当前工序: Optional[int] = Field(None, description="当前工序")
    预计交期: Optional[date] = Field(None, description="预计交期")
    次日预计: Optional[int] = Field(None, description="次日预计")
    三日预计: Optional[int] = Field(None, description="三日预计")
    七日预计: Optional[int] = Field(None, description="七日预计")
    仓库库存: Optional[int] = Field(None, description="仓库库存")
    扣留信息: Optional[str] = Field(None, description="扣留信息")
    滞留天数: Optional[int] = Field(None, description="滞留天数")
    在线合计: Optional[int] = Field(None, description="在线合计")
    研磨: Optional[int] = Field(None, description="研磨")
    切割: Optional[int] = Field(None, description="切割")
    待装片: Optional[int] = Field(None, description="待装片")
    装片: Optional[int] = Field(None, description="装片")
    银胶固化: Optional[int] = Field(None, description="银胶固化")
    等离子清洗1: Optional[int] = Field(None, description="等离子清洗1")
    键合: Optional[int] = Field(None, description="键合")
    三目检: Optional[int] = Field(None, description="三目检")
    等离子清洗2: Optional[int] = Field(None, description="等离子清洗2")
    塑封: Optional[int] = Field(None, description="塑封")
    后固化: Optional[int] = Field(None, description="后固化")
    回流焊: Optional[int] = Field(None, description="回流焊")
    电镀: Optional[int] = Field(None, description="电镀")
    打印: Optional[int] = Field(None, description="打印")
    后切割: Optional[int] = Field(None, description="后切割")
    切筋成型: Optional[int] = Field(None, description="切筋成型")
    测编打印: Optional[int] = Field(None, description="测编打印")
    外观检: Optional[int] = Field(None, description="外观检")
    包装: Optional[int] = Field(None, description="包装")
    待入库: Optional[int] = Field(None, description="待入库")
    finished_at: Optional[date] = Field(None, description="完成时间")
    modified_at: Optional[date] = Field(None, description="修改时间")