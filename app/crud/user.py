from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.models.user import User, UserAvatar
from app.schemas.user import UserCreate, UserUpdate, UserInfoResponse, UserTableListResponse, UserTableItem, UserEmailInfo
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.role import Role
from app.models.user import UserRole
from sqlalchemy import select as sa_select
from app.core.logger import logger
from app.core.exceptions import CustomException

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

    def get_users_list_with_params(
        self,
        db: Session,
        *,
        params: Dict[str, Any]
    ) -> UserTableListResponse:
        """根据参数获取用户列表"""
        # 构建基础查询
        base_query = """
            SELECT u.id,u.username,u.email,u.department_id,d.department_name,u.last_login,u.status,u.created_at,
                   r.id as role_id,r.role_name,r.description
            FROM huaxinAdmin_users u
            LEFT JOIN huaxinAdmin_departments d ON u.department_id = d.id
            LEFT JOIN huaxinAdmin_userRoles ur ON u.id = ur.user_id
            LEFT JOIN huaxinAdmin_roles r ON ur.role_id = r.id
            WHERE 1=1
        """
        
        # 构建条件
        conditions = []
        query_params = {}
        if params.get("username"):
            conditions.append("AND u.username LIKE :username")
            query_params["username"] = f"%{params['username']}%"
        if params.get("email"):
            conditions.append("AND u.email LIKE :email")
            query_params["email"] = f"%{params['email']}%"
        if params.get("department_id"):
            conditions.append("AND u.department_id = :department_id")
            query_params["department_id"] = params["department_id"]
        if params.get("status") is not None:
            conditions.append("AND u.status = :status")
            query_params["status"] = params["status"]

        # 添加条件到查询
        query_str = base_query + " " + " ".join(conditions)

        # 添加排序
        order_by = params.get("order_by")
        if order_by:
            if order_by.startswith("-"):
                field = order_by[1:]
                query_str += f" ORDER BY u.{field} DESC"
            else:
                query_str += f" ORDER BY u.{order_by}"
        else:
            query_str += " ORDER BY u.id"

        # 获取总记录数
        count_query = f"""
            SELECT COUNT(DISTINCT u.id)
            FROM huaxinAdmin_users u
            LEFT JOIN huaxinAdmin_departments d ON u.department_id = d.id
            WHERE 1=1 {' '.join(conditions)}
        """
        total = db.execute(text(count_query), query_params).scalar()

        # 添加分页
        skip = params.get("skip", 0)
        limit = params.get("limit", 10)
        query_str += " OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY"
        query_params["skip"] = skip
        query_params["limit"] = limit

        # 执行查询
        query = text(query_str)
        results = db.execute(query, query_params).all()

        # 转换为响应列表，处理多角色数据
        user_dict = {}
        for result in results:
            user_id = result.id
            if user_id not in user_dict:
                # 创建新的用户记录
                user_dict[user_id] = {
                    "id": result.id,
                    "username": result.username,
                    "email": result.email,
                    "department_id": result.department_id,
                    "department_name": result.department_name,
                    "status": result.status,
                    "last_login": result.last_login.strftime("%Y-%m-%d %H:%M:%S") if result.last_login else None,
                    "created_at": result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "roles": []
                }
            
            # 添加角色信息（如果有）
            if result.role_id:
                user_dict[user_id]["roles"].append({
                    "id": result.role_id,
                    "role_name": result.role_name,
                    "description": result.description
                })

        # 构建最终的用户列表
        user_list = []
        for user_data in user_dict.values():
            # 获取第一个角色的ID和描述（如果有）
            role_id = [role["id"] for role in user_data["roles"]]
            description = user_data["roles"][0]["description"] if user_data["roles"] else None
            role_names = [role["role_name"] for role in user_data["roles"]]
            
            user_list.append(
                UserTableItem(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    department_id=user_data["department_id"],
                    department_name=user_data["department_name"],
                    role_id=role_id,
                    role_name=role_names,
                    description=description,
                    status=user_data["status"],
                    last_login=user_data["last_login"],
                    created_at=user_data["created_at"]
                )
            )

        return UserTableListResponse(
            list=user_list,
            total=total or 0
        )

    def update_email_password(self, db: Session, user_id: int, new_password: str) -> None:
        """更新邮箱密码"""
        try:
            sql = text("""
                MERGE INTO huaxinAdmin_email_msg AS target
                USING (SELECT :user_id AS id, :new_password AS email_special_password) AS source
                ON (target.id = source.id)
                WHEN MATCHED THEN
                    UPDATE SET email_special_password = source.email_special_password
                WHEN NOT MATCHED THEN
                    INSERT (id, email_special_password)
                    VALUES (source.id, source.email_special_password);
            """)
            db.execute(sql, {"user_id": user_id, "new_password": new_password})
            db.commit()
        except Exception as e:
            logger.error(f"更新邮箱密码失败: {str(e)}")
            raise CustomException(f'更新邮箱密码失败: {str(e)}')
        
    def get_user_email_info(self, db: Session, user_id: int) -> Optional[UserEmailInfo]:
        """获取用户邮箱信息"""
        try:
            sql = text("""
                SELECT 
                hu.id AS ID,
                hu.email AS EMAIL, 
                he.email_special_password AS PASSWORD,
                's220s.chinaemail.cn' AS IMAP_SERVER, 
                465 AS SMTP_PORT
                FROM huaxinAdmin_users hu
                LEFT JOIN huaxinAdmin_email_msg he ON he.id = hu.id
                WHERE hu.id = :user_id
            """)
            result = db.execute(sql, {"user_id": user_id}).fetchone()
            if result:
                # 将Row对象转换为字典
                data = {
                    "ID": result.ID,
                    "EMAIL": result.EMAIL,
                    "PASSWORD": result.PASSWORD,
                    "IMAP_SERVER": result.IMAP_SERVER,
                    "SMTP_PORT": result.SMTP_PORT
                }
                return UserEmailInfo(**data)
            return None
        except Exception as e:
            logger.error(f"获取用户邮箱信息失败: {str(e)}")
            raise CustomException(f"获取用户邮箱信息失败: {str(e)}")
        
user = CRUDUser(User) 