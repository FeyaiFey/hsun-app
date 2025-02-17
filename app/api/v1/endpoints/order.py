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
from app.schemas.e10 import PurchaseOrder, PurchaseOrderQuery
from app.services.e10_service import E10Service


router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/purchase", response_model=IResponse[List[PurchaseOrder]])
@monitor_request
async def get_purchase_order_by_params(
    params: PurchaseOrderQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """根据参数获取采购订单"""
    try:
        e10_service = E10Service(db, cache)
        purchase_orders = await e10_service.get_purchase_order_by_params(params)
        return CustomResponse.success(purchase_orders)
    except CustomException as e:
        logger.error(f"获取采购订单失败: {str(e)}")
        raise CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="POError"
        )
    except Exception as e:
        logger.error(f"获取采购订单失败: {str(e)}")
        raise CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
