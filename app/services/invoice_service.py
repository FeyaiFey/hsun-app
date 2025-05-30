import os
import re
import tempfile
from typing import List, Dict, Any, Tuple, Optional
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path
from fastapi import UploadFile
from sqlmodel import Session
import pdfplumber

from app.models.invoice import Invoice
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceExtractData,
    InvoiceExtractResponse, InvoiceConfirmData, InvoiceBatchConfirmRequest,
    InvoiceBatchConfirmResponse, InvoiceSearchRequest, InvoiceStatistics,
    InvoiceStatusUpdate, InvoiceStatusBatchUpdate
)
from app.schemas.file import FileUpload
from app.crud.invoice import InvoiceCRUD
from app.services.file_service import FileService
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.config import settings

class InvoiceService:
    """发票服务类"""

    @staticmethod
    def check_pdfplumber():
        """检查pdfplumber是否安装"""
        if pdfplumber is None:
            raise CustomException(
                code=500,
                message="pdfplumber库未安装，请先安装: pip install pdfplumber"
            )

    @staticmethod
    async def extract_invoice_data_from_pdf(pdf_path: str) -> Dict[str, str]:
        """从PDF文件提取发票数据"""
        InvoiceService.check_pdfplumber()
        
        data = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # 合并所有页面的文本
                all_text = ''
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        all_text += f'\n--- 第{page_num}页 ---\n' + page_text + '\n'
                
                # 使用合并后的文本进行处理
                text = all_text

            logger.info(f"正在处理PDF文件: {pdf_path}, 总页数: {len(pdf.pages)}")
            
            # 基础信息提取
            data['发票类型'] = InvoiceService._extract_field(text, r'(电子发票[（(][^)）]*[)）])')
            data['发票号码'] = InvoiceService._extract_field(text, r'发票号码[:：]\s*(\d+)')
            data['开票日期'] = InvoiceService._extract_field(text, r'开票日期[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)')
            
            # 购买方和销售方信息
            buyer_seller_match = re.search(r'购\s+名称[:：]\s*([^销]+)\s+销\s+名称[:：]\s*([^\n]+)', text)
            if buyer_seller_match:
                data['购买方名称'] = buyer_seller_match.group(1).strip()
                data['销售方名称'] = buyer_seller_match.group(2).strip()
            else:
                data['购买方名称'] = ''
                data['销售方名称'] = ''
            
            # 税号提取
            tax_codes = re.findall(r'统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]+)', text)
            if len(tax_codes) >= 2:
                data['购买方税号'] = tax_codes[0]
                data['销售方税号'] = tax_codes[1]
            elif len(tax_codes) == 1:
                data['购买方税号'] = tax_codes[0]
                data['销售方税号'] = ''
            else:
                data['购买方税号'] = ''
                data['销售方税号'] = ''
            
            # 金额信息
            data['合计金额'] = InvoiceService._extract_field(text, r'合\s*计\s*¥([0-9.,]+)')
            data['合计税额'] = InvoiceService._extract_field(text, r'合\s*计\s*¥[0-9.,]+\s*¥([0-9.,]+)')
            data['价税合计大写'] = InvoiceService._extract_field(text, r'价税合计[（(]大写[)）]\s*([^（(]+)')
            data['价税合计小写'] = InvoiceService._extract_field(text, r'[（(]小写[)）]\s*¥([0-9.,]+)')
            
            # 开票人
            data['开票人'] = InvoiceService._extract_field(text, r'开票人[:：]\s*([^\s\n]+)')
            
            return data
            
        except Exception as e:
            logger.error(f"提取PDF发票数据失败: {str(e)}")
            raise CustomException(
                code=400,
                message=f"提取PDF发票数据失败: {str(e)}"
            )

    @staticmethod
    def _extract_field(text: str, pattern: str) -> str:
        """提取单个字段"""
        try:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            return match.group(1).strip() if match else ''
        except Exception:
            return ''

    @staticmethod
    async def process_uploaded_pdfs(
        files: List[UploadFile],
        temp_dir: Optional[str] = None
    ) -> InvoiceExtractResponse:
        """处理上传的PDF文件并提取发票数据"""
        InvoiceService.check_pdfplumber()
        
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        extracted_data = []
        errors = []
        
        try:
            for file in files:
                if not file.filename.lower().endswith('.pdf'):
                    errors.append(f"文件 {file.filename} 不是PDF格式")
                    continue
                
                # 保存临时文件
                temp_file_path = os.path.join(temp_dir, file.filename)
                
                try:
                    content = await file.read()
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(content)
                    
                    # 提取发票数据
                    invoice_data = await InvoiceService.extract_invoice_data_from_pdf(temp_file_path)
                    invoice_data['文件名'] = file.filename
                    
                    # 转换为响应格式
                    extract_data = InvoiceExtractData(**invoice_data)
                    extracted_data.append(extract_data)
                    
                    logger.info(f"成功提取发票数据: {file.filename}")
                    
                except Exception as e:
                    error_msg = f"处理文件 {file.filename} 失败: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                        except Exception:
                            pass
            
            return InvoiceExtractResponse(
                success=len(extracted_data) > 0,
                data=extracted_data,
                errors=errors
            )
            
        finally:
            # 清理临时目录
            try:
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception:
                pass

    @staticmethod
    def _convert_confirm_data_to_create(confirm_data: InvoiceConfirmData) -> InvoiceCreate:
        """将前端确认数据转换为创建数据"""
        try:
            # 处理日期
            issue_date = None
            if confirm_data.issue_date:
                try:
                    # 尝试解析日期格式
                    if isinstance(confirm_data.issue_date, str):
                        if '年' in confirm_data.issue_date:
                            # 中文格式 "2024年1月1日"
                            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', confirm_data.issue_date)
                            if match:
                                year, month, day = match.groups()
                                issue_date = date(int(year), int(month), int(day))
                        else:
                            # 标准格式 "2024-01-01"
                            issue_date = datetime.strptime(confirm_data.issue_date, "%Y-%m-%d").date()
                    else:
                        issue_date = confirm_data.issue_date
                except Exception as e:
                    logger.warning(f"日期解析失败: {confirm_data.issue_date}, {str(e)}")
                    issue_date = None

            # 处理金额
            total_amount = None
            total_tax = None
            total_amount_in_numbers = None
            
            if confirm_data.total_amount:
                try:
                    # 清理金额字符串
                    amount_str = str(confirm_data.total_amount).replace(',', '').replace('¥', '').strip()
                    if amount_str:
                        total_amount = Decimal(amount_str)
                except Exception:
                    logger.warning(f"总金额解析失败: {confirm_data.total_amount}")

            if confirm_data.total_tax:
                try:
                    tax_str = str(confirm_data.total_tax).replace(',', '').replace('¥', '').strip()
                    if tax_str:
                        total_tax = Decimal(tax_str)
                except Exception:
                    logger.warning(f"总税额解析失败: {confirm_data.total_tax}")

            if confirm_data.total_amount_in_numbers:
                try:
                    numbers_str = str(confirm_data.total_amount_in_numbers).replace(',', '').replace('¥', '').strip()
                    if numbers_str:
                        total_amount_in_numbers = Decimal(numbers_str)
                except Exception:
                    logger.warning(f"小写金额解析失败: {confirm_data.total_amount_in_numbers}")

            return InvoiceCreate(
                file_name=confirm_data.file_name,
                invoice_type=confirm_data.invoice_type,
                invoice_number=confirm_data.invoice_number,
                issue_date=issue_date,
                issuer=confirm_data.issuer,
                buyer_name=confirm_data.buyer_name,
                buyer_tax_number=confirm_data.buyer_tax_number,
                seller_name=confirm_data.seller_name,
                seller_tax_number=confirm_data.seller_tax_number,
                total_amount=total_amount,
                total_tax=total_tax,
                total_amount_in_words=confirm_data.total_amount_in_words,
                total_amount_in_numbers=total_amount_in_numbers,
                status=confirm_data.status  # 添加状态字段
            )
        except Exception as e:
            logger.error(f"转换确认数据失败: {str(e)}")
            raise CustomException(
                code=400,
                message=f"数据转换失败: {str(e)}"
            )

    @staticmethod
    async def confirm_and_save_invoices(
        db: Session,
        request: InvoiceBatchConfirmRequest,
        uploaded_files: List[UploadFile],
        user_id: int,
        storage_path: Path
    ) -> InvoiceBatchConfirmResponse:
        """确认并保存发票数据"""
        success_count = 0
        error_count = 0
        success_invoices = []
        error_details = []
        
        # 创建文件名到UploadFile的映射
        file_map = {file.filename: file for file in uploaded_files}
        
        try:
            # 开始数据库事务
            for confirm_data in request.invoices:
                try:
                    # 转换数据格式
                    invoice_create = InvoiceService._convert_confirm_data_to_create(confirm_data)
                    
                    # 上传对应的文件
                    uploaded_file = None
                    if confirm_data.file_name in file_map:
                        upload_file = file_map[confirm_data.file_name]
                        
                        # 准备文件上传数据
                        file_upload_data = FileUpload(
                            folder_id=request.folder_id,
                            is_public=False,
                            tags="invoice"
                        )
                        
                        # 上传文件
                        uploaded_file = await FileService.upload_file(
                            upload_file,
                            db,
                            file_upload_data,
                            user_id,
                            storage_path
                        )
                        
                        logger.info(f"文件上传成功: {confirm_data.file_name}")
                    
                    # 创建发票记录
                    db_invoice = await InvoiceCRUD.create_invoice(db, invoice_create)
                    success_invoices.append(db_invoice)
                    success_count += 1
                    
                    logger.info(f"发票保存成功: {confirm_data.invoice_number}, 状态: {db_invoice.status_text}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"保存发票失败 {confirm_data.file_name}: {str(e)}"
                    error_details.append({
                        "file_name": confirm_data.file_name,
                        "invoice_number": confirm_data.invoice_number,
                        "error": str(e)
                    })
                    logger.error(error_msg)
                    
                    # 如果是数据库相关错误，回滚当前操作
                    try:
                        db.rollback()
                    except Exception:
                        pass
            
            # 如果有任何成功的记录，提交事务
            if success_count > 0:
                db.commit()
                logger.info(f"批量保存发票完成: 成功 {success_count} 条, 失败 {error_count} 条")
            
            return InvoiceBatchConfirmResponse(
                success_count=success_count,
                error_count=error_count,
                success_invoices=success_invoices,
                error_details=error_details
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"批量保存发票失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"批量保存发票失败: {str(e)}"
            )

    @staticmethod
    async def update_invoice_status(
        db: Session,
        invoice_id: int,
        status_update: InvoiceStatusUpdate,
        user_id: int
    ) -> Invoice:
        """更新发票状态"""
        try:
            # 检查发票是否存在
            invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
            if not invoice:
                raise CustomException(
                    code=404,
                    message="发票不存在"
                )
            
            # 检查状态是否相同
            if invoice.status == status_update.status:
                raise CustomException(
                    code=400,
                    message=f"发票已经是{invoice.status_text}状态"
                )
            
            # 更新状态
            updated_invoice = await InvoiceCRUD.update_invoice_status(
                db, invoice_id, status_update, user_id
            )
            
            status_text = "正常" if status_update.status == 1 else "作废"
            logger.info(f"发票状态更新成功: {invoice.invoice_number} -> {status_text}")
            
            return updated_invoice
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"更新发票状态失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"更新发票状态失败: {str(e)}"
            )

    @staticmethod
    async def batch_update_invoice_status(
        db: Session,
        batch_update: InvoiceStatusBatchUpdate,
        user_id: int
    ) -> Dict[str, Any]:
        """批量更新发票状态"""
        try:
            # 验证发票ID列表
            if not batch_update.invoice_ids:
                raise CustomException(
                    code=400,
                    message="请提供要更新的发票ID列表"
                )
            
            # 执行批量更新
            result = await InvoiceCRUD.batch_update_invoice_status(
                db, batch_update, user_id
            )
            
            status_text = "正常" if batch_update.status == 1 else "作废"
            logger.info(f"批量更新发票状态完成: {result['success_count']} 条成功更新为{status_text}")
            
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"批量更新发票状态失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"批量更新发票状态失败: {str(e)}"
            )

    @staticmethod
    async def void_invoice(db: Session, invoice_id: int, user_id: int, reason: str = None) -> Invoice:
        """作废发票"""
        status_update = InvoiceStatusUpdate(status=0, reason=reason)
        return await InvoiceService.update_invoice_status(db, invoice_id, status_update, user_id)

    @staticmethod
    async def activate_invoice(db: Session, invoice_id: int, user_id: int, reason: str = None) -> Invoice:
        """激活发票（恢复正常状态）"""
        status_update = InvoiceStatusUpdate(status=1, reason=reason)
        return await InvoiceService.update_invoice_status(db, invoice_id, status_update, user_id)

    @staticmethod
    async def get_invoice_statistics(db: Session) -> InvoiceStatistics:
        """获取发票统计信息"""
        try:
            return await InvoiceCRUD.get_invoice_statistics(db)
        except Exception as e:
            logger.error(f"获取发票统计失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"获取发票统计失败: {str(e)}"
            )

    @staticmethod
    async def search_invoices(
        db: Session,
        search_params: InvoiceSearchRequest,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Invoice], int]:
        """搜索发票"""
        try:
            invoices = await InvoiceCRUD.search_invoices(db, search_params, skip, limit)
            total = await InvoiceCRUD.get_invoice_count(db, search_params)
            return invoices, total
        except Exception as e:
            logger.error(f"搜索发票失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"搜索发票失败: {str(e)}"
            )

    @staticmethod
    async def get_active_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """获取正常状态的发票"""
        try:
            return await InvoiceCRUD.get_active_invoices(db, skip, limit)
        except Exception as e:
            logger.error(f"获取正常发票失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"获取正常发票失败: {str(e)}"
            )

    @staticmethod
    async def get_void_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """获取作废状态的发票"""
        try:
            return await InvoiceCRUD.get_void_invoices(db, skip, limit)
        except Exception as e:
            logger.error(f"获取作废发票失败: {str(e)}")
            raise CustomException(
                code=500,
                message=f"获取作废发票失败: {str(e)}"
            ) 