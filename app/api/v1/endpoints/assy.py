from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional
from datetime import date

from app.db.session import get_db
from app.schemas.response import IResponse
from app.core.deps import get_current_active_user
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.models.user import User
from app.schemas.e10 import AssyOrderQuery, AssyOrderResponse, AssyWipQuery, AssyWipResponse
from app.services.e10_service import E10Service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/table", response_model=IResponse[AssyOrderResponse])
@monitor_request
async def get_assy_order_by_params(
    params: AssyOrderQuery = Depends(),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_order_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/wip", response_model=IResponse[AssyWipResponse])
@monitor_request
async def get_assy_wip_by_params(
    params: AssyWipQuery = Depends(),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_wip_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装在制失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装在制失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
