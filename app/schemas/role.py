from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .menu import MenuResponse
    from .user import UserResponse

# 基础模型
class PermissionBase(BaseModel):
    """权限基础模型"""
    menu_id: int = Field(..., description="菜单ID")
    name: str = Field(..., max_length=255, description="权限名称")
    action: str = Field(..., max_length=50, description="权限动作")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")

class PermissionCreate(PermissionBase):
    """权限创建模型"""
    pass

class PermissionUpdate(BaseModel):
    """权限更新模型"""
    menu_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    action: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class PermissionInDB(PermissionBase):
    """权限数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PermissionResponse(PermissionInDB):
    """权限响应模型"""
    menu: Optional["MenuResponse"] = None

    class Config:
        from_attributes = True

# 角色相关模型
class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., max_length=255, description="角色名称")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

class RoleCreate(RoleBase):
    """角色创建模型"""
    pass

class RoleUpdate(BaseModel):
    """角色更新模型"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    status: Optional[int] = None

class RoleInDB(RoleBase):
    """角色数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleResponse(RoleInDB):
    """角色响应模型"""
    users: List["UserResponse"] = []
    menus: List["MenuResponse"] = []
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

# 用于角色分配
class RoleAssignment(BaseModel):
    """角色分配模型"""
    role_ids: List[int] = Field(..., description="角色ID列表")

# 用于权限分配
class PermissionAssignment(BaseModel):
    """权限分配模型"""
    permission_ids: List[int] = Field(..., description="权限ID列表") 