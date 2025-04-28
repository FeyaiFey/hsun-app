from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

# 基础用户模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    department_id: Optional[int] = Field(default=None, description="部门ID")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

# 创建用户
class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=20, description="密码")

# 更新用户
class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = Field(None, min_length=6, max_length=20)

# 用户登录
class UserLogin(BaseModel):
    """用户登录模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: str = Field(..., description="密码")

# 用户信息
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
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# Token相关
class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: int = Field(..., description="用户ID")
    exp: datetime = Field(..., description="过期时间")

# 密码更新请求
class UpdatePasswordRequest(BaseModel):
    """更新密码请求模型"""
    old_password: str
    new_password: str

# 批量删除请求
class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    ids: List[int]

# 用户表格列表项
class UserTableItem(BaseModel):
    """用户表格列表项"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    department_id: Optional[int] = Field(None, description="部门ID")
    department_name: Optional[str] = Field(None, description="部门名称")
    role_id: Optional[List[int]] = Field(None, description="角色ID")
    role_name: Optional[List[str]] = Field(None, description="角色名称")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(..., description="状态：1-启用，0-禁用")
    last_login: Optional[str] = Field(None, description="最后登录时间")
    created_at: str = Field(..., description="创建时间")

# 用户表格列表响应
class UserTableListResponse(BaseModel):
    """用户表格列表响应"""
    list: List[UserTableItem] = Field(..., description="用户列表")
    total: int = Field(..., description="总记录数")

# 更新邮箱密码请求
class UpdateEmailPasswordRequest(BaseModel):
    """更新邮箱密码请求模型"""
    new_password: str

# 用户邮箱信息
class UserEmailInfo(BaseModel):
    """用户邮箱信息"""
    ID: int = Field(..., description="用户ID")
    EMAIL: str = Field(..., description="邮箱")
    PASSWORD: Optional[str] = Field(None, description="邮箱密码")
    IMAP_SERVER: str = Field(..., description="IMAP服务器")
    IMAP_PORT: int = Field(..., description="IMAP端口")
    IMAP_USE_SSL: int = Field(..., description="IMAP是否使用SSL")
    SMTP_SERVER: str = Field(..., description="SMTP服务器")
    SMTP_PORT: int = Field(..., description="SMTP端口")
    SMTP_USE_SSL: int = Field(..., description="SMTP是否使用SSL")
    