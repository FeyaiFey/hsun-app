from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile

# 基础文件夹模型
class FolderBase(BaseModel):
    name: str = Field(..., description="文件夹名称")
    parent_id: Optional[int] = Field(None, description="父文件夹ID")
    is_public: bool = Field(False, description="是否公开")

# 创建文件夹请求
class FolderCreate(FolderBase):
    pass

# 更新文件夹请求
class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, description="文件夹名称")
    parent_id: Optional[int] = Field(None, description="父文件夹ID")
    is_public: Optional[bool] = Field(None, description="是否公开")

# 文件夹响应模型
class FolderResponse(FolderBase):
    id: int
    user_id: Optional[int] = Field(None, description="创建用户ID")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 基础文件模型
class FileBase(BaseModel):
    name: str = Field(..., description="文件名")
    folder_id: Optional[int] = Field(None, description="所属文件夹ID")
    is_public: bool = Field(False, description="是否公开")
    tags: Optional[str] = Field(None, description="标签，以逗号分隔")

# 文件上传请求
class FileUpload(BaseModel):
    folder_id: Optional[int] = Field(None, description="所属文件夹ID")
    is_public: bool = Field(False, description="是否公开")
    tags: Optional[str] = Field(None, description="标签，以逗号分隔")

# 更新文件请求
class FileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="文件名")
    folder_id: Optional[int] = Field(None, description="所属文件夹ID")
    is_public: Optional[bool] = Field(None, description="是否公开")
    tags: Optional[str] = Field(None, description="标签，以逗号分隔")

# 文件响应模型
class FileResponse(FileBase):
    id: int
    original_name: str = Field(..., description="原始文件名")
    extension: str = Field(..., description="文件扩展名")
    mime_type: str = Field(..., description="MIME类型")
    size: int = Field(..., description="文件大小(字节)")
    path: str = Field(..., description="文件存储路径")
    user_id: Optional[int] = Field(None, description="上传用户ID")
    is_folder: bool = Field(False, description="是否是文件夹")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 文件树节点
class FileTreeNode(BaseModel):
    id: int
    name: str
    is_folder: bool
    parent_id: Optional[int] = None
    children: List["FileTreeNode"] = []
    
    class Config:
        from_attributes = True

# 批量上传响应
class BatchUploadResponse(BaseModel):
    success: List[FileResponse] = []
    failed: List[Dict[str, Any]] = []

# 文件搜索请求
class FileSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    folder_id: Optional[int] = Field(None, description="在指定文件夹中搜索")
    file_type: Optional[str] = Field(None, description="文件类型过滤")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")

# 重循环引用
FileTreeNode.update_forward_refs() 