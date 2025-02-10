from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

# 简单部门信息
class UserDepartmentInfo(BaseModel):
    """部门简单信息"""
    id: int
    department_name: str
    status: int

# 简单角色信息
class UserRoleInfo(BaseModel):
    """角色简单信息"""
    id: int
    role_name: str
    status: int

# 用户头像相关模型
class UserAvatarBase(BaseModel):
    """用户头像基础模型"""
    user_id: int = Field(..., description="用户ID")
    avatar_url: str = Field(..., max_length=255, description="头像URL")
    is_active: bool = Field(default=True, description="是否当前使用")

class UserAvatarCreate(UserAvatarBase):
    """用户头像创建模型"""
    pass

class UserAvatarResponse(UserAvatarBase):
    """用户头像响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department_id: Optional[int] = Field(default=None, description="部门ID")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=20, description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = Field(None, min_length=6, max_length=20)

class UserInDB(UserBase):
    """用户数据库模型"""
    id: int
    password_hash: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """用户响应模型"""
    department: Optional[UserDepartmentInfo] = None
    roles: List[UserRoleInfo] = []
    avatars: List[UserAvatarResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        exclude = {"password_hash"}

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: int = Field(..., description="用户ID")
    exp: datetime = Field(..., description="过期时间") 