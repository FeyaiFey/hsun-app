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
from app.schemas.purchase import (PurchaseOrderQuery, 
                             PurchaseOrderResponse, 
                             PurchaseWipQuery, 
                             PurchaseWipResponse, 
                             PurchaseWipSupplierResponse, 
                             PurchaseSupplierResponse)
from app.services.e10_service import E10Service


router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/table", response_model=IResponse[PurchaseOrderResponse])
@monitor_request
async def get_purchase_order_by_params(
    params: PurchaseOrderQuery = Depends(),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    """根据参数获取采购订单
    
    Args:
        params: 查询参数，包含：
            - receipt_close: 收货结束状态
            - doc_no: 单据编号
            - item_code: 物料编码
            - item_name: 物料名称
            - supplier: 供应商
            - purchase_date: 采购日期
            - pageIndex: 页码
            - pageSize: 每页数量
    """
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_purchase_order_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取采购订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="POError"
        )
    except Exception as e:
        logger.error(f"获取采购订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/wip", response_model=IResponse[PurchaseWipResponse])
@monitor_request
async def get_purchase_wip_by_params(
    params: PurchaseWipQuery = Depends(),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_purchase_wip_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取采购在途失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="WipError"
        )
    except Exception as e:
        logger.error(f"获取采购在途失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/supplier", response_model=IResponse[PurchaseSupplierResponse])
@monitor_request
async def get_purchase_supplier(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_purchase_supplier()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取采购供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SupplierError"
        )
    except Exception as e:
        logger.error(f"获取采购供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/wip/supplier", response_model=IResponse[PurchaseWipSupplierResponse])
@monitor_request
async def get_purchase_wip_supplier(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_purchase_wip_supplier()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取采购在制供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="WipSupplierError"
        )
    except Exception as e:
        logger.error(f"获取采购在制供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    

        
