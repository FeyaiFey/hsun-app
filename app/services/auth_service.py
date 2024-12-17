from fastapi import HTTPException, status
from sqlmodel import Session
from app.crud.user import user_crud
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserResponse
from app.core.logger import logger

async def authenticate_user(email: str, password: str, db: Session) -> UserResponse:
    """用户认证"""
    try:
        user = await user_crud.get_user_by_email(db, email)
        if not user:
            logger.warning(f"登录失败: 用户不存在 - {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
            
        if not verify_password(password, user.password_hash):
            logger.warning(f"登录失败: 密码错误 - {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        token = create_access_token(data={"sub": user.email})
        user_details = await user_crud.get_user_details(email, db)
        
        logger.info(f"用户登录成功: {email}")
        
        return UserResponse(
            email=user_details.email,
            nickname=user_details.nickname,
            department=user_details.department,
            avatar_url=user_details.avatar_url,
            token=token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"认证过程发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证失败"
        )

async def get_department(db: Session):
    """获取部门信息"""
    try:
        departments = await user_crud.get_department(db)
        if not departments:
            raise HTTPException(status_code=404, detail="部门信息不存在")
        return departments
    except Exception as e:
        logger.error(f"获取部门信息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取部门信息失败: {str(e)}"
        )

async def get_user_info(email: str, db: Session):
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

async def get_user_details(email: str, db: Session):
    user_details = await user_crud.get_user_details(db, email)
    if not user_details:
        raise HTTPException(status_code=404, detail="用户信息不存在")
    return user_details
