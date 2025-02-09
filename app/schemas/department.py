from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# 基础模型
class DepartmentBase(BaseModel):
    """部门基础模型"""
    department_name: str = Field(..., description="部门名称")
    parent_id: Optional[int] = Field(default=None, description="父部门ID")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

# 创建请求模型
class DepartmentCreate(DepartmentBase):
    """部门创建模型"""
    pass

# 更新请求模型
class DepartmentUpdate(BaseModel):
    """部门更新模型"""
    department_name: Optional[str] = Field(None, description="部门名称")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    status: Optional[int] = Field(None, description="状态：1-启用，0-禁用")

# 数据库模型
class DepartmentInDB(DepartmentBase):
    """部门数据库模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 响应模型
class DepartmentResponse(DepartmentInDB):
    """部门响应模型"""
    children: List["DepartmentResponse"] = []
    parent: Optional["DepartmentResponse"] = None

    class Config:
        from_attributes = True

# 解决循环引用
DepartmentResponse.model_rebuild() 