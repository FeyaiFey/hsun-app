from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field

class RouteMetaCustom(BaseModel):
    title: str = Field(..., max_length=255, description="菜单标题")
    icon: Optional[str] = Field(None, max_length=255, description="图标")
    always_show: Optional[bool] = Field(default=False, description="是否总是显示")
    no_cache: Optional[bool] = Field(default=False, description="是否不缓存")
    affix: Optional[bool] = Field(default=False, description="是否固定")
    hidden: Optional[bool] = Field(default=False, description="是否隐藏")
    permission: Optional[List[str]] = Field(None, description="权限标识")

# 定义 Component 类型
Component = Union[str, dict]

class AppRouteRecordRaw(BaseModel):
    path: str = Field(..., max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    name: str = Field(..., max_length=100, description="路由名称")
    meta: RouteMetaCustom

class AppCustomRouteRecordRaw(BaseModel):
    path: str = Field(..., max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    name: str = Field(..., max_length=100, description="路由名称")
    meta: RouteMetaCustom
    children: Optional[List['AppCustomRouteRecordRaw']] = Field(default=[], description="子路由列表")



# 简单权限信息
class MenuPermissionInfo(BaseModel):
    """权限简单信息"""
    id: int
    name: str
    action: str

# 简单角色信息
class MenuRoleInfo(BaseModel):
    """角色简单信息"""
    id: int
    role_name: str
    status: int

# 菜单相关模型
class MenuBase(BaseModel):
    """菜单基础模型"""
    path: str = Field(..., max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    name: str = Field(..., max_length=100, description="路由名称")
    title: str = Field(..., max_length=255, description="菜单标题")
    icon: Optional[str] = Field(None, max_length=255, description="图标")
    parent_id: Optional[int] = Field(default=None, description="父菜单ID")
    always_show: Optional[bool] = Field(default=False, description="是否总是显示")
    no_cache: Optional[bool] = Field(default=False, description="是否不缓存")
    affix: Optional[bool] = Field(default=False, description="是否固定")
    hidden: Optional[bool] = Field(default=False, description="是否隐藏")
    external_link: Optional[str] = Field(None, max_length=255, description="外部链接")
    permission: Optional[str] = Field(None, description="权限标识")
    menu_order: Optional[int] = Field(default=0, description="排序")

class MenuCreate(MenuBase):
    """菜单创建模型"""
    pass

class MenuUpdate(BaseModel):
    """菜单更新模型"""
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    redirect: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[int] = None
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
    parent: Optional["MenuResponse"] = None
    permissions: List[MenuPermissionInfo] = []
    roles: List[MenuRoleInfo] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 