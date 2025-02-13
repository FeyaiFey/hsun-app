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