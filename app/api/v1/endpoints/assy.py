from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional
from datetime import date, datetime
import io
from fastapi.responses import StreamingResponse
from urllib.parse import quote

from app.db.session import get_db
from app.schemas.response import IResponse
from app.core.deps import get_current_user
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.cache import MemoryCache
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.models.user import User
from app.schemas.assy import (
    AssyOrderQuery, AssyOrderResponse, AssyWipQuery, AssyWipResponse, AssyOrderItemsQuery, AssyOrderItemsResponse,
    AssyOrderPackageTypeQuery, AssyOrderPackageTypeResponse, AssyOrderSupplierQuery, AssyOrderSupplierResponse,
    AssyBomQuery, AssyBomResponse, AssyAnalyzeTotalResponse, AssyAnalyzeLoadingResponse, AssyYearTrendResponse
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
    doc_no: Optional[str] = Query(None, description="封装订单号"),
    item_code: Optional[str] = Query(None, description="品号"),
    lot_code: Optional[str] = Query(None, description="批号"),
    package_type: Optional[str] = Query(None, description="封装类型"),
    supplier: Optional[str] = Query(None, description="供应商"),
    assembly_code: Optional[str] = Query(None, description="打线图号"),
    is_closed: Optional[int] = Query(None, description="是否关闭"),
    order_date_start: Optional[str] = Query(None, description="工单日期开始"),
    order_date_end: Optional[str] = Query(None, description="工单日期结束"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderQuery(
            pageIndex=pageIndex,
            pageSize=pageSize,
            doc_no=doc_no,
            item_code=item_code,
            lot_code=lot_code,
            package_type=package_type,
            supplier=supplier,
            assembly_code=assembly_code,
            is_closed=is_closed
        )
        
        # 处理日期参数
        if order_date_start:
            params.order_date_start = date.fromisoformat(order_date_start)
        if order_date_end:
            params.order_date_end = date.fromisoformat(order_date_end)
            
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
    
@router.get("/bom", response_model=IResponse[AssyBomResponse])
@monitor_request
async def get_assy_bom_by_params(
    params: AssyBomQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_bom_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装订单BOM失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装订单BOM失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
        
@router.get("/export")
@monitor_request
async def export_assy_order(
    params: AssyOrderQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        excel_data = await e10_service.export_assy_order(params)
        
        # 生成文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"封装订单_{current_time}.xlsx"
        
        # 对文件名进行URL编码
        encoded_filename = quote(filename)
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except CustomException as e:
        logger.error(f"导出封装订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"导出封装订单失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="导出封装订单失败",
            name="AssyError"
        )

@router.get("/wip", response_model=IResponse[AssyWipResponse])
@monitor_request
async def get_assy_wip_by_params(
    params: AssyWipQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = AssyOrderPackageTypeQuery(
            package_type=package_type
        )
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
    current_user: User = Depends(get_current_user)
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


@router.get("/analyze/total", response_model=IResponse[AssyAnalyzeTotalResponse])
@monitor_request
async def get_assy_analyze_total(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_analyze_total()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装分析总表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装分析总表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/analyze/loading", response_model=IResponse[AssyAnalyzeLoadingResponse])
@monitor_request
async def get_assy_analyze_loading(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    range_type: Optional[str] = Query(None, description="范围类型")
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_analyze_loading(range_type)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装分析装载失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装分析装载失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/analyze/year-trend", response_model=IResponse[AssyYearTrendResponse])
@monitor_request
async def get_assy_year_trend(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_assy_year_trend()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取封装年趋势失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取封装年趋势失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
