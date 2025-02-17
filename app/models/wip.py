from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, Integer, Date

class FabWip(SQLModel, table=True):
    """晶圆厂WIP"""
    __tablename__ = "huaxinAdmin_wip_fab"

    lot: str = Field(
        sa_column=Column(String(255), primary_key=True),
        description="批号"
    )
    purchaseOrder: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="采购订单"
    )
    itemName: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="产品名称"
    )
    qty: Optional[int] = Field(
        default=None,
        description="数量"
    )
    status: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="状态"
    )
    stage: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="阶段"
    )
    layerCount: Optional[int] = Field(
        default=None,
        description="总层数"
    )
    remainLayer: Optional[int] = Field(
        default=None,
        description="剩余层数"
    )
    currentPosition: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="当前位置"
    )
    forecastDate: Optional[date] = Field(
        sa_column=Column(Date),
        default=None,
        description="预计交期"
    )
    supplier: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="供应商"
    )
    finished_at: Optional[date] = Field(
        sa_column=Column(Date),
        default=None,
        description="完成时间"
    )
    create_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(7),
            server_default="sysdatetime()",
            nullable=True
        ),
        description="创建时间"
    )
    modified_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(7),
            server_default="sysdatetime()",
            nullable=True
        ),
        description="修改时间"
    )

class AssyWip(SQLModel, table=True):
    """封装厂WIP"""
    __tablename__ = "huaxinAdmin_wip_assy"

    订单号: str = Field(
        sa_column=Column(String(255), primary_key=True),
        description="订单号"
    )
    封装厂: str = Field(
        sa_column=Column(String(255)),
        description="封装厂"
    )
    当前工序: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="当前工序"
    )
    预计交期: Optional[date] = Field(
        sa_column=Column(Date),
        default=None,
        description="预计交期"
    )
    次日预计: Optional[int] = Field(
        default=None,
        description="次日预计"
    )
    三日预计: Optional[int] = Field(
        default=None,
        description="三日预计"
    )
    七日预计: Optional[int] = Field(
        default=None,
        description="七日预计"
    )
    仓库库存: Optional[int] = Field(
        default=None,
        description="仓库库存"
    )
    扣留信息: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="扣留信息"
    )
    在线合计: Optional[int] = Field(
        default=None,
        description="在线合计"
    )
    研磨: Optional[int] = Field(
        default=None,
        description="研磨"
    )
    切割: Optional[int] = Field(
        default=None,
        description="切割"
    )
    待装片: Optional[int] = Field(
        default=None,
        description="待装片"
    )
    装片: Optional[int] = Field(
        default=None,
        description="装片"
    )
    银胶固化: Optional[int] = Field(
        default=None,
        description="银胶固化"
    )
    等离子清洗1: Optional[int] = Field(
        default=None,
        description="等离子清洗1"
    )
    键合: Optional[int] = Field(
        default=None,
        description="键合"
    )
    三目检: Optional[int] = Field(
        default=None,
        description="三目检"
    )
    等离子清洗2: Optional[int] = Field(
        default=None,
        description="等离子清洗2"
    )
    塑封: Optional[int] = Field(
        default=None,
        description="塑封"
    )
    后固化: Optional[int] = Field(
        default=None,
        description="后固化"
    )
    回流焊: Optional[int] = Field(
        default=None,
        description="回流焊"
    )
    电镀: Optional[int] = Field(
        default=None,
        description="电镀"
    )
    打印: Optional[int] = Field(
        default=None,
        description="打印"
    )
    后切割: Optional[int] = Field(
        default=None,
        description="后切割"
    )
    切筋成型: Optional[int] = Field(
        default=None,
        description="切筋成型"
    )
    测编打印: Optional[int] = Field(
        default=None,
        description="测编打印"
    )
    外观检: Optional[int] = Field(
        default=None,
        description="外观检"
    )
    包装: Optional[int] = Field(
        default=None,
        description="包装"
    )
    待入库: Optional[int] = Field(
        default=None,
        description="待入库"
    )
    finished_at: Optional[date] = Field(
        sa_column=Column(Date),
        default=None,
        description="完成时间"
    )
    create_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(7),
            server_default="sysdatetime()",
            nullable=True
        ),
        description="创建时间"
    )
    modified_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(7),
            server_default="sysdatetime()",
            nullable=True
        ),
        description="修改时间"
    )
