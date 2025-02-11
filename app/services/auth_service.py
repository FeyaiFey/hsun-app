from datetime import timedelta
from typing import Dict, Any, Optional, Set
from sqlmodel import Session
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.logger import logger
from app.core.config import settings
from app.models.user import User, UserAvatar, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.department_service import DepartmentService
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.monitor import MetricsManager
from app.core.error_codes import ErrorCode, get_error_message
from app.crud.user import user as crud_user
from app.crud.role import role as crud_role
from app.services.cache_service import cache_service

# 默认头像路径
DEFAULT_AVATAR_PATH = "static/avatars/default.png"

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session, cache: MemoryCache):
        self.db = db
        self.cache = cache
        self.department_service = DepartmentService(db, cache)
        self.metrics = MetricsManager()

    def _clear_user_cache(self, user_id: int) -> None:
        """清除用户相关缓存"""
        try:
            cache_service.clear_model_cache(
                user_id,
                [
                    "user",
                    "user:permissions",
                    "user:menus",
                    "user:roles"
                ]
            )
        except Exception as e:
            logger.error(f"清除用户缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """用户登录认证"""
        try:
            user = crud_user.get_by_email(self.db, email)
            
            if not user:
                self.metrics.track_auth_metrics(success=False, reason="user_not_found")
                logger.warning(f"登录失败: 邮箱 {email} 不存在")
                raise CustomException(
                    message=get_error_message(ErrorCode.USER_NOT_FOUND)
                )
            
            if not verify_password(password, user.password_hash):
                self.metrics.track_auth_metrics(success=False, reason="invalid_password")
                logger.warning(f"登录失败: 邮箱 {email} 密码错误")
                raise CustomException(
                    message=get_error_message(ErrorCode.PASSWORD_ERROR)
                )
            
            if not user.status:
                self.metrics.track_auth_metrics(success=False, reason="user_disabled")
                logger.warning(f"登录失败: 用户 {user.username} 已被禁用")
                raise CustomException(
                    message=get_error_message(ErrorCode.ACCOUNT_LOCKED)
                )

            # 获取用户部门名称
            department_name = ""
            if user.department_id:
                try:
                    department = await self.department_service.get_department_by_id(user.department_id)
                    if department:
                        department_name = department.department_name
                except Exception as e:
                    logger.warning(f"获取部门信息失败: {str(e)}")

            # 获取用户头像
            avatar_url = DEFAULT_AVATAR_PATH
            active_avatar = crud_user.get_active_avatar(self.db, user.id)
            if active_avatar:
                avatar_url = active_avatar.avatar_url

            # 获取用户角色
            user_roles = []
            try:
                roles = crud_role.get_user_roles(self.db, user.id)
                if roles:
                    user_roles = [role.role_name for role in roles]
            except Exception as e:
                logger.warning(f"获取用户角色失败: {str(e)}")

            # 生成访问令牌
            access_token = await self.create_access_token(
                user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            # 构建响应数据
            response_data = {
                "userinfo": {
                    "email": user.email or "",
                    "username": user.username,
                    "department_name": department_name,
                    "avatar_url": avatar_url,
                    "password": "",
                    "roles": user_roles
                },
                "token": access_token
            }
                
            self.metrics.track_auth_metrics(success=True)
            logger.info(f"用户 {user.username} 登录成功")
            return response_data
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"登录异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.SYSTEM_ERROR)
            )

    async def create_user(self, user_in: UserCreate) -> User:
        """创建新用户"""
        try:
            # 验证用户名
            if crud_user.get_by_username(self.db, user_in.username):
                raise CustomException(
                    message=get_error_message(ErrorCode.USER_ALREADY_EXISTS)
                )
            
            # 验证邮箱    
            if crud_user.get_by_email(self.db, user_in.email):
                raise CustomException(
                    message=get_error_message(ErrorCode.USER_ALREADY_EXISTS)
                )
            
            # 创建用户
            user = crud_user.create(self.db, obj_in=user_in)
            
            # 创建默认头像
            await self._create_default_avatar(user.id)

            # 分配默认角色
            await self._assign_default_role(user.id)
            
            logger.info(f"用户 {user.username}({user.email}) 创建成功")
            return user
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"创建用户异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def _create_default_avatar(self, user_id: int) -> UserAvatar:
        """创建默认头像"""
        try:
            return crud_user.create_user_avatar(
                self.db,
                user_id=user_id,
                avatar_url=DEFAULT_AVATAR_PATH
            )
        except Exception as e:
            logger.error(f"创建默认头像失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def _assign_default_role(self, user_id: int) -> UserRole:
        """分配默认角色"""
        try:
            return crud_role.assign_default_role(
                self.db,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"创建默认角色失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )


    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """获取用户权限"""
        try:
            # 尝试从缓存获取
            cache_key = f"user:permissions:{user_id}"
            cached_permissions = self.cache.get(cache_key)
            if cached_permissions:
                self.metrics.track_cache_metrics(hit=True)
                return cached_permissions

            self.metrics.track_cache_metrics(hit=False)
            
            # 获取用户角色
            roles = crud_role.get_user_roles(self.db, user_id)
            if not roles:
                return set()
                
            # 获取角色权限
            permissions = set()
            for role in roles:
                role_permissions = crud_role.get_role_permissions(self.db, role.id)
                permissions.update(p.action for p in role_permissions if p.action)
            
            # 缓存结果
            self.cache.set(cache_key, permissions, expire=3600)
            
            return permissions
            
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            return set()

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """更新用户信息"""
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise CustomException(
                    message=get_error_message(ErrorCode.USER_NOT_FOUND)
                )

            update_data = user_in.dict(exclude_unset=True)
            
            # 验证用户名唯一性
            if "username" in update_data:
                existing_user = crud_user.get_by_username(
                    self.db,
                    update_data["username"]
                )
                if existing_user and existing_user.id != user_id:
                    raise CustomException(
                        message=get_error_message(ErrorCode.USER_ALREADY_EXISTS)
                    )
                    
            # 验证邮箱唯一性
            if "email" in update_data:
                existing_user = crud_user.get_by_email(
                    self.db,
                    update_data["email"]
                )
                if existing_user and existing_user.id != user_id:
                    raise CustomException(
                        message=get_error_message(ErrorCode.USER_ALREADY_EXISTS)
                    )
            
            # 更新用户信息
            user = crud_user.update(self.db, db_obj=user, obj_in=update_data)
            
            # 清除缓存
            self._clear_user_cache(user_id)
            
            logger.info(f"用户 {user.username} 信息更新成功")
            return user
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"更新用户信息异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            return await cache_service.get_model_by_id(
                db=self.db,
                model_type=User,
                model_id=user_id,
                prefix="user"
            )
        except Exception as e:
            logger.error(f"获取用户异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.USER_NOT_FOUND)
            )

    async def update_user_avatar(self, user_id: int, avatar_url: str) -> UserAvatar:
        """更新用户头像"""
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise CustomException(
                    message=get_error_message(ErrorCode.USER_NOT_FOUND)
                )

            # 创建新头像
            avatar = crud_user.create_user_avatar(
                self.db,
                user_id=user_id,
                avatar_url=avatar_url
            )

            # 清除缓存
            self._clear_user_cache(user_id)
            
            logger.info(f"用户 {user.username} 头像更新成功")
            return avatar
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"更新用户头像异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def create_access_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        try:
            to_encode = {"sub": str(user_id)}
            token = create_access_token(
                data=to_encode,
                expires_delta=expires_delta
            )
            logger.info(f"为用户 {user_id} 创建访问令牌成功")
            return token
        except Exception as e:
            logger.error(f"创建访问令牌异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )

    async def create_refresh_token(self, user_id: int) -> str:
        """创建刷新令牌"""
        try:
            to_encode = {"sub": str(user_id)}
            token = create_refresh_token(
                data=to_encode,
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            logger.info(f"为用户 {user_id} 创建刷新令牌成功")
            return token
        except Exception as e:
            logger.error(f"创建刷新令牌异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )

    async def update_user_login(self, user_id: int) -> None:
        """更新用户最后登录时间"""
        try:
            crud_user.update_last_login(self.db, user_id=user_id)
            # 清除缓存
            self._clear_user_cache(user_id)
            logger.info(f"更新用户 {user_id} 最后登录时间成功")
        except Exception as e:
            logger.error(f"更新用户登录时间异常: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建全局认证服务实例
auth_service = AuthService(None, None)  # 在应用启动时注入实际的 db 和 cache
