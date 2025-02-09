from .menu import (
    MenuBase,
    MenuCreate,
    MenuUpdate,
    MenuInDB,
    MenuResponse,
    DepartmentBase,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentInDB,
    DepartmentResponse
)

from .role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleInDB,
    RoleResponse,
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    PermissionInDB,
    PermissionResponse
)

from .user import (
    UserAvatarBase,
    UserAvatarCreate,
    UserAvatarResponse,
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserLogin,
    Token,
    TokenPayload
)

# 在所有导入完成后重建模型
MenuResponse.model_rebuild()
DepartmentResponse.model_rebuild()
PermissionResponse.model_rebuild()
RoleResponse.model_rebuild()
UserResponse.model_rebuild()

__all__ = [
    # Menu schemas
    "MenuBase",
    "MenuCreate",
    "MenuUpdate",
    "MenuInDB", 
    "MenuResponse",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentInDB",
    "DepartmentResponse",
    
    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleUpdate", 
    "RoleInDB",
    "RoleResponse",
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionInDB", 
    "PermissionResponse",
    
    # User schemas
    "UserAvatarBase",
    "UserAvatarCreate",
    "UserAvatarResponse",
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload"
] 