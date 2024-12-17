from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.response import IResponse
from app.schemas.user import UserLogin, UserResponse, User, Department
from app.services.auth_service import authenticate_user, get_user_details, get_department
from app.core.deps import get_current_user
from app.core.rate_limit import SimpleRateLimiter
from app.core.monitor import monitor_request
from app.core.logger import logger
from typing import List

router = APIRouter()

# 创建限流器实例
rate_limiter = SimpleRateLimiter()

@router.get("/department", response_model=IResponse[List[Department]])
@monitor_request
async def get_department_list(db: Session = Depends(get_db)):
    """获取部门列表"""
    try:
        departments = await get_department(db)
        return IResponse(code=200, data=departments)
    except HTTPException as e:
        logger.warning(f"获取部门信息失败: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"获取部门信息异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取部门信息失败: {str(e)}"
        )


@router.post("/login", response_model=IResponse[UserResponse])
@monitor_request
async def login(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录接口"""
    # 检查限流 - 每分钟最多5次请求
    client_ip = request.client.host
    if not await rate_limiter.check_rate_limit(
        key=f"login:{client_ip}",
        limit=5,
        window=60
    ):
        logger.warning(f"IP {client_ip} 登录请求过于频繁")
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试"
        )

    try:
        user_response = await authenticate_user(
            email=user_data.email,
            password=user_data.password,
            db=db
        )
        return IResponse(code=200, data=user_response)
    except HTTPException as e:
        logger.warning(f"登录失败: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.get("/me", response_model=IResponse[UserResponse])
@monitor_request
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    try:
        user_info = await get_user_details(current_user.email, db)
        return IResponse(
            code=200,
            data=UserResponse(
                email=user_info.email,
                nickname=user_info.nickname,
                department=user_info.department,
                avatar_url=user_info.avatar_url,
                token=""
            )
        )
    except HTTPException as e:
        logger.warning(f"获取用户信息失败: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"获取用户信息异常: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取用户信息失败: {str(e)}"
        )
