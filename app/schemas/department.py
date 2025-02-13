from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# 部门的数据库模型
class DepartmentInDB(BaseModel):
    """部门数据库模型"""
    id: int = Field(..., description="部门ID")
    department_name: str = Field(..., description="部门名称")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    status: int = Field(..., description="状态：1-启用，0-禁用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="创建时间")

# 前端部门列表
class DepartmentItem(BaseModel):
    """部门项模型"""
    id: str = Field(..., description="部门ID")
    department_name: str = Field(..., description="部门名称")
    children: Optional[List["DepartmentItem"]] = Field(default=None, description="子部门列表")

class DepartmentListResponse(BaseModel):
    """部门列表响应模型"""
    list: List[DepartmentItem] = Field(..., description="部门列表")

    class Config:
        json_schema_extra = {
            "example": {
                "list": [
                    {
                        "id": "1",
                        "department_name": "技术部",
                        "children": [
                            {
                                "id": "2",
                                "department_name": "开发组"
                            }
                        ]
                    }
                ]
            }
        }

# 注册时部门模型-自用
class DepartmentRegister(BaseModel):
    """注册时部门模型"""
    label: str = Field(..., description="名称")
    value: int = Field(..., description="部门id")

# 部门树节点模型-自用
class DepartmentTreeNode(BaseModel):
    """部门树节点模型"""
    label: str = Field(..., description="部门名称")
    value: int = Field(..., description="部门ID")
    parentId: Optional[int] = Field(None, description="父部门ID")
    children: Optional[List["DepartmentTreeNode"]] = Field(default=[], description="子部门")

# 适配前端树模型列表
class DepartmentList(BaseModel):
    """部门树模型列表"""
    id: int = Field(..., description="部门ID")
    pid: Optional[int] = Field(None, description="父部门ID")
    department_name: str = Field(..., description="部门名称")
    status: int = Field(..., description="状态：1-启用，0-禁用")
    created_at: datetime = Field(..., description="创建时间")
    

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