from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .role import RoleResponse, PermissionResponse
    from .user import UserResponse

# 基础模型
class MenuBase(BaseModel):
    """菜单基础模型"""
    parent_id: Optional[int] = Field(default=None, description="父菜单ID")
    path: str = Field(..., max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    name: str = Field(..., max_length=100, description="路由名称")
    title: str = Field(..., max_length=255, description="菜单标题")
    icon: Optional[str] = Field(None, max_length=255, description="图标")
    always_show: Optional[bool] = Field(False, description="是否总是显示")
    no_cache: Optional[bool] = Field(False, description="是否不缓存")
    affix: Optional[bool] = Field(False, description="是否固定")
    hidden: Optional[bool] = Field(False, description="是否隐藏")
    external_link: Optional[str] = Field(None, max_length=255, description="外部链接")
    permission: Optional[str] = Field(None, description="权限标识")
    menu_order: Optional[int] = Field(0, description="排序")

class MenuCreate(MenuBase):
    """菜单创建模型"""
    pass

class MenuUpdate(BaseModel):
    """菜单更新模型"""
    parent_id: Optional[int] = None
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    redirect: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=255)
    always_show: Optional[bool] = None
    no_cache: Optional[bool] = None
    affix: Optional[bool] = None
    hidden: Optional[bool] = None
    external_link: Optional[str] = Field(None, max_length=255)
    permission: Optional[str] = None
    menu_order: Optional[int] = None

class MenuInDB(MenuBase):
    """菜单数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuResponse(MenuInDB):
    """菜单响应模型"""
    children: List["MenuResponse"] = []
    permissions: List["PermissionResponse"] = []
    roles: List["RoleResponse"] = []

    class Config:
        from_attributes = True

# 部门相关模型
class DepartmentBase(BaseModel):
    """部门基础模型"""
    name: str = Field(..., max_length=50, description="部门名称")
    parent_id: Optional[int] = Field(default=None, description="父部门ID")
    description: Optional[str] = Field(None, max_length=200, description="部门描述")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

class DepartmentCreate(DepartmentBase):
    """部门创建模型"""
    pass

class DepartmentUpdate(BaseModel):
    """部门更新模型"""
    name: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=200)
    status: Optional[int] = None

class DepartmentInDB(DepartmentBase):
    """部门数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DepartmentResponse(DepartmentInDB):
    """部门响应模型"""
    children: List["DepartmentResponse"] = []
    parent: Optional["DepartmentResponse"] = None
    users: List["UserResponse"] = []

    class Config:
        from_attributes = True 