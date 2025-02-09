from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func

if TYPE_CHECKING:
    from .role import Role
    from .menu import Department

# 关联表定义
class UserRole(SQLModel, table=True):
    """用户-角色关联表"""
    __tablename__ = "huaxinAdmin_userRoles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="huaxinAdmin_users.id",
        nullable=False,
        description="用户ID"
    )
    role_id: int = Field(
        foreign_key="huaxinAdmin_roles.id",
        nullable=False,
        description="角色ID"
    )
    assigned_at: datetime = Field(
        sa_column=Column(
            DateTime,
            default=datetime.now,
            server_default=func.sysdatetime(),
            nullable=False
        ),
        description="分配时间"
    )

# 主要模型定义
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
        foreign_key="huaxinAdmin_departments.id",
        default=None,
        description="部门ID"
    )
    status: Optional[int] = Field(
        default=1,
        description="状态：1-启用，0-禁用"
    )
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime),
        default=None,
        description="最后登录时间"
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
    department: Optional["Department"] = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole
    )
    avatars: List["UserAvatar"] = Relationship(back_populates="user")

class UserAvatar(SQLModel, table=True):
    """用户头像模型"""
    __tablename__ = "huaxinAdmin_userAvatars"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="huaxinAdmin_users.id",
        nullable=False,
        description="用户ID"
    )
    avatar_path: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="头像存储路径"
    )
    is_active: bool = Field(default=True, description="是否当前使用")
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
    user: User = Relationship(back_populates="avatars") 