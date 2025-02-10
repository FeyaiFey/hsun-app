from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.crud.base import CRUDBase

class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    """部门CRUD操作类"""
    
    def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        """通过名称获取部门"""
        return db.exec(
            select(Department).where(Department.department_name == name)
        ).first()

    def get_children(self, db: Session, parent_id: Optional[int] = None) -> List[Department]:
        """获取子部门"""
        query = select(Department)
        if parent_id is not None:
            query = query.where(Department.parent_id == parent_id)
        else:
            query = query.where(Department.parent_id.is_(None))
        return db.exec(query).all()

    def get_tree(self, db: Session) -> List[Department]:
        """获取部门树"""
        return self.get_children(db)

    def get_parent_chain(self, db: Session, department_id: int) -> List[Department]:
        """获取父部门链"""
        result = []
        current = self.get(db, department_id)
        
        while current and current.parent_id:
            parent = self.get(db, current.parent_id)
            if parent:
                result.insert(0, parent)
            current = parent
            
        return result

    def get_all_children(self, db: Session, department_id: int) -> List[Department]:
        """获取所有子部门（包括子部门的子部门）"""
        result = []
        children = self.get_children(db, department_id)
        
        for child in children:
            result.append(child)
            result.extend(self.get_all_children(db, child.id))
            
        return result

    def get_department_users(self, db: Session, department_id: int) -> List["User"]:
        """获取部门用户列表"""
        from app.models.user import User
        return db.exec(
            select(User).where(User.department_id == department_id)
        ).all()

    def remove(self, db: Session, *, id: int) -> Department:
        """删除部门（包括子部门）"""
        # 递归删除子部门
        children = self.get_children(db, id)
        for child in children:
            self.remove(db, id=child.id)
            
        return super().remove(db, id=id)

department = CRUDDepartment(Department) 