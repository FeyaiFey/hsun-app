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

# 匹配前端部门列表
class DepartmentItem(BaseModel):
    """部门项模型"""
    id: str = Field(..., description="部门ID")
    department_name: str = Field(..., description="部门名称")
    children: Optional[List["DepartmentItem"]] = Field(default=None, description="子部门列表")

# 匹配前端部门列表响应
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

# 适配前端树模型列表
class DepartmentList(BaseModel):
    """部门树模型列表"""
    id: int = Field(..., description="部门ID")
    pid: Optional[int] = Field(None, description="父部门ID")
    department_name: str = Field(..., description="部门名称")
    status: int = Field(..., description="状态：1-启用，0-禁用")
    created_at: str = Field(..., description="创建时间")

class DepartmentTableListResponse(BaseModel):
    """部门表格列表响应模型"""
    list: List[DepartmentList] = Field(..., description="部门列表数据")
    total: int = Field(..., description="总记录数")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 1,
                        "pid": None,
                        "department_name": "技术部",
                        "status": 1,
                        "created_at": "2024-02-13 18:05:28"
                    }
                ],
                "total": 1
            }
        }