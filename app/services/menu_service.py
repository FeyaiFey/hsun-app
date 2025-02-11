from typing import List, Dict, Any, Optional
from sqlmodel import Session
from app.models.menu import Menu
from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuResponse,
    MenuPermissionInfo,
    MenuRoleInfo
)
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.monitor import MetricsManager
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.crud.menu import menu as crud_menu
from app.services.cache_service import cache_service

class MenuService:
    """菜单服务类"""
    
    def __init__(self, db: Session, cache: MemoryCache):
        self.db = db
        self.cache = cache
        self.metrics = MetricsManager()

    def _clear_menu_cache(self, menu_id: Optional[int] = None) -> None:
        """清除菜单缓存"""
        try:
            if menu_id:
                cache_service.clear_model_cache(
                    menu_id,
                    ["menu", "menu:tree", "menu:children"]
                )
            else:
                cache_service.clear_list_cache(
                    ["menu:list", "menu:tree"]
                )
        except Exception as e:
            logger.error(f"清除菜单缓存失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_menu_by_id(self, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        try:
            return await cache_service.get_model_by_id(
                db=self.db,
                model_type=Menu,
                model_id=menu_id,
                prefix="menu"
            )
        except Exception as e:
            logger.error(f"获取菜单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.RESOURCE_NOT_FOUND)
            )

    async def get_menu_tree(self) -> List[Dict[str, Any]]:
        """获取菜单树"""
        try:
            # 尝试从缓存获取
            cache_key = "menu:tree"
            cached_tree = self.cache.get(cache_key)
            if cached_tree:
                self.metrics.track_cache_metrics(hit=True)
                return cached_tree

            self.metrics.track_cache_metrics(hit=False)
            
            # 获取所有根菜单
            menus = crud_menu.get_tree(self.db)
            
            # 构建树形结构
            menu_tree = []
            for menu in menus:
                menu_dict = menu.dict()
                children = crud_menu.get_children(self.db, menu.id)
                if children:
                    menu_dict["children"] = [child.dict() for child in children]
                menu_tree.append(menu_dict)
            
            # 缓存结果
            self.cache.set(cache_key, menu_tree, expire=3600)
            
            return menu_tree
            
        except Exception as e:
            logger.error(f"获取菜单树失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def get_user_menus(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户菜单"""
        try:
            # 尝试从缓存获取
            cache_key = f"user:menus:{user_id}"
            cached_menus = self.cache.get(cache_key)
            if cached_menus:
                self.metrics.track_cache_metrics(hit=True)
                return cached_menus

            self.metrics.track_cache_metrics(hit=False)
            
            # 获取用户菜单
            menus = crud_menu.get_user_menus(self.db, user_id)
            
            # 构建树形结构
            menu_tree = []
            root_menus = [menu for menu in menus if not menu.parent_id]
            for menu in root_menus:
                menu_dict = menu.dict()
                children = [m for m in menus if m.parent_id == menu.id]
                if children:
                    menu_dict["children"] = [child.dict() for child in children]
                menu_tree.append(menu_dict)
            
            # 缓存结果
            self.cache.set(cache_key, menu_tree, expire=3600)
            
            return menu_tree
            
        except Exception as e:
            logger.error(f"获取用户菜单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def create_menu(self, menu_in: MenuCreate) -> Menu:
        """创建菜单"""
        try:
            # 检查名称是否已存在
            if crud_menu.get_by_name(self.db, menu_in.name):
                raise CustomException(
                    message=get_error_message(ErrorCode.RESOURCE_ALREADY_EXISTS)
                )
                
            menu = crud_menu.create(self.db, obj_in=menu_in)
            
            # 清除缓存
            self._clear_menu_cache()
            
            return menu
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"创建菜单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def update_menu(
        self, menu_id: int, menu_in: MenuUpdate
    ) -> Menu:
        """更新菜单"""
        try:
            menu = crud_menu.get(self.db, menu_id)
            if not menu:
                raise CustomException(
                    message=get_error_message(ErrorCode.RESOURCE_NOT_FOUND)
                )
                
            # 检查名称是否已被其他菜单使用
            if menu_in.name:
                existing = crud_menu.get_by_name(self.db, menu_in.name)
                if existing and existing.id != menu_id:
                    raise CustomException(
                        message=get_error_message(ErrorCode.RESOURCE_ALREADY_EXISTS)
                    )
            
            menu = crud_menu.update(self.db, db_obj=menu, obj_in=menu_in)
            
            # 清除缓存
            self._clear_menu_cache(menu_id)
            
            return menu
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"更新菜单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

    async def delete_menu(self, menu_id: int) -> Menu:
        """删除菜单"""
        try:
            menu = crud_menu.get(self.db, menu_id)
            if not menu:
                raise CustomException(
                    message=get_error_message(ErrorCode.RESOURCE_NOT_FOUND)
                )
                
            # 删除菜单（包括子菜单）
            menu = crud_menu.remove(self.db, id=menu_id)
            
            # 清除缓存
            self._clear_menu_cache()
            
            return menu
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"删除菜单失败: {str(e)}")
            raise CustomException(
                message=get_error_message(ErrorCode.DB_ERROR)
            )

# 创建全局菜单服务实例
menu_service = MenuService(None, None)  # 在应用启动时注入实际的 db 和 cache 