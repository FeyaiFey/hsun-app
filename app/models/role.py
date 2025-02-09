from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func

if TYPE_CHECKING:
    from .user import User
    from .menu import Menu

# 导入 UserRole 类
from .user import UserRole

# 关联表定义
class RoleMenu(SQLModel, table=True):
    """角色-菜单关联表"""
    __tablename__ = "huaxinAdmin_roleMenus"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="huaxinAdmin_roles.id", nullable=False)
    menu_id: int = Field(foreign_key="huaxinAdmin_menus.id", nullable=False)
    assigned_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            server_default=func.sysdatetime()
        )
    )

class RolePermission(SQLModel, table=True):
    """角色-权限关联表"""
    __tablename__ = "huaxinAdmin_rolePermissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="huaxinAdmin_roles.id", nullable=False)
    permission_id: int = Field(foreign_key="huaxinAdmin_permissions.id", nullable=False)
    granted_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        ),
        description="授权时间"
    )

# 主要模型定义
class Role(SQLModel, table=True):
    """角色模型"""
    __tablename__ = "huaxinAdmin_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False),
        description="角色名称"
    )
    description: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="角色描述"
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
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole  # 使用实际的模型类
    )
    menus: List["Menu"] = Relationship(
        back_populates="roles",
        link_model=RoleMenu
    )
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission
    )

class Permission(SQLModel, table=True):
    """权限模型"""
    __tablename__ = "huaxinAdmin_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_id: Optional[int] = Field(
        foreign_key="huaxinAdmin_menus.id",
        default=None,
        description="菜单ID"
    )
    name: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="权限名称"
    )
    action: Optional[str] = Field(
        sa_column=Column(String(255)),
        description="权限动作"
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
    roles: List[Role] = Relationship(
        back_populates="permissions",
        link_model=RolePermission
    )
    menu: Optional["Menu"] = Relationship(back_populates="permissions")