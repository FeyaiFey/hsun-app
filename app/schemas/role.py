from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# 简单用户信息
class RoleUserInfo(BaseModel):
    """用户简单信息"""
    id: int
    username: str
    email: Optional[str] = None
    status: int

# 简单菜单信息
class RoleMenuInfo(BaseModel):
    """菜单简单信息"""
    id: int
    name: str
    title: str
    path: str

# 权限相关模型
class PermissionBase(BaseModel):
    """权限基础模型"""
    menu_id: Optional[int] = Field(default=None, description="菜单ID")
    name: Optional[str] = Field(None, max_length=255, description="权限名称")
    action: Optional[str] = Field(None, max_length=255, description="权限动作")

class PermissionCreate(PermissionBase):
    """权限创建模型"""
    pass

class PermissionUpdate(BaseModel):
    """权限更新模型"""
    menu_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    action: Optional[str] = Field(None, max_length=255)

class PermissionInDB(PermissionBase):
    """权限数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PermissionResponse(PermissionInDB):
    """权限响应模型"""
    roles: List["RoleResponse"] = []
    menu: Optional[RoleMenuInfo] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 角色相关模型
class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

class RoleCreate(RoleBase):
    """角色创建模型"""
    pass

class RoleUpdate(BaseModel):
    """角色更新模型"""
    role_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    status: Optional[int] = None

class RoleInDB(RoleBase):
    """角色数据库模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RoleResponse(RoleInDB):
    """角色响应模型"""
    users: List[RoleUserInfo] = []
    menus: List[RoleMenuInfo] = []
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 用于角色分配
class RoleAssignment(BaseModel):
    """角色分配模型"""
    role_ids: List[int] = Field(..., description="角色ID列表")

# 用于权限分配
class PermissionAssignment(BaseModel):
    """权限分配模型"""
    permission_ids: List[int] = Field(..., description="权限ID列表") 