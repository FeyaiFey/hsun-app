from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field

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