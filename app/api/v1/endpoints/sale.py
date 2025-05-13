from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional
from datetime import date, datetime
from fastapi.responses import StreamingResponse
from uuid import UUID

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
from app.schemas.sale import (
    SaleTableQuery, SaleTableResponse, SaleTargetCreate, SaleTargetUpdate,
    SaleTargetSummaryQuery, SaleTargetSummaryResponse,
    SaleTargetDetailQuery, SaleTargetDetailResponse,
    SaleAmountAnalyzeQuery, SaleAmountAnalyzeResponse,
    SaleAnalysisPannelResponse, SaleForecastResponse,
    SaleAmountResponse, SaleAmountQuery
)
from app.services.sale_service import SaleService

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/target/table", response_model=IResponse[SaleTableResponse])
@monitor_request
async def get_sale_target_table(
    params: SaleTableQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_table = await sale_service.get_sale_table(db,params)
        return CustomResponse.success(data=sale_table)
    except CustomException as e:
        logger.error(f"获取销售目标列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售目标列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

@router.post("/target/create", response_model=IResponse[SaleTableResponse])
@monitor_request
async def create_sale_target(
    data: SaleTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.create_sale_target(db,current_user.username,data)
        return CustomResponse.success(data=sale_target,message="创建成功!")
    except CustomException as e:
        logger.error(f"创建销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"创建销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

@router.put("/target/update", response_model=IResponse[SaleTableResponse])
@monitor_request
async def update_sale_target(
    data: SaleTargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    logger.info(f"更新销售目标: {data}")
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.update_sale_target(db,data)
        return CustomResponse.success(data=sale_target,message="更新成功!")
    except CustomException as e:
        logger.error(f"更新销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"更新销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )
    
@router.delete("/target/delete", response_model=IResponse[SaleTableResponse])
@monitor_request
async def delete_sale_target(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.delete_sale_target(db,id)
        return CustomResponse.success(data=sale_target,message="删除成功!")
    except CustomException as e:
        logger.error(f"删除销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"删除销售目标失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

@router.get("/target/summary",response_model=IResponse[SaleTargetSummaryResponse])
@monitor_request
async def get_sale_target_summary(
    params: SaleTargetSummaryQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.get_sale_target_summary(db,params)
        return CustomResponse.success(data=sale_target)
    except CustomException as e:
        logger.error(f"获取销售目标汇总失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售目标汇总失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )


@router.get("/target/detail",response_model=IResponse[SaleTargetDetailResponse])
@monitor_request
async def get_sale_target_detail(
    params: SaleTargetDetailQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.get_sale_target_detail(db,params)
        return CustomResponse.success(data=sale_target)
    except CustomException as e:
        logger.error(f"获取销售目标详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售目标详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )
    
@router.get("/amount/analyze",response_model=IResponse[SaleAmountAnalyzeResponse])
@monitor_request
async def get_sale_amount_analyze(
    params: SaleAmountAnalyzeQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_amount = await sale_service.get_sale_amount_analyze(db,params)
        return CustomResponse.success(data=sale_amount)
    except CustomException as e:
        logger.error(f"获取销售金额分析失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售金额分析失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

@router.get("/pannel",response_model=IResponse[SaleAnalysisPannelResponse])
@monitor_request
async def get_sale_analysis_pannel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_pannel = await sale_service.get_sale_analysis_pannel(db)
        return CustomResponse.success(data=sale_pannel)
    except CustomException as e:
        logger.error(f"获取销售分析面板失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售分析面板失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )
@router.get("/analyze/forecast",response_model=IResponse[SaleForecastResponse])
@monitor_request
async def get_sale_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_forecast = await sale_service.get_sale_forecast(db)
        return CustomResponse.success(data=sale_forecast)
    except CustomException as e:
        logger.error(f"获取销售预测失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售预测失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

@router.get("/analyze/amount",response_model=IResponse[SaleAmountResponse])
@monitor_request
async def get_sale_amount_detail(
    params: SaleAmountQuery = Depends(),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_amount = await sale_service.get_sale_analyze_amount(db,params)
        return CustomResponse.success(data=sale_amount)
    except CustomException as e:
        logger.error(f"获取销售金额详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleError"
        )
    except Exception as e:
        logger.error(f"获取销售金额详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="SaleError"
        )

