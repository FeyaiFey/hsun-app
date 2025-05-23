from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, BinaryIO, Tuple
import os
import shutil
import uuid
import asyncio
import aiofiles
import mimetypes
from datetime import datetime
import io

from app.core.logger import logger
from app.crud.file import FileCRUD, FolderCRUD
from app.schemas.file import FileUpload, FileResponse, BatchUploadResponse, FolderCreate, FileSearchRequest
from app.models.file import File, Folder

class FileService:
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1].lower().lstrip('.') if '.' in filename else ""
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """获取MIME类型"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """确保目录存在"""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    async def save_upload_file(upload_file: UploadFile, destination_path: str) -> None:
        """保存上传的文件"""
        # 确保目标目录存在
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # 异步保存文件
        async with aiofiles.open(destination_path, 'wb') as out_file:
            # 分块读取和写入
            CHUNK_SIZE = 1024 * 1024  # 1MB 块大小
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                await out_file.write(chunk)

    @staticmethod
    async def process_upload(
        file: UploadFile, 
        db: Session,
        file_data: FileUpload,
        user_id: Optional[int],
        file_storage_path: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """处理单个文件上传"""
        try:
            # 生成唯一文件名
            original_filename = file.filename or "unknown_file"
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            extension = FileService.get_file_extension(original_filename)
            
            # 构建保存路径 - 使用日期+用户ID组织文件
            today = datetime.now().strftime("%Y-%m-%d")
            user_folder = f"user_{user_id}" if user_id else "anonymous"
            relative_path = os.path.join(today, user_folder)
            
            # 确保目录存在
            full_directory = os.path.join(file_storage_path, relative_path)
            FileService.ensure_directory_exists(full_directory)
            
            full_file_path = os.path.join(full_directory, unique_filename)
            relative_file_path = os.path.join(relative_path, unique_filename)
            
            # 保存文件
            await FileService.save_upload_file(file, full_file_path)
            
            # 文件元数据
            file_size = os.path.getsize(full_file_path)
            mime_type = FileService.get_mime_type(original_filename)
            
            # 创建文件记录
            file_db_data = {
                "name": original_filename,
                "original_name": original_filename,
                "extension": extension,
                "mime_type": mime_type,
                "size": file_size,
                "path": relative_file_path,
                "folder_id": file_data.folder_id,
                "is_public": file_data.is_public,
                "tags": file_data.tags
            }
            
            db_file = await FileCRUD.create_file(db, file_db_data, user_id)
            return True, FileResponse.from_orm(db_file).dict()
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            return False, {"filename": file.filename, "error": str(e)}

    @staticmethod
    async def upload_file(
        file: UploadFile,
        db: Session,
        file_data: FileUpload,
        user_id: Optional[int],
        file_storage_path: str
    ) -> FileResponse:
        """上传单个文件"""
        success, result = await FileService.process_upload(file, db, file_data, user_id, file_storage_path)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {result.get('error', '未知错误')}"
            )
        
        return FileResponse(**result)

    @staticmethod
    async def upload_files_batch(
        files: List[UploadFile],
        db: Session,
        file_data: FileUpload,
        user_id: Optional[int],
        file_storage_path: str
    ) -> BatchUploadResponse:
        """批量上传文件"""
        tasks = []
        for file in files:
            # 为每个文件创建上传任务
            tasks.append(FileService.process_upload(
                file, db, file_data, user_id, file_storage_path
            ))
            
        # 异步执行所有任务
        results = await asyncio.gather(*tasks)
        
        response = BatchUploadResponse()
        
        # 处理结果
        for success, result in results:
            if success:
                response.success.append(FileResponse(**result))
            else:
                response.failed.append(result)
                
        return response

    @staticmethod
    async def get_file_content(
        db: Session,
        file_id: int,
        file_storage_path: str
    ) -> Tuple[BinaryIO, str, int]:
        """获取文件内容用于预览"""
        # 获取文件记录
        db_file = await FileCRUD.get_file(db, file_id)
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        # 构建文件完整路径
        full_path = os.path.join(file_storage_path, db_file.path)
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在于存储系统中"
            )
            
        # 打开文件
        try:
            # 返回文件对象、MIME类型和文件大小
            return open(full_path, "rb"), db_file.mime_type, db_file.size
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="读取文件失败"
            )

    @staticmethod
    async def create_folder(
        db: Session,
        folder_data: FolderCreate,
        user_id: Optional[int]
    ) -> Folder:
        """创建文件夹"""
        # 如果指定了父文件夹，检查是否存在
        if folder_data.parent_id:
            parent_folder = await FolderCRUD.get_folder(db, folder_data.parent_id)
            if not parent_folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父文件夹不存在"
                )
                
        # 创建文件夹
        return await FolderCRUD.create_folder(
            db, 
            name=folder_data.name,
            parent_id=folder_data.parent_id,
            user_id=user_id,
            is_public=folder_data.is_public
        )

    @staticmethod
    async def get_folder_tree(
        db: Session,
        root_folder_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取文件夹树结构"""
        return await FolderCRUD.get_folder_tree(db, root_folder_id, user_id)

    @staticmethod
    async def search_files(
        db: Session,
        search_params: FileSearchRequest,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """搜索文件"""
        return await FileCRUD.search_files(db, search_params, user_id, skip, limit) 