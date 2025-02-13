from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate

class CRUDMenu:
    """菜单CRUD操作类"""
    
    def __init__(self, model: Menu):
        self.model = model

    def get_user_menus(self, db: Session, user_id: int) -> List[Menu]:
        """获取用户菜单列表"""
        from app.models.user import UserRole
        from app.models.role import RolePermission

        # 获取用户角色的菜单
        user_first_role = db.exec(select(UserRole).where(UserRole.user_id == user_id).limit(1)).first()
        if user_first_role:
            role_id = user_first_role.role_id
        else:
            role_id = 2
        query = (
            select(Menu)
            .join(RolePermission, RolePermission.menu_id == Menu.id)
            .where(RolePermission.role_id == role_id)
            .distinct()
        )
        return db.exec(query.order_by(Menu.menu_order)).all()

    def get(self, db: Session, id: Any) -> Optional[Menu]:
        """根据ID获取记录"""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[Menu]:
        """获取多条记录"""
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        return db.exec(query.offset(skip).limit(limit)).all()

    def create(self, db: Session, *, obj_in: MenuCreate) -> Menu:
        """创建记录"""
        db_obj = Menu(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Menu,
        obj_in: MenuUpdate
    ) -> Menu:
        """更新记录"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Menu:
        """删除记录"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: Any) -> bool:
        """检查记录是否存在"""
        obj = db.get(self.model, id)
        return obj is not None

    def get_by_name(self, db: Session, name: str) -> Optional[Menu]:
        """通过名称获取菜单"""
        return db.exec(select(Menu).where(Menu.name == name)).first()

    def get_all_menus(self, db: Session) -> List[Menu]:
        """获取所有菜单"""
        return db.exec(select(Menu).order_by(Menu.id)).all()

    

menu = CRUDMenu(Menu) 