from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

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

class RoleItem(BaseModel):
    """角色列表项模型"""
    id: int
    role_name: str

# 添加更新用户角色的请求模型
class UpdateRoleRequest(BaseModel):
    """更新用户角色请求模型"""
    id: List[int] = Field(..., description="用户ID列表")
    role_id: List[int] = Field(..., description="角色ID列表")
    status: int = Field(..., description="状态：1-启用，0-禁用")
