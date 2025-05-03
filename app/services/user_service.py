from typing import Dict, Any, Optional, List
from sqlmodel import Session, select, func
import base64
import hashlib
import os
from datetime import datetime
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserTableListResponse,
    UserTableItem,
    UserEmailInfo
)
from app.crud.user import user as crud_user
from app.crud.role import role as crud_role
from app.models.user import UserAvatar

# 默认头像路径
DEFAULT_AVATAR_PATH = "static/avatars/default.png"

class UserService:
    """用户服务类"""
    
    def __init__(self, db: Optional[Session] = None, cache: Optional[MemoryCache] = None):
        self._db = db
        self._cache = cache

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if not self._db:
            raise CustomException("数据库会话未注入")
        return self._db
    
    @db.setter
    def db(self, value: Session):
        """设置数据库会话"""
        self._db = value
        
    @property
    def cache(self) -> MemoryCache:
        """获取缓存实例"""
        if not self._cache:
            raise CustomException("缓存实例未注入")
        return self._cache
    
    @cache.setter
    def cache(self, value: MemoryCache):
        """设置缓存实例"""
        self._cache = value

    def _clear_user_cache(self, user_id: int) -> None:
        """清除用户相关缓存"""
        try:
            cache_keys = [
                f"user:{user_id}",
                "user:list",
                f"user:permissions:{user_id}",
                f"user:menus:{user_id}",
                f"user:roles:{user_id}"
            ]
            for key in cache_keys:
                self.cache.delete(key)
        except Exception as e:
            logger.error(f"清除用户缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def create_user(self, user_in: UserCreate) -> User:
        """创建用户"""
        try:
            # 验证用户名唯一性
            if crud_user.get_by_username(self.db, user_in.username):
                raise CustomException("用户名已存在")
                
            # 验证邮箱唯一性
            if user_in.email and crud_user.get_by_email(self.db, user_in.email):
                raise CustomException("邮箱已存在")
            
            # 创建用户
            user = crud_user.create(self.db, obj_in=user_in)
            
            # 创建默认头像
            crud_user.create_user_avatar(
                self.db,
                user_id=user.id,
                avatar_url=DEFAULT_AVATAR_PATH
            )
            
            # 分配默认角色
            crud_role.assign_default_role(self.db, user_id=user.id)
            
            return user
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """更新用户"""
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise CustomException("用户不存在")
                
            # 验证用户名唯一性
            if user_in.username:
                existing = crud_user.get_by_username(self.db, user_in.username)
                if existing and existing.id != user_id:
                    raise CustomException("用户名已存在")
                    
            # 验证邮箱唯一性
            if user_in.email:
                existing = crud_user.get_by_email(self.db, user_in.email)
                if existing and existing.id != user_id:
                    raise CustomException("邮箱已存在")
            
            # 更新用户
            user = crud_user.update(self.db, db_obj=user, obj_in=user_in)
            
            # 清除缓存
            self._clear_user_cache(user_id)
            
            return user
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def delete_user(self, user_id: int) -> None:
        """删除用户"""
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise CustomException("用户不存在")
                
            # 删除用户
            crud_user.remove(self.db, id=user_id)
            
            # 清除缓存
            self._clear_user_cache(user_id)
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def batch_delete_users(self, user_ids: List[int]) -> None:
        """批量删除用户"""
        try:
            for user_id in user_ids:
                await self.delete_user(user_id)
                
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"批量删除用户失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_users_list_with_params(
        self,
        params: Dict[str, Any]
    ) -> UserTableListResponse:
        """获取用户列表
        
        Args:
            params: 查询参数
                - username: 用户名
                - email: 邮箱
                - status: 状态
                - department_id: 部门ID
                - pageIndex: 页码
                - pageSize: 每页数量
                - order_by: 排序字段
                
        Returns:
            UserTableListResponse: 用户列表响应
        """
        try:
            # 转换分页参数
            query_params = {
                "username": params.get("username"),
                "email": params.get("email"),
                "status": params.get("status"),
                "department_id": params.get("department_id"),
                "order_by": params.get("order_by"),
                "skip": (params.get("pageIndex", 1) - 1) * params.get("pageSize", 10),
                "limit": params.get("pageSize", 10)
            }
            
            # 使用crud_user的实现获取用户列表
            return crud_user.get_users_list_with_params(
                db=self.db,
                params=query_params
            )
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def update_email_password(self, user_id: int, new_password: str) -> None:
        """更新邮箱密码"""
        try:
            user = crud_user.get(self.db, user_id)
            if not user:
                raise CustomException("用户不存在")
            
            # 更新邮箱密码
            crud_user.update_email_password(self.db, user_id, new_password)
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取用户邮箱信息失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )
    
    async def get_user_email_info(self, user_id: int) -> UserEmailInfo:
        """获取用户邮箱信息"""
        try:
            return crud_user.get_user_email_info(self.db, user_id)
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"获取用户邮箱信息失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def update_user_avatar(self, user_id: int, avatar_data: str) -> None:
        """更新用户头像
        
        Args:
            user_id: 用户ID
            avatar_data: base64编码的图片数据，格式为 "data:image/xxx;base64,xxxxx"
        """
        try:
            # 验证用户是否存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException("用户不存在")
                
            # 解析base64数据
            try:
                # 移除 data:image/xxx;base64, 前缀
                if "," in avatar_data:
                    avatar_data = avatar_data.split(",", 1)[1]
                    
                # 解码base64数据
                image_data = base64.b64decode(avatar_data)
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"avatar_{user_id}_{timestamp}.png"
                
                # 确保上传目录存在
                upload_dir = os.path.join("static", "avatars")
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存图片文件
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(image_data)
                    
                # 更新用户头像URL
                avatar_url = f"/static/avatars/{filename}"
                
                # 将之前的头像设置为非活动
                self.db.query(UserAvatar).filter(
                    UserAvatar.user_id == user_id,
                    UserAvatar.is_active == True
                ).update({"is_active": False})
                
                # 创建新的头像记录
                new_avatar = UserAvatar(
                    user_id=user_id,
                    avatar_url=avatar_url,
                    is_active=True
                )
                self.db.add(new_avatar)
                self.db.commit()
                
                logger.info(f"用户 {user_id} 头像更新成功")
                
            except Exception as e:
                logger.error(f"处理头像数据失败: {str(e)}")
                raise CustomException("处理头像数据失败")
                
        except CustomException as e:
            raise e
        except Exception as e:
            logger.error(f"更新用户头像失败: {str(e)}")
            raise CustomException("更新用户头像失败")

# 创建服务实例
user_service = UserService(None, None)  # 在应用启动时注入实际的 db 和 cache 