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
from app.schemas.e10 import (
    AssyOrderQuery, AssyOrderResponse, AssyWipQuery, AssyWipResponse, AssyOrderItemsQuery, AssyOrderItemsResponse,
    AssyOrderPackageTypeQuery, AssyOrderPackageTypeResponse, AssyOrderSupplierQuery, AssyOrderSupplierResponse
)
from app.services.e10_service import E10Service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/table", response_model=IResponse[AssyOrderResponse])
@monitor_request
async def get_assy_order_by_params(
    pageIndex: int = Query(1, description="页码"),
    pageSize: int = Query(50, description="每页数量"),
    item_code: Optional[str] = Query(None, description="品号，多个用逗号分隔"),
    doc_no: Optional[str] = Query(None, description="单号"),
    supplier: Optional[str] = Query(None, description="供应商，多个用逗号分隔"),
    package_type: Optional[str] = Query(None, description="封装类型，多个用逗号分隔"),
    is_closed: Optional[int] = Query(None, description="是否结案"),
    order_date_start: Optional[str] = Query(None, description="订单日期开始"),
    order_date_end: Optional[str] = Query(None, description="订单日期结束"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderQuery(
            pageIndex=pageIndex,
            pageSize=pageSize,
            doc_no=doc_no,
            is_closed=is_closed
        )
        
        # 处理日期参数
        if order_date_start:
            params.order_date_start = date.fromisoformat(order_date_start)
        if order_date_end:
            params.order_date_end = date.fromisoformat(order_date_end)
            
        # 处理可能包含多个值的参数
        if item_code:
            params.item_code = [code.strip() for code in item_code.split(',') if code.strip()]
        if supplier:
            params.supplier = [s.strip() for s in supplier.split(',') if s.strip()]
        if package_type:
            params.package_type = [pt.strip() for pt in package_type.split(',') if pt.strip()]
            
        # 调用服务层方法获取数据
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

@router.get("/items", response_model=IResponse[AssyOrderItemsResponse])
@monitor_request
async def get_assy_wip_items(
    item_code: Optional[str] = Query(None, description="品号"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderItemsQuery(
            item_code=item_code
        )
        logger.info(f"接收到的参数: {params.model_dump()}")
        result = await e10_service.get_assy_order_items(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装在制品号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装在制品号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/package_type", response_model=IResponse[AssyOrderPackageTypeResponse])
@monitor_request
async def get_assy_order_package_type(
    package_type: Optional[str] = Query(None, description="封装类型"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderPackageTypeQuery(
            package_type=package_type
        )
        logger.info(f"接收到的参数: {params.model_dump()}")
        result = await e10_service.get_assy_order_package_type(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装类型失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装类型失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/supplier", response_model=IResponse[AssyOrderSupplierResponse])
@monitor_request
async def get_assy_order_supplier(
    supplier: Optional[str] = Query(None, description="供应商"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderSupplierQuery(
            supplier=supplier
        )
        logger.info(f"接收到的参数: {params.model_dump()}")
        result = await e10_service.get_assy_order_supplier(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装供应商失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
