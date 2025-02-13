from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department_id: Optional[int] = Field(default=None, description="部门ID")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

class UserLogin(BaseModel):
    """用户登录模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(..., description="密码")

class UserType(BaseModel):
    """用户信息类型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    username: str = Field(..., max_length=50, description="用户名")
    department_name: str = Field(..., description="部门名称")
    roles: List[str]
    avatar_url: str = Field(...,description="头像路由")
    password: str = Field(exclude=True)  # 确保密码不会被序列化

class UserInfoType(BaseModel):
    """用户信息响应类型"""
    userinfo: UserType
    token: str 

class UserInfoResponse(BaseModel):
    """用户信息响应模型"""
    username: str = Field(..., max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(...,description="密码")
    department_name: str = Field(..., description="部门名称")
    roles: List[str]
    avatar_url: str = Field(...,description="头像路由")

class UserInDB(BaseModel):
    """用户数据库模型"""
    id: int
    username: str = Field(..., max_length=50, description="用户名")
    password_hash: str = Field(...,description="密码哈希")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department_id: Optional[int] = Field(default=None, description="部门ID")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")
    last_login: Optional[datetime] = Field(default=None,description="上次登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: int = Field(..., description="用户ID")
    exp: datetime = Field(..., description="过期时间")

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = Field(None, min_length=6, max_length=20)