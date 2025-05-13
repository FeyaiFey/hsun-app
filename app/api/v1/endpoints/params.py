from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional
from datetime import date

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
from app.schemas.assy import ItemWaferInfoResponse
from app.schemas.e10 import (FeatureGroupNameQuery, 
                             FeatureGroupNameResponse, 
                             ItemCodeQuery, 
                             ItemCodeResponse, 
                             ItemNameQuery, 
                             ItemNameResponse, 
                             WarehouseNameQuery, 
                             WarehouseNameResponse, 
                             TestingProgramQuery, 
                             TestingProgramResponse, 
                             BurningProgramQuery, 
                             BurningProgramResponse, 
                             LotCodeQuery, 
                             LotCodeResponse,
                             SaleUnitResponse,
                             SalesResponse)
from app.services.e10_service import E10Service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/feature_group_name", response_model=IResponse[FeatureGroupNameResponse])
@monitor_request
async def get_feature_group_name(
    feature_group_name: Optional[str] = Query(None, description="品号群组"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = FeatureGroupNameQuery(
            feature_group_name=feature_group_name
        )
        result = await e10_service.get_feature_group_name(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取品号群组失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="FeatureGroupNameError"
        )
    except Exception as e:
        logger.error(f"获取品号群组失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/item_code", response_model=IResponse[ItemCodeResponse])
@monitor_request
async def get_item_code(
    item_code: Optional[str] = Query(None, description="品号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = ItemCodeQuery(
            item_code=item_code
        )   
        result = await e10_service.get_item_code(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取品号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="ItemCodeError"
        )
    except Exception as e:
        logger.error(f"获取品号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/item_name", response_model=IResponse[ItemNameResponse])
@monitor_request
async def get_item_name(
    item_name: Optional[str] = Query(None, description="品名"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = ItemNameQuery(
            item_name=item_name
        )
        result = await e10_service.get_item_name(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取品名失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="ItemNameError"
        )
    except Exception as e:
        logger.error(f"获取品名失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
    
@router.get("/lot_code", response_model=IResponse[LotCodeResponse])
@monitor_request
async def get_lot_code(
    lot_code: Optional[str] = Query(None, description="批号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = LotCodeQuery(
            lot_code=lot_code
        )
        result = await e10_service.get_lot_code(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取批号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="LotCodeError"
        )
    except Exception as e:
        logger.error(f"获取批号失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/warehouse_name", response_model=IResponse[WarehouseNameResponse])
@monitor_request
async def get_warehouse_name(
    warehouse_name: Optional[str] = Query(None, description="仓库"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = WarehouseNameQuery(
            warehouse_name=warehouse_name
        )
        result = await e10_service.get_warehouse_name(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取仓库失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="WarehouseNameError"
        )
    except Exception as e:
        logger.error(f"获取仓库失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/testing_program", response_model=IResponse[TestingProgramResponse])
@monitor_request
async def get_testing_program(
    testing_program: Optional[str] = Query(None, description="测试程序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = TestingProgramQuery(
            testing_program=testing_program
        )
        result = await e10_service.get_testing_program(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取测试程序失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="TestingProgramError"
        )
    except Exception as e:
        logger.error(f"获取测试程序失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/burning_program", response_model=IResponse[BurningProgramResponse])
@monitor_request
async def get_burning_program(
    burning_program: Optional[str] = Query(None, description="烧录程序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        # 构建查询参数
        params = BurningProgramQuery(
            burning_program=burning_program
        )
        result = await e10_service.get_burning_program(params)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取烧录程序失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="BurningProgramError"
        )
    except Exception as e:
        logger.error(f"获取烧录程序失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/requirement/wafer-info", response_model=IResponse[ItemWaferInfoResponse])
@monitor_request
async def get_item_wafer_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    item_name: Optional[str] = Query(None, description="芯片名称")
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_item_wafer_info(item_name)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取晶圆信息失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"获取晶圆信息失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/requirement/sales", response_model=IResponse[SalesResponse])
@monitor_request
async def get_sales(
    admin_unit_name: Optional[str] = Query(None, description="行政部门"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_sales(admin_unit_name)
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取销售员名称失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SalesError"
        )
    except Exception as e:
        logger.error(f"获取销售员名称失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/sale/unit", response_model=IResponse[SaleUnitResponse])
@monitor_request
async def get_sale_unit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_sale_unit()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取销售单位失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="SaleUnitError"
        )
    except Exception as e:
        logger.error(f"获取销售单位失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )