from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from app.models.user import User, UserAvatar
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户CRUD操作类"""
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return db.exec(select(User).where(User.email == email)).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.exec(select(User).where(User.username == username)).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建新用户"""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            department_id=obj_in.department_id,
            status=obj_in.status,
            password_hash=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """更新用户信息"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password_hash"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_user_avatars(self, db: Session, user_id: int) -> List[UserAvatar]:
        """获取用户头像列表"""
        return db.exec(
            select(UserAvatar)
            .where(UserAvatar.user_id == user_id)
            .order_by(UserAvatar.created_at.desc())
        ).all()

    def get_active_avatar(self, db: Session, user_id: int) -> Optional[UserAvatar]:
        """获取用户当前头像"""
        return db.exec(
            select(UserAvatar)
            .where(UserAvatar.user_id == user_id, UserAvatar.is_active == True)
        ).first()

    def create_user_avatar(
        self, db: Session, *, user_id: int, avatar_url: str
    ) -> UserAvatar:
        """创建用户头像"""
        # 将当前头像设置为非活动
        current_avatars = db.exec(
            select(UserAvatar)
            .where(UserAvatar.user_id == user_id, UserAvatar.is_active == True)
        ).all()
        
        for avatar in current_avatars:
            avatar.is_active = False
            db.add(avatar)
        
        # 创建新头像
        avatar = UserAvatar(
            user_id=user_id,
            avatar_url=avatar_url,
            is_active=True
        )
        db.add(avatar)
        db.commit()
        db.refresh(avatar)
        return avatar

    def update_last_login(self, db: Session, *, user_id: int) -> Optional[User]:
        """更新最后登录时间"""
        user = self.get(db, user_id)
        if user:
            from datetime import datetime
            user.last_login = datetime.now()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

user = CRUDUser(User) 