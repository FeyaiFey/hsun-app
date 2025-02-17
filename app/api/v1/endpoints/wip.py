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
from app.core.deps import get_current_user
from app.models.user import User
from app.models.wip import FabWip
from app.schemas.wip import FabWipQuery
from app.services.wip_service import wip_service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/fab", response_model=IResponse[List[FabWip]])
@monitor_request
async def get_fab_wip(
    purchaseOrder: Optional[str] = Query(None, description="采购订单"),
    lot: Optional[str] = Query(None, description="批号"),
    itemName: Optional[str] = Query(None, description="产品名称"),
    forecastDate: Optional[date] = Query(None, description="预计交期"),
    supplier: Optional[str] = Query(None, description="供应商"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取晶圆厂WIP
    
    Args:
        purchaseOrder: 采购订单
        lot: 批号
        itemName: 产品名称
        forecastDate: 预计交期
        supplier: 供应商
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        WIP列表
    """
    try:
        # 注入数据库会话和缓存
        wip_service.db = db
        wip_service.cache = cache
        
        # 构建查询参数
        query_params = FabWipQuery(
            purchaseOrder=purchaseOrder,
            lot=lot,
            itemName=itemName,
            forecastDate=forecastDate,
            supplier=supplier
        )
        
        # 获取数据
        result = await wip_service.get_fab_wip_list(query_params)
        return CustomResponse.success(data=result)
        
    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="WipError"
        )
    except Exception as e:
        logger.error(f"获取晶圆厂WIP列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )


