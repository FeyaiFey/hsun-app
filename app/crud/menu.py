from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate
from app.crud.base import CRUDBase

class CRUDMenu(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    """菜单CRUD操作类"""

    def get_all_menus(self, db: Session) -> Optional[Menu]:
        return db.exec(select(Menu)).all()

    def get_by_name(self, db: Session, name: str) -> Optional[Menu]:
        """通过名称获取菜单"""
        return db.exec(select(Menu).where(Menu.name == name)).first()

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
            select(RolePermission)
            .join(Menu, RolePermission.menu_id == Menu.id)
            .where(RolePermission.role_id == role_id)
            .distinct()
        )
        return db.exec(query.order_by(Menu.menu_order)).all()

    def remove(self, db: Session, *, id: int) -> Menu:
        """删除菜单（包括子菜单）"""
        # 递归删除子菜单
        children = self.get_children(db, id)
        for child in children:
            self.remove(db, id=child.id)
            
        return super().remove(db, id=id)

    def create(self, db: Session, *, obj_in: MenuCreate) -> Menu:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Menu(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Menu, obj_in: Union[MenuUpdate, Dict[str, Any]]
    ) -> Menu:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Menu:
        obj = db.query(Menu).get(id)
        # 删除子菜单
        children = db.query(Menu).filter(Menu.parent_id == id).all()
        for child in children:
            db.delete(child)
        db.delete(obj)
        db.commit()
        return obj

menu = CRUDMenu(Menu) 