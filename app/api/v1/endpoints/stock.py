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
from app.schemas.stock import (StockQuery, 
                               StockResponse, 
                               WaferIdQtyDetailResponse, 
                               WaferIdQtyDetailQuery,
                               StockSummaryResponse,
                               StockSummaryQuery
                               )
from app.services.e10_service import E10Service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/list", response_model=IResponse[StockResponse])
@monitor_request
async def get_stock_by_params(
    feature_group_name: Optional[str] = Query(None, description="品号群组,多个用逗号分隔"),
    item_code: Optional[str] = Query(None, description="品号,多个用逗号分隔"),
    item_name: Optional[str] = Query(None, description="品名,多个用逗号分隔"),
    lot_code: Optional[str] = Query(None, description="批号,多个用逗号分隔"),
    warehouse_name: Optional[str] = Query(None, description="仓库,多个用逗号分隔"),
    testing_program: Optional[str] = Query(None, description="测试程序,多个用逗号分隔"),
    burning_program: Optional[str] = Query(None, description="烧录程序,多个用逗号分隔"),
    pageIndex: Optional[int] = Query(None, description="页码"),
    pageSize: Optional[int] = Query(None, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """根据参数获取库存列表"""
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = StockQuery()
    
        # 处理可能包含多个值的参数
        if feature_group_name:
            params.feature_group_name = [name.strip() for name in feature_group_name.split(',') if name.strip()]

        if item_code:
            params.item_code = [code.strip() for code in item_code.split(',') if code.strip()]

        if item_name:
            params.item_name = [name.strip() for name in item_name.split(',') if name.strip()]

        if lot_code:
            params.lot_code = [code.strip() for code in lot_code.split(',') if code.strip()]

        if warehouse_name:
            params.warehouse_name = [name.strip() for name in warehouse_name.split(',') if name.strip()]

        if testing_program:
            params.testing_program = [name.strip() for name in testing_program.split(',') if name.strip()]
        
        if burning_program:
            params.burning_program = [name.strip() for name in burning_program.split(',') if name.strip()]

        if pageIndex:
            params.pageIndex = pageIndex

        if pageSize:
            params.pageSize = pageSize

        # 调用服务层方法获取数据
        result = await e10_service.get_stock_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取库存失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="StockError"
        )
    except Exception as e:
        logger.error(f"获取库存失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="StockError"
        )
    
@router.get("/export")
@monitor_request
async def export_stock_by_params(
    feature_group_name: Optional[str] = Query(None, description="品号群组,多个用逗号分隔"),
    item_code: Optional[str] = Query(None, description="品号,多个用逗号分隔"),
    item_name: Optional[str] = Query(None, description="品名,多个用逗号分隔"),
    lot_code: Optional[str] = Query(None, description="批号,多个用逗号分隔"),
    warehouse_name: Optional[str] = Query(None, description="仓库,多个用逗号分隔"),
    testing_program: Optional[str] = Query(None, description="测试程序,多个用逗号分隔"),
    burning_program: Optional[str] = Query(None, description="烧录程序,多个用逗号分隔"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        
        # 构建查询参数
        params = StockQuery()
        
        # 处理可能包含多个值的参数
        if feature_group_name:
            params.feature_group_name = [name.strip() for name in feature_group_name.split(',') if name.strip()]

        if item_code:
            params.item_code = [code.strip() for code in item_code.split(',') if code.strip()]

        if item_name:
            params.item_name = [name.strip() for name in item_name.split(',') if name.strip()]

        if lot_code:
            params.lot_code = [code.strip() for code in lot_code.split(',') if code.strip()]

        if warehouse_name:
            params.warehouse_name = [name.strip() for name in warehouse_name.split(',') if name.strip()]

        if testing_program:
            params.testing_program = [name.strip() for name in testing_program.split(',') if name.strip()]
        
        if burning_program:
            params.burning_program = [name.strip() for name in burning_program.split(',') if name.strip()]
            
        excel_data = await e10_service.export_stock_by_params(params)
        
        # 生成文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stockQuery_{current_time}.xlsx"

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except CustomException as e:
        logger.error(f"导出库存失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="StockExportError"
        )
    except Exception as e:
        logger.error(f"导出库存失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="StockExportError"
        )

@router.get("/wafer_id_qty_detail", response_model=IResponse[WaferIdQtyDetailResponse])
@monitor_request
async def get_wafer_id_qty_detail_by_params(
    item_code: Optional[str] = Query(None, description="品号"),
    lot_code: Optional[str] = Query(None, description="批号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """根据参数获取晶圆ID数量明细"""
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = WaferIdQtyDetailQuery(
            item_code=item_code,
            lot_code=lot_code
        )

        # 调用服务层方法获取数据
        result = await e10_service.get_wafer_id_qty_detail_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取晶圆ID数量明细失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="WaferIdQtyDetailError"
        )
    except Exception as e:
        logger.error(f"获取晶圆ID数量明细失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="WaferIdQtyDetailError"
        )
    
@router.get("/summary", response_model=IResponse[StockSummaryResponse])
@monitor_request
async def get_stock_summary_by_params(
    item_name: Optional[str] = Query(None, description="品名"),
    warehouse_name: Optional[str] = Query(None, description="仓库"),
    feature_group_name: Optional[str] = Query(None, description="品号群组"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """根据参数获取库存汇总"""
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = StockSummaryQuery(
            item_name=item_name,
            warehouse_name=warehouse_name,
            feature_group_name=feature_group_name
        )
        # 调用服务层方法获取数据
        result = await e10_service.get_stock_summary_by_params(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取库存汇总失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="StockSummaryError"
        )
    except Exception as e:
        logger.error(f"获取库存汇总失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="StockSummaryError"
        )

