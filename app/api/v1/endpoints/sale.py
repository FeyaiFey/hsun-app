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
    SaleTargetDetailQuery, SaleTargetDetailResponse
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
    params: SaleTargetCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.create_sale_target(db,current_user.username,params)
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
    params: SaleTargetUpdate = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        sale_service = SaleService(db)
        sale_target = await sale_service.update_sale_target(db,params)
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
    id: UUID = Depends(),
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
    

