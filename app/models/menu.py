from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import remote
from .role import RoleMenu

if TYPE_CHECKING:
    from .user import User
    from .role import Role, Permission, RoleMenu

class Department(SQLModel, table=True):
    """部门模型"""
    __tablename__ = "huaxinAdmin_departments"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False),
        description="部门名称"
    )
    parent_id: Optional[int] = Field(
        foreign_key="huaxinAdmin_departments.id",
        default=None,
        description="父部门ID"
    )
    description: Optional[str] = Field(
        sa_column=Column(String(200)),
        default=None,
        description="部门描述"
    )
    status: int = Field(default=1, description="状态：1-启用，0-禁用")
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

    # 关系
    parent: Optional["Department"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": [id]}
    )
    children: List["Department"] = Relationship(back_populates="parent")
    users: List["User"] = Relationship(back_populates="department")

class Menu(SQLModel, table=True):
    """菜单模型"""
    __tablename__ = "huaxinAdmin_menus"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(
        foreign_key="huaxinAdmin_menus.id",
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
        sa_column=Column(Boolean, default=False),
        description="是否总是显示"
    )
    no_cache: Optional[bool] = Field(
        sa_column=Column(Boolean, default=False),
        description="是否不缓存"
    )
    affix: Optional[bool] = Field(
        sa_column=Column(Boolean, default=False),
        description="是否固定"
    )
    hidden: Optional[bool] = Field(
        sa_column=Column(Boolean, default=False),
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
        description="排序"
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
    parent: Optional["Menu"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": [id]}
    )
    children: List["Menu"] = Relationship(back_populates="parent")
    permissions: List["Permission"] = Relationship(back_populates="menu")
    roles: List["Role"] = Relationship(
        back_populates="menus",
        link_model=RoleMenu
    ) 