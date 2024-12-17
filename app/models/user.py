from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "huaxin_users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    nickname: str
    avatar_url: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    # 添加反向关系
    user_departments: List["UserDepartments"] = Relationship(back_populates="user")

class Department(SQLModel, table=True):
    __tablename__ = "huaxin_departments"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=255, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # 添加反向关系
    user_departments: List["UserDepartments"] = Relationship(back_populates="department")
    department_permissions: List["DepartmentPermissions"] = Relationship(back_populates="department")

class Permission(SQLModel, table=True):
    __tablename__ = "huaxin_permissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=255)
    key: str = Field(..., max_length=255, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # 添加反向关系
    department_permissions: List["DepartmentPermissions"] = Relationship(back_populates="permission")

class DepartmentPermissions(SQLModel, table=True):
    __tablename__ = "huaxin_department_permissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    department_id: int = Field(..., foreign_key="departments.id")
    permission_id: int = Field(..., foreign_key="permissions.id")
    created_at: datetime = Field(default_factory=datetime.now)

    # 定义关系（可选，可用于方便地在代码中进行关联查询等操作）
    department: Optional["Department"] = Relationship(back_populates="department_permissions")
    permission: Optional["Permission"] = Relationship(back_populates="department_permissions")

class UserDepartments(SQLModel, table=True):
    __tablename__ = "huaxin_user_departments"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(..., foreign_key="users.id")
    department_id: int = Field(..., foreign_key="departments.id")
    created_at: datetime = Field(default_factory=datetime.now)

    # 可定义关联关系（方便后续在代码中进行相关操作，比如通过关联查询获取更多信息）
    user: Optional["User"] = Relationship(back_populates="user_departments")
    department: Optional["Department"] = Relationship(back_populates="user_departments")