from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select
from app.models.user import User, UserAvatar
from app.schemas.user import UserCreate, UserUpdate, UserInfoResponse
from app.core.security import get_password_hash

class CRUDUser:
    """用户CRUD操作类"""
    
    def __init__(self, model: User):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[User]:
        """根据ID获取记录"""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[User]:
        """获取多条记录"""
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        return db.exec(query.offset(skip).limit(limit)).all()
    
    # 使用
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
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> User:
        """删除记录"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: Any) -> bool:
        """检查记录是否存在"""
        obj = db.get(self.model, id)
        return obj is not None

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