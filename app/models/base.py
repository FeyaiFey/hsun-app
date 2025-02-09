from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func

def to_dict(self):
    """
    将模型转换为字典
    """
    return {
        column.name: getattr(self, column.name)
        for column in self.__table__.columns
    }

def update(self, **kwargs):
    """
    更新模型属性
    """
    for key, value in kwargs.items():
        if hasattr(self, key):
            setattr(self, key, value)

# 扩展 SQLModel 添加通用方法
SQLModel.to_dict = to_dict
SQLModel.update = update

class TimeStampModel(SQLModel):
    """包含时间戳的基础模型"""
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            onupdate=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        )
    )

class StatusModel(TimeStampModel):
    """包含状态字段的基础模型"""
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用") 