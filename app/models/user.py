from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, func

class UserRole(SQLModel, table=True):
    """用户-角色关联表"""
    __tablename__ = "huaxinAdmin_userRoles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        nullable=False,
        description="用户ID"
    )
    role_id: int = Field(
        nullable=False,
        description="角色ID"
    )
    assigned_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="分配时间"
    )

class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "huaxinAdmin_users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False),
        description="用户名"
    )
    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="密码哈希"
    )
    email: Optional[str] = Field(
        sa_column=Column(String(100), unique=True, nullable=True),
        default=None,
        description="邮箱"
    )
    department_id: Optional[int] = Field(
        default=None,
        description="部门ID"
    )
    status: Optional[int] = Field(
        default=1,
        sa_column_kwargs={"server_default": "1"},
        description="状态：1-启用，0-禁用"
    )
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        default=None,
        description="最后登录时间"
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

class UserAvatar(SQLModel, table=True):
    """用户头像模型"""
    __tablename__ = "huaxinAdmin_userAvatars"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        nullable=False,
        description="用户ID"
    )
    avatar_url: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="头像URL"
    )
    is_active: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": "1"},
        description="是否当前使用"
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