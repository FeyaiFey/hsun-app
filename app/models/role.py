from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, func

class RoleMenu(SQLModel, table=True):
    """角色-菜单关联表"""
    __tablename__ = "huaxinAdmin_roleMenus"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(
        nullable=False,
        description="角色ID"
    )
    menu_id: int = Field(
        nullable=False,
        description="菜单ID"
    )
    assigned_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="分配时间"
    )

class RolePermission(SQLModel, table=True):
    """角色-权限关联表"""
    __tablename__ = "huaxinAdmin_rolePermissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(
        nullable=False,
        description="角色ID"
    )
    permission_id: int = Field(
        nullable=False,
        description="权限ID"
    )
    granted_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="授权时间"
    )

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

class Permission(SQLModel, table=True):
    """权限模型"""
    __tablename__ = "huaxinAdmin_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_id: Optional[int] = Field(
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