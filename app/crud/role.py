from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from app.models.user import UserRole
from app.models.role import Role, Permission, RolePermission
from app.schemas.role import RoleCreate, RoleUpdate, RoleItem, UpdateRoleRequest

class CRUDRole:
    """角色CRUD操作类"""
    def __init__(self, model: Role):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[Role]:
        """根据ID获取记录"""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[Role]:
        """获取多条记录"""
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        return db.exec(query.offset(skip).limit(limit)).all()

    def create(self, db: Session, *, obj_in: RoleCreate) -> Role:
        """创建记录"""
        db_obj = Role(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Role,
        obj_in: Union[RoleUpdate, Dict[str, Any]]
    ) -> Role:
        """更新记录"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Role:
        """删除记录"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: Any) -> bool:
        """检查记录是否存在"""
        obj = db.get(self.model, id)
        return obj is not None

    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """获取用户角色列表"""
        # 通过 join 查询获取用户角色信息
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(Role.status == 1)  # 只获取启用状态的角色
        )
        return db.exec(statement).all()
    
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
    
    def assign_default_role(
        self, db: Session, *, user_id: int
    ) -> Optional[Role]:
        """分配默认角色"""
        default_role = UserRole(
            user_id=user_id,
            role_id=2
        )
        db.add(default_role)
        db.commit()
        db.refresh(default_role)
        return default_role

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

    def get_all_roles(self, db: Session) -> List[RoleItem]:
        """获取所有角色列表
        
        Args:
            db: 数据库会话
            
        Returns:
            List[RoleItem]: 角色列表
        """
        query = select(Role).where(Role.status == 1)  # 只获取启用状态的角色
        roles = db.exec(query).all()
        return [
            RoleItem(
                id=role.id,
                role_name=role.role_name
            ) for role in roles
        ]

    def update_user_roles(
        self,
        db: Session,
        *,
        request: UpdateRoleRequest
    ) -> bool:
        """更新用户角色
        
        Args:
            db: 数据库会话
            request: 更新请求
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 开始事务
            for user_id in request.id:
                # 删除原有角色
                statement = select(UserRole).where(UserRole.user_id == user_id)
                user_roles = db.exec(statement).all()
                for user_role in user_roles:
                    db.delete(user_role)
                
                # 添加新角色
                for role_id in request.role_id:
                    user_role = UserRole(
                        user_id=user_id,
                        role_id=int(role_id),
                        status=request.status
                    )
                    db.add(user_role)
            
            # 提交事务
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e

    def get_user_role_list(
        self,
        db: Session,
        user_id: int
    ) -> List[UserRole]:
        """获取用户角色列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[UserRole]: 用户角色列表
        """
        statement = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.status == 1
        )
        return db.exec(statement).all()

class CRUDPermission:
    """权限CRUD操作类"""
    
    def __init__(self, model: Permission):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[Permission]:
        """根据ID获取记录"""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[Permission]:
        """获取多条记录"""
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        return db.exec(query.offset(skip).limit(limit)).all()

    def create(self, db: Session, *, obj_in: dict) -> Permission:
        """创建记录"""
        db_obj = Permission(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Permission,
        obj_in: dict
    ) -> Permission:
        """更新记录"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Permission:
        """删除记录"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: Any) -> bool:
        """检查记录是否存在"""
        obj = db.get(self.model, id)
        return obj is not None
    
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