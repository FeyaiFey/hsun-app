from sqlmodel import Session, select, or_, and_
from fastapi import UploadFile
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import os
import shutil

from app.models.file import File, Folder
from app.schemas.file import FileUpdate, FolderUpdate, FileSearchRequest

class FileCRUD:
    @staticmethod
    async def create_file(
        db: Session,
        file_data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> File:
        """创建文件记录"""
        file = File(**file_data, user_id=user_id)
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    async def get_file(db: Session, file_id: int) -> Optional[File]:
        """通过ID获取文件"""
        return db.exec(select(File).where(
            and_(File.id == file_id, File.is_deleted == False)
        )).first()

    @staticmethod
    async def get_files_by_folder(
        db: Session, 
        folder_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[File]:
        """获取指定文件夹下的所有文件"""
        query = select(File).where(
            and_(
                File.folder_id == folder_id if folder_id is not None else File.folder_id.is_(None),
                File.is_deleted == False
            )
        ).order_by(File.created_at.desc()).offset(skip).limit(limit)
        return db.exec(query).all()

    @staticmethod
    async def search_files(
        db: Session,
        search_params: FileSearchRequest,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """搜索文件"""
        conditions = [File.is_deleted == False]
        
        # 关键词搜索 - 名称和标签
        if search_params.query:
            conditions.append(or_(
                File.name.contains(search_params.query),
                File.original_name.contains(search_params.query),
                File.tags.contains(search_params.query)
            ))
        
        # 文件夹过滤
        if search_params.folder_id is not None:
            conditions.append(File.folder_id == search_params.folder_id)
        
        # 文件类型过滤
        if search_params.file_type:
            conditions.append(File.extension == search_params.file_type.lower())
        
        # 日期范围过滤
        if search_params.date_from:
            conditions.append(File.created_at >= search_params.date_from)
        if search_params.date_to:
            conditions.append(File.created_at <= search_params.date_to)
        
        # 权限过滤 - 只查看自己的或公开的
        if user_id:
            conditions.append(or_(
                File.user_id == user_id,
                File.is_public == True
            ))
            
        query = select(File).where(and_(*conditions)).order_by(File.created_at.desc()).offset(skip).limit(limit)
        return db.exec(query).all()

    @staticmethod
    async def update_file(
        db: Session,
        file_id: int,
        file_update: FileUpdate
    ) -> Optional[File]:
        """更新文件信息"""
        db_file = await FileCRUD.get_file(db, file_id)
        if not db_file:
            return None
            
        update_data = file_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_file, key, value)
            
        setattr(db_file, "updated_at", datetime.now())
        db.commit()
        db.refresh(db_file)
        return db_file

    @staticmethod
    async def delete_file(db: Session, file_id: int) -> bool:
        """软删除文件"""
        db_file = await FileCRUD.get_file(db, file_id)
        if not db_file:
            return False
            
        db_file.is_deleted = True
        db_file.updated_at = datetime.now()
        db.commit()
        return True

    @staticmethod
    async def permanently_delete_file(db: Session, file_id: int, file_storage_path: str) -> bool:
        """永久删除文件（包括存储）"""
        db_file = await FileCRUD.get_file(db, file_id)
        if not db_file:
            return False
            
        # 删除实际文件
        try:
            full_path = os.path.join(file_storage_path, db_file.path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception:
            # 文件删除失败，但仍继续删除数据库记录
            pass
            
        # 删除数据库记录
        db.delete(db_file)
        db.commit()
        return True


class FolderCRUD:
    @staticmethod
    async def create_folder(
        db: Session,
        name: str,
        parent_id: Optional[int] = None,
        user_id: Optional[int] = None,
        is_public: bool = False
    ) -> Folder:
        """创建文件夹"""
        folder = Folder(
            name=name,
            parent_id=parent_id,
            user_id=user_id,
            is_public=is_public
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    async def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
        """通过ID获取文件夹"""
        return db.exec(select(Folder).where(
            and_(Folder.id == folder_id, Folder.is_deleted == False)
        )).first()

    @staticmethod
    async def get_folders(
        db: Session,
        parent_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Folder]:
        """获取文件夹列表"""
        conditions = [Folder.is_deleted == False]
        
        if parent_id is not None:
            conditions.append(Folder.parent_id == parent_id)
        else:
            conditions.append(Folder.parent_id.is_(None))
            
        # 权限过滤 - 只查看自己的或公开的
        if user_id:
            conditions.append(or_(
                Folder.user_id == user_id,
                Folder.is_public == True
            ))
            
        query = select(Folder).where(and_(*conditions)).order_by(Folder.created_at.desc()).offset(skip).limit(limit)
        return db.exec(query).all()

    @staticmethod
    async def update_folder(
        db: Session,
        folder_id: int,
        folder_update: FolderUpdate
    ) -> Optional[Folder]:
        """更新文件夹信息"""
        db_folder = await FolderCRUD.get_folder(db, folder_id)
        if not db_folder:
            return None
            
        update_data = folder_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_folder, key, value)
            
        setattr(db_folder, "updated_at", datetime.now())
        db.commit()
        db.refresh(db_folder)
        return db_folder

    @staticmethod
    async def delete_folder(db: Session, folder_id: int) -> bool:
        """软删除文件夹"""
        db_folder = await FolderCRUD.get_folder(db, folder_id)
        if not db_folder:
            return False
            
        db_folder.is_deleted = True
        db_folder.updated_at = datetime.now()
        db.commit()
        return True

    @staticmethod
    async def get_folder_tree(
        db: Session,
        root_folder_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取文件夹树结构"""
        # 获取所有相关文件夹
        conditions = [Folder.is_deleted == False]
        if user_id:
            conditions.append(or_(
                Folder.user_id == user_id,
                Folder.is_public == True
            ))
            
        all_folders = db.exec(select(Folder).where(and_(*conditions)).order_by(Folder.name)).all()
        
        # 构建文件夹树
        folder_map = {folder.id: {
            "id": folder.id,
            "name": folder.name,
            "is_folder": True,
            "parent_id": folder.parent_id,
            "children": []
        } for folder in all_folders}
        
        # 对于根节点或未指定根节点
        root_nodes = []
        for folder in all_folders:
            if folder.parent_id is None:
                root_nodes.append(folder_map[folder.id])
            elif folder.parent_id in folder_map:
                folder_map[folder.parent_id]["children"].append(folder_map[folder.id])
        
        # 如果指定了根文件夹，则只返回该节点
        if root_folder_id is not None and root_folder_id in folder_map:
            return [folder_map[root_folder_id]]
        
        return root_nodes 