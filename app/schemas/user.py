from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .role import RoleResponse
    from .menu import DepartmentResponse

# 用户头像相关模型
class UserAvatarBase(BaseModel):
    """用户头像基础模型"""
    avatar_path: str = Field(..., description="头像存储路径")
    is_active: bool = Field(default=True, description="是否当前使用")

class UserAvatarCreate(UserAvatarBase):
    """用户头像创建模型"""
    user_id: int = Field(..., description="用户ID")

class UserAvatarResponse(UserAvatarBase):
    """用户头像响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(
        ...,
        max_length=50,
        description="用户名"
    )
    email: Optional[str] = Field(
        None,
        max_length=100,
        description="邮箱"
    )
    department_id: Optional[int] = Field(
        default=None,
        description="部门ID"
    )
    status: Optional[int] = Field(
        default=1,
        description="状态：1-启用，0-禁用"
    )

class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    """用户数据库模型"""
    id: int
    password_hash: str = Field(..., max_length=255, description="密码哈希")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """用户响应模型"""
    roles: List["RoleResponse"] = []
    department: Optional["DepartmentResponse"] = None
    avatars: List[UserAvatarResponse] = []

    class Config:
        from_attributes = True
        exclude = {"password_hash"}

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# Token相关模型
class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")

class TokenPayload(BaseModel):
    """Token载荷模型"""
    sub: int = Field(..., description="用户ID")
    exp: int = Field(..., description="过期时间戳") 