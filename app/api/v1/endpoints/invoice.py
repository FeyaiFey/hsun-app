from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Path as PathParam, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from pathlib import Path

from app.db.session import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import (
    InvoiceResponse, InvoiceUpdate, InvoiceCreate,
    InvoiceExtractResponse, InvoiceBatchConfirmRequest, InvoiceBatchConfirmResponse,
    InvoiceSearchRequest, InvoiceStatistics, InvoiceStatusUpdate, InvoiceStatusBatchUpdate
)
from app.schemas.response import IResponse
from app.crud.invoice import InvoiceCRUD
from app.services.invoice_service import InvoiceService
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User
from app.core.monitor import monitor_request
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.core.config import settings

router = APIRouter()

# 文件存储路径
INVOICE_STORAGE_PATH = Path("uploads/invoices")

@router.post("/extract/", response_model=IResponse[InvoiceExtractResponse])
@monitor_request
async def extract_invoice_data(
    files: List[UploadFile] = File(..., description="PDF发票文件"),
    current_user: User = Depends(get_current_active_user)
):
    """从PDF文件提取发票数据"""
    try:
        if not files:
            return CustomResponse.error(
                code=status.HTTP_400_BAD_REQUEST,
                message="请至少上传一个PDF文件",
                name="NoFilesProvided"
            )

        # 检查文件格式
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                return CustomResponse.error(
                    code=status.HTTP_400_BAD_REQUEST,
                    message=f"文件 {file.filename} 不是PDF格式",
                    name="InvalidFileFormat"
                )

        # 处理PDF文件并提取数据
        result = await InvoiceService.process_uploaded_pdfs(files)
        
        if result.success:
            message = f"成功提取 {len(result.data)} 个发票数据"
            if result.errors:
                message += f"，{len(result.errors)} 个文件处理失败"
        else:
            message = "所有文件处理失败"

        return CustomResponse.success(data=result, message=message)

    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="InvoiceExtractionError"
        )
    except Exception as e:
        logger.error(f"提取发票数据失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/confirm/", response_model=IResponse[InvoiceBatchConfirmResponse])
@monitor_request
async def confirm_and_save_invoices_with_files(
    files: List[UploadFile] = File(..., description="对应的PDF文件"),
    invoice_data: str = Form(..., description="发票确认数据JSON字符串"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """确认并保存发票数据（包含文件上传）"""
    try:
        # 解析JSON字符串
        import json
        try:
            request_data = json.loads(invoice_data)
            batch_request = InvoiceBatchConfirmRequest(**request_data)
        except (json.JSONDecodeError, ValueError) as e:
            return CustomResponse.error(
                code=status.HTTP_400_BAD_REQUEST,
                message=f"请求数据格式错误: {str(e)}",
                name="InvalidRequestFormat"
            )

        if not batch_request.invoices:
            return CustomResponse.error(
                code=status.HTTP_400_BAD_REQUEST,
                message="请提供要保存的发票数据",
                name="NoInvoiceDataProvided"
            )

        # 确保存储目录存在
        INVOICE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

        # 处理发票数据和文件上传
        result = await InvoiceService.confirm_and_save_invoices(
            db=db,
            request=batch_request,
            uploaded_files=files,
            user_id=current_user.id,
            storage_path=INVOICE_STORAGE_PATH
        )

        message = f"批量保存完成: 成功 {result.success_count} 条, 失败 {result.error_count} 条"
        
        return CustomResponse.success(data=result, message=message)

    except CustomException as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=e.message,
            name="InvoiceConfirmError"
        )
    except Exception as e:
        logger.error(f"确认保存发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/", response_model=IResponse[List[InvoiceResponse]])
@monitor_request
async def get_invoices(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    order_by: str = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序"),
    status_filter: Optional[int] = Query(None, description="状态过滤：0-作废，1-正常", ge=0, le=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取发票列表"""
    try:
        invoices = await InvoiceCRUD.get_invoices(
            db=db,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            status_filter=status_filter
        )
        
        return CustomResponse.success(data=invoices, message="获取发票列表成功")

    except Exception as e:
        logger.error(f"获取发票列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/active/", response_model=IResponse[List[InvoiceResponse]])
@monitor_request
async def get_active_invoices(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取正常状态的发票"""
    try:
        invoices = await InvoiceService.get_active_invoices(db, skip, limit)
        return CustomResponse.success(data=invoices, message="获取正常发票列表成功")

    except Exception as e:
        logger.error(f"获取正常发票列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/void/", response_model=IResponse[List[InvoiceResponse]])
@monitor_request
async def get_void_invoices(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取作废状态的发票"""
    try:
        invoices = await InvoiceService.get_void_invoices(db, skip, limit)
        return CustomResponse.success(data=invoices, message="获取作废发票列表成功")

    except Exception as e:
        logger.error(f"获取作废发票列表失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/{invoice_id}/status", response_model=IResponse[InvoiceResponse])
@monitor_request
async def update_invoice_status(
    status_update: InvoiceStatusUpdate,
    invoice_id: int = PathParam(..., description="发票ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新发票状态"""
    try:
        updated_invoice = await InvoiceService.update_invoice_status(
            db=db,
            invoice_id=invoice_id,
            status_update=status_update,
            user_id=current_user.id
        )
        
        status_text = "正常" if status_update.status == 1 else "作废"
        return CustomResponse.success(
            data=updated_invoice, 
            message=f"发票状态已更新为{status_text}"
        )

    except CustomException as e:
        return CustomResponse.error(
            code=e.code,
            message=e.message,
            name="StatusUpdateError"
        )
    except Exception as e:
        logger.error(f"更新发票状态失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/{invoice_id}/void", response_model=IResponse[InvoiceResponse])
@monitor_request
async def void_invoice(
    invoice_id: int = PathParam(..., description="发票ID"),
    reason: Optional[str] = Query(None, description="作废原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """作废发票"""
    try:
        voided_invoice = await InvoiceService.void_invoice(
            db=db,
            invoice_id=invoice_id,
            user_id=current_user.id,
            reason=reason
        )
        
        return CustomResponse.success(
            data=voided_invoice, 
            message="发票已作废"
        )

    except CustomException as e:
        return CustomResponse.error(
            code=e.code,
            message=e.message,
            name="VoidInvoiceError"
        )
    except Exception as e:
        logger.error(f"作废发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/{invoice_id}/activate", response_model=IResponse[InvoiceResponse])
@monitor_request
async def activate_invoice(
    invoice_id: int = PathParam(..., description="发票ID"),
    reason: Optional[str] = Query(None, description="激活原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """激活发票（恢复正常状态）"""
    try:
        activated_invoice = await InvoiceService.activate_invoice(
            db=db,
            invoice_id=invoice_id,
            user_id=current_user.id,
            reason=reason
        )
        
        return CustomResponse.success(
            data=activated_invoice, 
            message="发票已激活"
        )

    except CustomException as e:
        return CustomResponse.error(
            code=e.code,
            message=e.message,
            name="ActivateInvoiceError"
        )
    except Exception as e:
        logger.error(f"激活发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/batch/status", response_model=IResponse[Dict])
@monitor_request
async def batch_update_invoice_status(
    batch_update: InvoiceStatusBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量更新发票状态"""
    try:
        result = await InvoiceService.batch_update_invoice_status(
            db=db,
            batch_update=batch_update,
            user_id=current_user.id
        )
        
        status_text = "正常" if batch_update.status == 1 else "作废"
        message = f"批量状态更新完成: 成功 {result['success_count']} 条更新为{status_text}, 失败 {result['error_count']} 条"
        
        return CustomResponse.success(data=result, message=message)

    except CustomException as e:
        return CustomResponse.error(
            code=e.code,
            message=e.message,
            name="BatchStatusUpdateError"
        )
    except Exception as e:
        logger.error(f"批量更新发票状态失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/{invoice_id}", response_model=IResponse[InvoiceResponse])
@monitor_request
async def get_invoice(
    invoice_id: int = PathParam(..., description="发票ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取发票详情"""
    try:
        invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
        if not invoice:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="发票不存在",
                name="InvoiceNotFound"
            )

        return CustomResponse.success(data=invoice, message="获取发票详情成功")

    except Exception as e:
        logger.error(f"获取发票详情失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.put("/{invoice_id}", response_model=IResponse[InvoiceResponse])
@monitor_request
async def update_invoice(
    invoice_update: InvoiceUpdate,
    invoice_id: int = PathParam(..., description="发票ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新发票信息"""
    try:
        invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
        if not invoice:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="发票不存在",
                name="InvoiceNotFound"
            )

        updated_invoice = await InvoiceCRUD.update_invoice(db, invoice_id, invoice_update)
        return CustomResponse.success(data=updated_invoice, message="发票更新成功")

    except ValueError as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
            name="ValidationError"
        )
    except Exception as e:
        logger.error(f"更新发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.delete("/{invoice_id}", response_model=IResponse)
@monitor_request
async def delete_invoice(
    invoice_id: int = PathParam(..., description="发票ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除发票"""
    try:
        invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
        if not invoice:
            return CustomResponse.error(
                code=status.HTTP_404_NOT_FOUND,
                message="发票不存在",
                name="InvoiceNotFound"
            )

        success = await InvoiceCRUD.delete_invoice(db, invoice_id)
        if success:
            return CustomResponse.success(message="发票删除成功")
        else:
            return CustomResponse.error(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="删除发票失败",
                name="DeleteInvoiceError"
            )

    except Exception as e:
        logger.error(f"删除发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/search/", response_model=IResponse[Dict])
@monitor_request
async def search_invoices(
    search_params: InvoiceSearchRequest,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """搜索发票"""
    try:
        invoices, total = await InvoiceService.search_invoices(
            db=db,
            search_params=search_params,
            skip=skip,
            limit=limit
        )

        result = {
            "invoices": invoices,
            "total": total,
            "skip": skip,
            "limit": limit
        }

        return CustomResponse.success(data=result, message="搜索发票完成")

    except Exception as e:
        logger.error(f"搜索发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/statistics/summary", response_model=IResponse[InvoiceStatistics])
@monitor_request
async def get_invoice_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取发票统计信息"""
    try:
        statistics = await InvoiceService.get_invoice_statistics(db)
        return CustomResponse.success(data=statistics, message="获取发票统计成功")

    except Exception as e:
        logger.error(f"获取发票统计失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.get("/recent/list", response_model=IResponse[List[InvoiceResponse]])
@monitor_request
async def get_recent_invoices(
    days: int = Query(7, ge=1, le=30, description="最近天数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取最近的发票"""
    try:
        invoices = await InvoiceCRUD.get_recent_invoices(db, days, limit)
        return CustomResponse.success(data=invoices, message="获取最近发票成功")

    except Exception as e:
        logger.error(f"获取最近发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

@router.post("/create/", response_model=IResponse[InvoiceResponse])
@monitor_request
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """手动创建发票"""
    try:
        invoice = await InvoiceCRUD.create_invoice(db, invoice_data)
        return CustomResponse.success(data=invoice, message="创建发票成功")

    except ValueError as e:
        return CustomResponse.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
            name="ValidationError"
        )
    except Exception as e:
        logger.error(f"创建发票失败: {str(e)}")
        return CustomResponse.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        ) 