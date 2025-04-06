from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import Any, List, Optional
from datetime import date, datetime
import io
from fastapi.responses import StreamingResponse
from urllib.parse import quote

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
from app.schemas.report import GlobalReport
from app.services.e10_service import E10Service

router = APIRouter()

# 创建缓存实例
cache = MemoryCache()

@router.get("/global", response_model=IResponse[List[GlobalReport]])
@monitor_request
async def get_global_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取综合报表"""
    try:
        e10_service = E10Service(db, cache)
        result = await e10_service.get_global_report()
        return CustomResponse.success(data=result)
    except CustomException as e:
        logger.error(f"获取综合报表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="GlobalReportError"
        )
    except Exception as e:
        logger.error(f"获取综合报表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.DB_ERROR),
            name="GlobalReportError"
        )

@router.get("/global/export")
@monitor_request
async def export_global_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """导出外协报表"""
    try:
        e10_service = E10Service(db)
        excel_data = await e10_service.export_global_report()
        # 生成文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"外协报表_{current_time}.xlsx"
        
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
        logger.error(f"导出外协报表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=e.message,
            name="AssyError"
        )
    except Exception as e:
        logger.error(f"导出外协报表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="导出外协报表失败",
            name="AssyError"
        )