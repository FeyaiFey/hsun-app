from sqlmodel import Session, select,text
from typing import Optional
from app.models.user import User, Department, Permission, DepartmentPermissions, UserDepartments
from app.core.cache import cache
from app.core.logger import logger

class UserCRUD:
    def __init__(self):
        self.cache_expire = 3600  # 缓存1小时

    async def get_department(self, db: Session):
        """获取部门信息"""
        try:
            # 直接使用传入的 db session
            query = text("SELECT id, name FROM huaxin_departments ORDER BY id")
            return db.exec(query).all()  # 执行查询
        except Exception as e:
            logger.error(f"获取部门信息失败: {str(e)}")
            raise


    async def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """获取用户基本信息"""
        cache_key = f"user_email_{email}"
        
        # 尝试从缓存获取
        if cached_user := cache.get(cache_key):
            return cached_user
            
        # 从数据库查询
        query = select(User).where(User.email == email)
        user = db.exec(query).first()
        
        # 设置缓存
        if user:
            cache.set(cache_key, user, self.cache_expire)
            
        return user

    async def get_user_details(self, db: Session, email: str) -> Optional[User]:
        """获取用户详细信息(包含部门和权限)"""
        cache_key = f"user_details_{email}"
        
        # 尝试从缓存获取
        if cached_details := cache.get(cache_key):
            return cached_details
            
        # 从数据库查询
        statement = (
            select(
                User.id,
                User.email,
                User.nickname,
                User.avatar_url,
                Department.name.label("department_name"),
                Permission.name.label("permission_name")
            )
            .join(UserDepartments, User.id == UserDepartments.user_id)
            .join(Department, UserDepartments.department_id == Department.id)
            .join(DepartmentPermissions, Department.id == DepartmentPermissions.department_id)
            .join(Permission, DepartmentPermissions.permission_id == Permission.id)
        )
        results = db.exec(statement).all()
        
        # 设置缓存
        if results:
            cache.set(cache_key, results, self.cache_expire)
            
        return results

    async def create_user(self, db: Session, user_data: dict) -> User:
        """创建新用户"""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        cache.clear()  # 清除所有缓存
        return user

    async def update_user(self, db: Session, user_id: int, user_data: dict) -> User:
        """更新用户信息"""
        user = db.get(User, user_id)
        if not user:
            return None
            
        for key, value in user_data.items():
            setattr(user, key, value)
            
        db.commit()
        db.refresh(user)
        cache.clear()  # 清除所有缓存
        return user

# 创建单例实例
user_crud = UserCRUD()

