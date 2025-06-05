from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Path as PathParam, BackgroundTasks
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse as FastAPIFileResponse
from sqlmodel import Session
import json
import os
from pathlib import Path as PathLib
import urllib.parse

from app.db.session import get_db
from app.core.config import settings
from app.models.file import File as FileModel, Folder
from app.schemas.file import (
    FileResponse, FolderResponse, FileUpdate, FolderUpdate,
    FolderCreate, FileUpload, BatchUploadResponse, FileSearchRequest, FileTreeNode
)
from app.schemas.response import IResponse
from app.services.file_service import FileService
from app.crud.file import FileCRUD, FolderCRUD
from app.api.v1.endpoints.auth import get_current_user, get_current_active_user
from app.models.user import User
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

router = APIRouter()

# 文件存储根路径
FILE_STORAGE_PATH = PathLib("uploads")

@router.post("/folders/", response_model=IResponse[FolderResponse])
@monitor_request
async def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新文件夹"""
    try:
        folder = await FileService.create_folder(db, folder_data, current_user.id)
        return CustomResponse.success(data=folder, message="文件夹创建成功")
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="FolderCreateError"
        )
    except Exception as e:
        logger.error(f"创建文件夹失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/folders/", response_model=IResponse[List[FolderResponse]])
@monitor_request
async def list_folders(
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定父文件夹下的所有子文件夹"""
    try:
        folders = await FolderCRUD.get_folders(db, parent_id, current_user.id, skip, limit)
        return CustomResponse.success(data=folders, message="获取文件夹列表成功")
    except Exception as e:
        logger.error(f"获取文件夹列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/folders/{folder_id}", response_model=IResponse[FolderResponse])
@monitor_request
async def get_folder(
    folder_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件夹详情"""
    try:
        folder = await FolderCRUD.get_folder(db, folder_id)
        if not folder:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件夹不存在",
                name="FolderNotFound"
            )
        
        # 检查权限
        if not folder.is_public and folder.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权访问该文件夹",
                name="PermissionDenied"
            )
        
        return CustomResponse.success(data=folder, message="获取文件夹详情成功")
    except Exception as e:
        logger.error(f"获取文件夹详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/folders/{folder_id}", response_model=IResponse[FolderResponse])
@monitor_request
async def update_folder(
    folder_update: FolderUpdate,
    folder_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新文件夹信息"""
    try:
        folder = await FolderCRUD.get_folder(db, folder_id)
        if not folder:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件夹不存在",
                name="FolderNotFound"
            )
        
        # 检查权限
        if folder.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权修改该文件夹",
                name="PermissionDenied"
            )
        
        updated_folder = await FolderCRUD.update_folder(db, folder_id, folder_update)
        return CustomResponse.success(data=updated_folder, message="文件夹更新成功")
    except Exception as e:
        logger.error(f"更新文件夹失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.delete("/folders/{folder_id}", response_model=IResponse)
@monitor_request
async def delete_folder(
    folder_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文件夹"""
    try:
        folder = await FolderCRUD.get_folder(db, folder_id)
        if not folder:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件夹不存在",
                name="FolderNotFound"
            )
        
        # 检查权限
        if folder.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权删除该文件夹",
                name="PermissionDenied"
            )
        
        await FolderCRUD.delete_folder(db, folder_id)
        return CustomResponse.success(message="文件夹删除成功")
    except Exception as e:
        logger.error(f"删除文件夹失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/folders/tree/", response_model=IResponse[List[Dict[str, Any]]])
@monitor_request
async def get_folder_tree(
    root_folder_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件夹树结构"""
    try:
        tree = await FileService.get_folder_tree(db, root_folder_id, current_user.id)
        return CustomResponse.success(data=tree, message="获取文件夹树成功")
    except Exception as e:
        logger.error(f"获取文件夹树失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/upload/", response_model=IResponse[FileResponse])
@monitor_request
async def upload_file(
    file: UploadFile = File(...),
    folder_id: Optional[int] = Form(None),
    is_public: bool = Form(False),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传单个文件"""
    try:
        file_data = FileUpload(
            folder_id=folder_id,
            is_public=is_public,
            tags=tags
        )
        uploaded_file = await FileService.upload_file(
            file,
            db,
            file_data,
            current_user.id,
            FILE_STORAGE_PATH
        )
        return CustomResponse.success(data=uploaded_file, message="文件上传成功")
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="FileUploadError"
        )
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/upload/batch/", response_model=IResponse[BatchUploadResponse])
@monitor_request
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    folder_id: Optional[int] = Form(None),
    is_public: bool = Form(False),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量上传文件"""
    try:
        file_data = FileUpload(
            folder_id=folder_id,
            is_public=is_public,
            tags=tags
        )
        result = await FileService.upload_files_batch(
            files,
            db,
            file_data,
            current_user.id,
            FILE_STORAGE_PATH
        )
        return CustomResponse.success(data=result, message="批量上传完成")
    except Exception as e:
        logger.error(f"批量上传失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/files/", response_model=IResponse[List[FileResponse]])
@monitor_request
async def list_files(
    folder_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定文件夹下的所有文件"""
    try:
        files = await FileCRUD.get_files_by_folder(db, folder_id, skip, limit)
        return CustomResponse.success(data=files, message="获取文件列表成功")
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/files/{file_id}", response_model=IResponse[FileResponse])
@monitor_request
async def get_file_info(
    file_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件详情"""
    try:
        file = await FileCRUD.get_file(db, file_id)
        if not file:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在",
                name="FileNotFound"
            )
        
        # 检查权限
        if not file.is_public and file.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权访问该文件",
                name="PermissionDenied"
            )
        
        return CustomResponse.success(data=file, message="获取文件详情成功")
    except Exception as e:
        logger.error(f"获取文件详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/files/{file_id}", response_model=IResponse[FileResponse])
@monitor_request
async def update_file(
    file_update: FileUpdate,
    file_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新文件信息"""
    try:
        file = await FileCRUD.get_file(db, file_id)
        if not file:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在",
                name="FileNotFound"
            )
        
        # 检查权限
        if file.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权修改该文件",
                name="PermissionDenied"
            )
        
        updated_file = await FileCRUD.update_file(db, file_id, file_update)
        return CustomResponse.success(data=updated_file, message="文件信息更新成功")
    except Exception as e:
        logger.error(f"更新文件信息失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.delete("/files/{file_id}", response_model=IResponse)
@monitor_request
async def delete_file(
    file_id: int = PathParam(...),
    permanent: bool = Query(False, description="是否永久删除"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文件"""
    try:
        file = await FileCRUD.get_file(db, file_id)
        if not file:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在",
                name="FileNotFound"
            )
        
        # 检查权限
        if file.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权删除该文件",
                name="PermissionDenied"
            )
        
        if permanent:
            result = await FileCRUD.permanently_delete_file(db, file_id, FILE_STORAGE_PATH)
        else:
            result = await FileCRUD.delete_file(db, file_id)
            
        if not result:
            return CustomResponse.error(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="删除文件失败",
                name="DeleteFileError"
            )
        
        message = "文件永久删除成功" if permanent else "文件删除成功"
        return CustomResponse.success(message=message)
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/files/{file_id}/download")
@monitor_request
async def download_file(
    file_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载文件"""
    try:
        file = await FileCRUD.get_file(db, file_id)
        if not file:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在",
                name="FileNotFound"
            )
        
        # 检查权限
        if not file.is_public and file.user_id != current_user.id:
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权下载该文件",
                name="PermissionDenied"
            )
        
        file_path = os.path.join(FILE_STORAGE_PATH, file.path)
        if not os.path.exists(file_path):
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在于存储系统中",
                name="FileNotFoundInStorage"
            )
        
        return FastAPIFileResponse(
            path=file_path,
            filename=file.original_name,
            media_type=file.mime_type
        )
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/files/{file_id}/preview")
@monitor_request
async def preview_file(
    file_id: int = PathParam(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """预览文件内容"""
    try:
        file = await FileCRUD.get_file(db, file_id)
        if not file:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="文件不存在",
                name="FileNotFound"
            )
        
        # 检查权限
        if not (current_user.department_id == 1 or current_user.department_id == 2):
            return CustomResponse.error(
                code=status.HTTP_403_FORBIDDEN,
                message="无权预览该文件",
                name="PermissionDenied"
            )
        
        # 获取文件内容
        file_content, mime_type, content_size = await FileService.get_file_content(db, file_id, FILE_STORAGE_PATH)
        
        # 安全处理文件名编码 - 避免中文字符导致的编码错误
        safe_filename = urllib.parse.quote(file.original_name.encode('utf-8'))
        
        # 设置响应头 - 使用安全的文件名编码
        headers = {
            "Content-Disposition": f"inline; filename*=UTF-8''{safe_filename}",
            "Content-Length": str(content_size)
        }
        
        # 创建迭代器函数来安全地读取文件内容
        def iter_file():
            try:
                CHUNK_SIZE = 1024 * 64  # 64KB chunks
                while True:
                    chunk = file_content.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk
            finally:
                file_content.close()
        
        # 创建流式响应
        return StreamingResponse(
            iter_file(),
            media_type=mime_type,
            headers=headers
        )
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="FilePreviewError"
        )
    except Exception as e:
        logger.error(f"预览文件失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/files/search/", response_model=IResponse[List[FileResponse]])
@monitor_request
async def search_files(
    search_params: FileSearchRequest,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索文件"""
    try:
        files = await FileService.search_files(db, search_params, current_user.id, skip, limit)
        return CustomResponse.success(data=files, message="文件搜索完成")
    except Exception as e:
        logger.error(f"搜索文件失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )