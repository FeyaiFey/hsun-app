from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from sqlmodel import Session
from app.core.security import verify_password, create_access_token, get_password_hash, create_refresh_token
from app.core.logger import logger
from app.core.config import settings
from app.models.user import User, UserAvatar
from app.models.role import Role, Permission
from app.schemas.user import UserCreate, UserUpdate
from app.core.cache import MemoryCache
from app.core.exceptions import (
    DatabaseError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    ValidationError
)
from app.core.monitor import MetricsManager
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
        self.metrics = MetricsManager()

    def _clear_user_cache(self, user_id: int) -> None:
        """清除用户相关缓存
        
        Args:
            user_id: 用户ID
        """
        cache_service.clear_model_cache(
            user_id,
            [
                "user",
                "user:permissions",
                "user:menus",
                "user:roles"
            ]
        )

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """用户登录认证
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            Optional[User]: 认证成功返回用户对象
            
        Raises:
            AuthenticationError: 认证失败时抛出
        """
        try:
            user = crud_user.get_by_email(self.db, email)
            
            if not user:
                self.metrics.track_auth_metrics(success=False, reason="user_not_found")
                logger.warning(f"登录失败: 邮箱 {email} 不存在")
                raise AuthenticationError(detail="用户名或密码错误")
            
            if not verify_password(password, user.password_hash):
                self.metrics.track_auth_metrics(success=False, reason="invalid_password")
                logger.warning(f"登录失败: 邮箱 {email} 密码错误")
                raise AuthenticationError(detail="用户名或密码错误")
            
            if not user.status:
                self.metrics.track_auth_metrics(success=False, reason="user_disabled")
                logger.warning(f"登录失败: 用户 {user.username} 已被禁用")
                raise AuthenticationError(detail="用户已被禁用")
                
            self.metrics.track_auth_metrics(success=True)
            logger.info(f"用户 {user.username}({email}) 登录成功")
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"登录异常: {str(e)}")
            raise DatabaseError(detail="登录服务异常")

    async def create_user(self, user_in: UserCreate) -> User:
        """创建新用户
        
        Args:
            user_in: 用户创建信息
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ConflictError: 用户名或邮箱已存在
            ValidationError: 数据验证失败
        """
        try:
            # 验证用户名
            if crud_user.get_by_username(self.db, user_in.username):
                raise ConflictError(detail="用户名已存在")
            
            # 验证邮箱    
            if crud_user.get_by_email(self.db, user_in.email):
                raise ConflictError(detail="邮箱已存在")
            
            # 创建用户
            user = crud_user.create(self.db, obj_in=user_in)
            
            # 创建默认头像
            await self._create_default_avatar(user.id)
            
            logger.info(f"用户 {user.username}({user.email}) 创建成功")
            return user
            
        except ConflictError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"创建用户异常: {str(e)}")
            raise DatabaseError(detail="创建用户失败")

    async def _create_default_avatar(self, user_id: int) -> UserAvatar:
        """创建默认头像
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserAvatar: 头像对象
        """
        try:
            return crud_user.create_user_avatar(
                self.db,
                user_id=user_id,
                avatar_path=DEFAULT_AVATAR_PATH
            )
        except Exception as e:
            logger.error(f"创建默认头像失败: {str(e)}")
            raise DatabaseError(detail="创建默认头像失败")

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """获取用户权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            Set[str]: 权限集合
        """
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
        """更新用户信息
        
        Args:
            user_id: 用户ID
            user_in: 更新的用户信息
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            NotFoundError: 用户不存在
            ConflictError: 用户名/邮箱已被占用
            ValidationError: 数据验证失败
        """
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise NotFoundError(detail="用户不存在")

            update_data = user_in.dict(exclude_unset=True)
            
            # 验证用户名唯一性
            if "username" in update_data:
                existing_user = crud_user.get_by_username(
                    self.db,
                    update_data["username"]
                )
                if existing_user and existing_user.id != user_id:
                    raise ConflictError(detail="用户名已被占用")
                    
            # 验证邮箱唯一性
            if "email" in update_data:
                existing_user = crud_user.get_by_email(
                    self.db,
                    update_data["email"]
                )
                if existing_user and existing_user.id != user_id:
                    raise ConflictError(detail="邮箱已被占用")
            
            # 更新用户信息
            user = crud_user.update(self.db, db_obj=user, obj_in=update_data)
            
            # 清除缓存
            self._clear_user_cache(user_id)
            
            logger.info(f"用户 {user.username} 信息更新成功")
            return user
            
        except (NotFoundError, ConflictError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"更新用户信息异常: {str(e)}")
            raise DatabaseError(detail="更新用户信息失败")

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象
        """
        try:
            return await cache_service.get_model_by_id(
                db=self.db,
                model_type=User,
                model_id=user_id,
                prefix="user"
            )
        except Exception as e:
            logger.error(f"获取用户异常: {str(e)}")
            return None

    async def update_user_avatar(self, user_id: int, avatar_path: str) -> UserAvatar:
        """更新用户头像
        
        Args:
            user_id: 用户ID
            avatar_path: 头像存储路径
            
        Returns:
            UserAvatar: 头像对象
            
        Raises:
            NotFoundError: 用户不存在
            ValidationError: 数据验证失败
        """
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise NotFoundError(detail="用户不存在")

            # 创建新头像
            avatar = crud_user.create_user_avatar(
                self.db,
                user_id=user_id,
                avatar_path=avatar_path
            )

            # 清除缓存
            self._clear_user_cache(user_id)
            
            logger.info(f"用户 {user.username} 头像更新成功")
            return avatar
            
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"更新用户头像异常: {str(e)}")
            raise DatabaseError(detail="更新用户头像失败")

    async def create_access_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌
        
        Args:
            user_id: 用户ID
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT令牌
        """
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
            raise DatabaseError(detail="创建访问令牌失败")

    async def create_refresh_token(self, user_id: int) -> str:
        """创建刷新令牌
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: JWT令牌
        """
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
            raise DatabaseError(detail="创建刷新令牌失败")

    async def update_user_login(self, user_id: int) -> None:
        """更新用户最后登录时间
        
        Args:
            user_id: 用户ID
        """
        try:
            crud_user.update_last_login(self.db, user_id=user_id)
            # 清除缓存
            self._clear_user_cache(user_id)
            logger.info(f"更新用户 {user_id} 最后登录时间成功")
        except Exception as e:
            logger.error(f"更新用户登录时间异常: {str(e)}")
            raise DatabaseError(detail="更新用户登录时间失败")

# 创建全局认证服务实例
auth_service = AuthService(None, None)  # 在应用启动时注入实际的 db 和 cache
