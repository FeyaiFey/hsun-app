from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, Boolean, func

class Menu(SQLModel, table=True):
    """菜单模型"""
    __tablename__ = "huaxinAdmin_menus"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(
        default=None,
        description="父菜单ID"
    )
    path: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="路由路径"
    )
    component: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="组件路径"
    )
    redirect: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="重定向路径"
    )
    name: str = Field(
        sa_column=Column(String(100), nullable=False),
        description="路由名称"
    )
    title: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="菜单标题"
    )
    icon: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="图标"
    )
    always_show: Optional[bool] = Field(
        sa_column=Column(Boolean, server_default="0"),
        description="是否总是显示"
    )
    no_cache: Optional[bool] = Field(
        sa_column=Column(Boolean, server_default="0"),
        description="是否不缓存"
    )
    affix: Optional[bool] = Field(
        sa_column=Column(Boolean, server_default="0"),
        description="是否固定"
    )
    hidden: Optional[bool] = Field(
        sa_column=Column(Boolean, server_default="0"),
        description="是否隐藏"
    )
    external_link: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="外部链接"
    )
    permission: Optional[str] = Field(
        description="权限标识"
    )
    menu_order: Optional[int] = Field(
        default=0,
        sa_column_kwargs={"server_default": "0"},
        description="排序"
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