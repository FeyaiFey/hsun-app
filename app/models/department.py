from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

class Department(SQLModel, table=True):
    """部门模型"""
    __tablename__ = "huaxinAdmin_departments"

    id: Optional[int] = Field(default=None, primary_key=True)
    department_name: str = Field(
        sa_column_kwargs={"unique": True, "nullable": False},
        description="部门名称"
    )
    parent_id: Optional[int] = Field(
        default=None, 
        foreign_key="huaxinAdmin_departments.id",
        description="父部门ID"
    )
    status: Optional[int] = Field(
        default=1,
        description="状态：1-启用，0-禁用"
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        ),
        description="创建时间"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            onupdate=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        ),
        description="更新时间"
    )

    # 关系
    parent: Optional["Department"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": [id]}
    )
    children: List["Department"] = Relationship(back_populates="parent")
    users: List["User"] = Relationship(back_populates="department") 