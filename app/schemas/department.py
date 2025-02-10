from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# 注册时部门模型
class DepartmentRegister(BaseModel):
    """注册时部门模型"""
    label: str = Field(..., description="名称")
    value: int = Field(..., description="部门id")

# 部门树节点模型
class DepartmentTreeNode(BaseModel):
    """部门树节点模型"""
    label: str = Field(..., description="部门名称")
    value: int = Field(..., description="部门ID")
    parentId: Optional[int] = Field(None, description="父部门ID")
    children: Optional[List["DepartmentTreeNode"]] = Field(default=[], description="子部门")

# 基础模型
class DepartmentBase(BaseModel):
    """部门基础模型"""
    department_name: str = Field(..., max_length=100, description="部门名称")
    parent_id: Optional[int] = Field(default=None, description="父部门ID")
    status: Optional[int] = Field(default=1, description="状态：1-启用，0-禁用")

# 创建请求模型
class DepartmentCreate(DepartmentBase):
    """部门创建模型"""
    pass

# 更新请求模型
class DepartmentUpdate(BaseModel):
    """部门更新模型"""
    department_name: Optional[str] = Field(None, max_length=100, description="部门名称")
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

# 用户简单信息
class DepartmentUserInfo(BaseModel):
    """用户简单信息"""
    id: int
    username: str
    email: Optional[str] = None
    status: int

# 响应模型
class DepartmentResponse(DepartmentInDB):
    """部门响应模型"""
    children: List["DepartmentResponse"] = []
    parent: Optional["DepartmentResponse"] = None
    users: List[DepartmentUserInfo] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 