from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, Integer, BigInteger, ForeignKey
from sqlalchemy.sql import func

class File(SQLModel, table=True):
    """文件模型"""
    __tablename__ = "huaxinAdmin_files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="文件名"
    )
    original_name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="原始文件名"
    )
    extension: str = Field(
        sa_column=Column(String(50)),
        description="文件扩展名"
    )
    mime_type: str = Field(
        sa_column=Column(String(100)),
        description="MIME类型"
    )
    size: int = Field(
        sa_column=Column(BigInteger),
        description="文件大小(字节)"
    )
    path: str = Field(
        sa_column=Column(String(500)),
        description="文件存储路径"
    )
    folder_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("huaxinAdmin_folders.id", ondelete="SET NULL")),
        default=None,
        description="所属文件夹ID"
    )
    user_id: Optional[int] = Field(
        default=None,
        description="上传用户ID"
    )
    is_folder: bool = Field(
        default=False,
        description="是否是文件夹"
    )
    is_public: bool = Field(
        default=False,
        description="是否公开"
    )
    is_deleted: bool = Field(
        default=False,
        description="是否已删除"
    )
    tags: Optional[str] = Field(
        sa_column=Column(String(255)),
        default=None,
        description="标签，以逗号分隔"
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="创建时间"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="更新时间"
    )

class Folder(SQLModel, table=True):
    """文件夹模型"""
    __tablename__ = "huaxinAdmin_folders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="文件夹名称"
    )
    parent_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("huaxinAdmin_folders.id", ondelete="SET NULL")),
        default=None,
        description="父文件夹ID"
    )
    user_id: Optional[int] = Field(
        default=None,
        description="创建用户ID"
    )
    is_public: bool = Field(
        default=False,
        description="是否公开"
    )
    is_deleted: bool = Field(
        default=False,
        description="是否已删除"
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="创建时间"
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.sysdatetime(),
            nullable=True
        ),
        description="更新时间"
    ) 