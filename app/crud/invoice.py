from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func, and_, or_
from sqlalchemy import text
from datetime import datetime, date
from decimal import Decimal

from app.models.invoice import Invoice
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceSearchRequest,
    InvoiceStatistics, InvoiceStatusUpdate, InvoiceStatusBatchUpdate
)
from app.core.logger import logger

class InvoiceCRUD:
    """发票数据库操作类"""

    @staticmethod
    async def create_invoice(db: Session, invoice_data: InvoiceCreate) -> Invoice:
        """创建发票"""
        try:
            # 检查发票号码是否已存在
            existing = await InvoiceCRUD.get_invoice_by_number(db, invoice_data.invoice_number)
            if existing:
                raise ValueError(f"发票号码 {invoice_data.invoice_number} 已存在")

            # 创建发票对象
            db_invoice = Invoice(**invoice_data.dict())
            db.add(db_invoice)
            db.commit()
            db.refresh(db_invoice)
            
            logger.info(f"创建发票成功: {invoice_data.invoice_number}")
            return db_invoice
        except Exception as e:
            db.rollback()
            logger.error(f"创建发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_invoice(db: Session, invoice_id: int) -> Optional[Invoice]:
        """根据ID获取发票"""
        try:
            statement = select(Invoice).where(Invoice.invoice_id == invoice_id)
            result = db.exec(statement)
            invoice = result.first()
            return invoice
        except Exception as e:
            logger.error(f"获取发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
        """根据发票号码获取发票"""
        try:
            statement = select(Invoice).where(Invoice.invoice_number == invoice_number)
            result = db.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"根据号码获取发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_invoices(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "invoice_id",
        order_desc: bool = False,
        status_filter: Optional[int] = None
    ) -> List[Invoice]:
        """获取发票列表"""
        try:
            statement = select(Invoice)
            
            # 状态过滤
            if status_filter is not None:
                statement = statement.where(Invoice.status == status_filter)
            
            # 排序
            if order_desc:
                if order_by == "created_at":
                    statement = statement.order_by(Invoice.created_at.desc())
                elif order_by == "issue_date":
                    statement = statement.order_by(Invoice.issue_date.desc())
                elif order_by == "total_amount":
                    statement = statement.order_by(Invoice.total_amount.desc())
                elif order_by == "invoice_id":
                    statement = statement.order_by(Invoice.invoice_id.desc())
                else:
                    statement = statement.order_by(Invoice.created_at.desc())
            else:
                if order_by == "created_at":
                    statement = statement.order_by(Invoice.created_at.asc())
                elif order_by == "issue_date":
                    statement = statement.order_by(Invoice.issue_date.asc())
                elif order_by == "total_amount":
                    statement = statement.order_by(Invoice.total_amount.asc())
                elif order_by == "invoice_id":
                    statement = statement.order_by(Invoice.invoice_id.asc())
                else:
                    statement = statement.order_by(Invoice.created_at.asc())
            
            statement = statement.offset(skip).limit(limit)
            result = db.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"获取发票列表失败: {str(e)}")
            raise

    @staticmethod
    async def update_invoice(db: Session, invoice_id: int, invoice_update: InvoiceUpdate) -> Optional[Invoice]:
        """更新发票"""
        try:
            db_invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
            if not db_invoice:
                return None

            # 如果更新发票号码，检查是否重复
            if invoice_update.invoice_number and invoice_update.invoice_number != db_invoice.invoice_number:
                existing = await InvoiceCRUD.get_invoice_by_number(db, invoice_update.invoice_number)
                if existing:
                    raise ValueError(f"发票号码 {invoice_update.invoice_number} 已存在")

            # 更新字段
            update_data = invoice_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_invoice, field, value)
            
            # 更新时间
            db_invoice.updated_at = datetime.now()
            
            db.commit()
            db.refresh(db_invoice)
            
            logger.info(f"更新发票成功: {invoice_id}")
            return db_invoice
        except Exception as e:
            db.rollback()
            logger.error(f"更新发票失败: {str(e)}")
            raise

    @staticmethod
    async def update_invoice_status(
        db: Session, 
        invoice_id: int, 
        status_update: InvoiceStatusUpdate,
        updated_by: int
    ) -> Optional[Invoice]:
        """更新发票状态"""
        try:
            db_invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
            if not db_invoice:
                return None

            old_status = db_invoice.status
            
            # 更新状态
            db_invoice.status = status_update.status
            db_invoice.updated_at = datetime.now()
            
            db.commit()
            db.refresh(db_invoice)
            
            logger.info(f"更新发票状态成功: {invoice_id}, {old_status} -> {status_update.status}")
            return db_invoice
        except Exception as e:
            db.rollback()
            logger.error(f"更新发票状态失败: {str(e)}")
            raise

    @staticmethod
    async def batch_update_invoice_status(
        db: Session,
        batch_update: InvoiceStatusBatchUpdate,
        updated_by: int
    ) -> Dict[str, Any]:
        """批量更新发票状态"""
        try:
            success_count = 0
            error_count = 0
            success_invoices = []
            error_details = []

            for invoice_id in batch_update.invoice_ids:
                try:
                    db_invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
                    if not db_invoice:
                        error_count += 1
                        error_details.append({
                            "invoice_id": invoice_id,
                            "error": "发票不存在"
                        })
                        continue

                    old_status = db_invoice.status
                    db_invoice.status = batch_update.status
                    db_invoice.updated_at = datetime.now()
                    
                    success_invoices.append(db_invoice)
                    success_count += 1
                    
                    logger.info(f"批量更新发票状态: {invoice_id}, {old_status} -> {batch_update.status}")
                    
                except Exception as e:
                    error_count += 1
                    error_details.append({
                        "invoice_id": invoice_id,
                        "error": str(e)
                    })

            if success_count > 0:
                db.commit()
                # 刷新所有成功更新的发票
                for invoice in success_invoices:
                    db.refresh(invoice)
            
            return {
                "success_count": success_count,
                "error_count": error_count,
                "success_invoices": success_invoices,
                "error_details": error_details
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"批量更新发票状态失败: {str(e)}")
            raise

    @staticmethod
    async def delete_invoice(db: Session, invoice_id: int) -> bool:
        """删除发票"""
        try:
            db_invoice = await InvoiceCRUD.get_invoice(db, invoice_id)
            if not db_invoice:
                return False

            db.delete(db_invoice)
            db.commit()
            
            logger.info(f"删除发票成功: {invoice_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除发票失败: {str(e)}")
            raise

    @staticmethod
    async def search_invoices(
        db: Session,
        search_params: InvoiceSearchRequest,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """搜索发票"""
        try:
            statement = select(Invoice)
            conditions = []

            # 发票号码搜索
            if search_params.invoice_number:
                conditions.append(Invoice.invoice_number.contains(search_params.invoice_number))

            # 购买方名称搜索
            if search_params.buyer_name:
                conditions.append(Invoice.buyer_name.contains(search_params.buyer_name))

            # 销售方名称搜索
            if search_params.seller_name:
                conditions.append(Invoice.seller_name.contains(search_params.seller_name))

            # 开票日期范围搜索
            if search_params.issue_date_start:
                conditions.append(Invoice.issue_date >= search_params.issue_date_start)
            if search_params.issue_date_end:
                conditions.append(Invoice.issue_date <= search_params.issue_date_end)

            # 金额范围搜索
            if search_params.amount_min:
                conditions.append(Invoice.total_amount >= search_params.amount_min)
            if search_params.amount_max:
                conditions.append(Invoice.total_amount <= search_params.amount_max)

            # 状态搜索
            if search_params.status is not None:
                conditions.append(Invoice.status == search_params.status)

            # 应用条件
            if conditions:
                statement = statement.where(and_(*conditions))

            # 排序和分页
            statement = statement.order_by(Invoice.invoice_id.asc()).offset(skip).limit(limit)
            
            result = db.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"搜索发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_invoice_count(db: Session, search_params: Optional[InvoiceSearchRequest] = None) -> int:
        """获取发票总数"""
        try:
            statement = select(func.count(Invoice.invoice_id))
            
            if search_params:
                conditions = []
                if search_params.invoice_number:
                    conditions.append(Invoice.invoice_number.contains(search_params.invoice_number))
                if search_params.buyer_name:
                    conditions.append(Invoice.buyer_name.contains(search_params.buyer_name))
                if search_params.seller_name:
                    conditions.append(Invoice.seller_name.contains(search_params.seller_name))
                if search_params.issue_date_start:
                    conditions.append(Invoice.issue_date >= search_params.issue_date_start)
                if search_params.issue_date_end:
                    conditions.append(Invoice.issue_date <= search_params.issue_date_end)
                if search_params.amount_min:
                    conditions.append(Invoice.total_amount >= search_params.amount_min)
                if search_params.amount_max:
                    conditions.append(Invoice.total_amount <= search_params.amount_max)
                if search_params.status is not None:
                    conditions.append(Invoice.status == search_params.status)
                
                if conditions:
                    statement = statement.where(and_(*conditions))
            
            result = db.exec(statement)
            return result.one()
        except Exception as e:
            logger.error(f"获取发票总数失败: {str(e)}")
            raise

    @staticmethod
    async def get_invoice_statistics(db: Session) -> InvoiceStatistics:
        """获取发票统计信息"""
        try:
            # 总数和总金额
            total_stats_query = select(
                func.count(Invoice.invoice_id).label("total_count"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("total_amount"),
                func.coalesce(func.sum(Invoice.total_tax), 0).label("total_tax"),
                func.coalesce(func.avg(Invoice.total_amount), 0).label("average_amount")
            )
            
            total_stats = db.exec(total_stats_query).first()

            # 状态统计
            active_count_query = select(func.count(Invoice.invoice_id)).where(Invoice.status == 1)
            active_count = db.exec(active_count_query).one()
            
            void_count_query = select(func.count(Invoice.invoice_id)).where(Invoice.status == 0)
            void_count = db.exec(void_count_query).one()

            # 本月统计
            current_month_start = date.today().replace(day=1)
            monthly_stats_query = select(
                func.count(Invoice.invoice_id).label("this_month_count"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("this_month_amount")
            ).where(Invoice.created_at >= current_month_start)
            
            monthly_stats = db.exec(monthly_stats_query).first()

            return InvoiceStatistics(
                total_count=total_stats.total_count or 0,
                active_count=active_count or 0,
                void_count=void_count or 0,
                total_amount=Decimal(str(total_stats.total_amount or 0)),
                total_tax=Decimal(str(total_stats.total_tax or 0)),
                average_amount=Decimal(str(total_stats.average_amount or 0)),
                this_month_count=monthly_stats.this_month_count or 0,
                this_month_amount=Decimal(str(monthly_stats.this_month_amount or 0))
            )
        except Exception as e:
            logger.error(f"获取发票统计失败: {str(e)}")
            raise

    @staticmethod
    async def batch_create_invoices(db: Session, invoices_data: List[InvoiceCreate]) -> List[Invoice]:
        """批量创建发票"""
        try:
            created_invoices = []
            
            # 检查发票号码重复
            invoice_numbers = [inv.invoice_number for inv in invoices_data]
            for number in invoice_numbers:
                existing = await InvoiceCRUD.get_invoice_by_number(db, number)
                if existing:
                    raise ValueError(f"发票号码 {number} 已存在")

            # 批量创建
            for invoice_data in invoices_data:
                db_invoice = Invoice(**invoice_data.dict())
                db.add(db_invoice)
                created_invoices.append(db_invoice)

            db.commit()
            
            # 刷新所有对象
            for invoice in created_invoices:
                db.refresh(invoice)
            
            logger.info(f"批量创建发票成功: {len(created_invoices)} 条")
            return created_invoices
        except Exception as e:
            db.rollback()
            logger.error(f"批量创建发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_recent_invoices(db: Session, days: int = 7, limit: int = 10) -> List[Invoice]:
        """获取最近的发票"""
        try:
            from datetime import timedelta
            recent_date = datetime.now() - timedelta(days=days)
            
            statement = select(Invoice).where(
                Invoice.created_at >= recent_date
            ).order_by(Invoice.created_at.desc()).limit(limit)
            
            result = db.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"获取最近发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_active_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """获取正常状态的发票"""
        try:
            statement = select(Invoice).where(
                Invoice.status == 1
            ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
            
            result = db.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"获取正常发票失败: {str(e)}")
            raise

    @staticmethod
    async def get_void_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """获取作废状态的发票"""
        try:
            statement = select(Invoice).where(
                Invoice.status == 0
            ).order_by(Invoice.updated_at.desc()).offset(skip).limit(limit)
            
            result = db.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"获取作废发票失败: {str(e)}")
            raise 