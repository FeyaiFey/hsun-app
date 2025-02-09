from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from app.models.role import Role, Permission, RolePermission
from app.schemas.role import RoleCreate, RoleUpdate
from app.crud.base import CRUDBase

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    """角色CRUD操作类"""
    
    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """通过名称获取角色"""
        return db.exec(select(Role).where(Role.role_name == name)).first()

    def get_role_permissions(self, db: Session, role_id: int) -> List[Permission]:
        """获取角色权限列表"""
        role = self.get(db, role_id)
        return role.permissions if role else []

    def assign_permissions(
        self, db: Session, *, role_id: int, permission_ids: List[int]
    ) -> Optional[Role]:
        """分配角色权限"""
        role = self.get(db, role_id)
        if not role:
            return None
            
        # 清除现有权限
        role.permissions = []
        db.commit()
        
        # 添加新权限
        permissions = db.exec(
            select(Permission).where(Permission.id.in_(permission_ids))
        ).all()
        role.permissions.extend(permissions)
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """获取用户角色列表"""
        from app.models.user import User
        user = db.get(User, user_id)
        return user.roles if user else []

    def assign_users(
        self, db: Session, *, role_id: int, user_ids: List[int]
    ) -> Optional[Role]:
        """分配角色给用户"""
        role = self.get(db, role_id)
        if not role:
            return None
            
        from app.models.user import User
        users = db.exec(select(User).where(User.id.in_(user_ids))).all()
        role.users.extend(users)
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def remove_users(
        self, db: Session, *, role_id: int, user_ids: List[int]
    ) -> Optional[Role]:
        """移除用户角色"""
        role = self.get(db, role_id)
        if not role:
            return None
            
        role.users = [user for user in role.users if user.id not in user_ids]
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

class CRUDPermission(CRUDBase[Permission, Any, Any]):
    """权限CRUD操作类"""
    
    def get_by_action(self, db: Session, action: str) -> Optional[Permission]:
        """通过动作获取权限"""
        return db.exec(
            select(Permission).where(Permission.action == action)
        ).first()

    def get_menu_permissions(self, db: Session, menu_id: int) -> List[Permission]:
        """获取菜单权限列表"""
        return db.exec(
            select(Permission).where(Permission.menu_id == menu_id)
        ).all()

role = CRUDRole(Role)
permission = CRUDPermission(Permission) 