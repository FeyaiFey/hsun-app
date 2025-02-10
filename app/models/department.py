from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, func

class Department(SQLModel, table=True):
    """部门模型"""
    __tablename__ = "huaxinAdmin_departments"

    id: Optional[int] = Field(default=None, primary_key=True)
    department_name: str = Field(
        sa_column=Column(String(100), unique=True, nullable=False),
        description="部门名称"
    )
    parent_id: Optional[int] = Field(
        default=None,
        description="父部门ID"
    )
    status: Optional[int] = Field(
        default=1,
        sa_column_kwargs={"server_default": "1"},
        description="状态：1-启用，0-禁用"
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="创建时间"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="更新时间"
    )