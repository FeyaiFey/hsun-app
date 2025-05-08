import io
import uuid
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.core.exceptions import CustomException
from app.core.logger import logger
from app.models.sale import Sale
from app.schemas.sale import SaleTableQuery, SaleTableResponse, SaleTargetCreate, SaleTargetUpdate

class CRUSale:
    """销售CRUD操作类"""

    def _clean_input(self, value: str) -> str:
        """清理输入参数，移除潜在的危险字符
        
        Args:
            value: 输入字符串
            
        Returns:
            清理后的字符串
        """
        if value is None:
            return ""
        # 移除常见的 SQL 注入字符
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_']
        cleaned = str(value)
        for char in dangerous_chars:
            cleaned = cleaned.replace(char, '')
        return cleaned
    
    async def get_sale_table(self, db: Session, params: SaleTableQuery) -> List[SaleTableResponse]:
        """获取销售目标列表"""
        try:
            # 清理输入参数
            year = self._clean_input(params.year)
            month = self._clean_input(params.month)
            yearmonth = self._clean_input(params.yearmonth)

            # 构建查询条件
            query = select(Sale).order_by(Sale.CreatedAt.desc())
            if year:
                query = query.where(Sale.Year == year)
            if month:
                query = query.where(Sale.Month == month)
            if yearmonth:
                query = query.where(Sale.YearMonth == yearmonth)
            
            # 获取总记录数
            total_query = select(text("COUNT(*)")).select_from(query.subquery())
            total = db.exec(total_query).first()
            
            # 添加分页
            query = query.offset((params.pageIndex - 1) * params.pageSize).limit(params.pageSize)
            
            # 执行查询
            sale_targets = db.exec(query).all()
            
            return SaleTableResponse(
                list=sale_targets,
                total=total
            )
        except Exception as e:
            logger.error(f"获取销售目标列表失败: {str(e)}")
            raise CustomException(f"获取销售目标列表失败: {str(e)}")
    
    async def create_sale_target(self, db: Session, user_name: str, params: SaleTargetCreate) -> SaleTableResponse:
        """创建销售目标"""
        try:
            # 清理输入参数
            year = self._clean_input(params.year)
            month = self._clean_input(params.month)
            yearmonth = self._clean_input(params.yearmonth)
            monthly_target = self._clean_input(params.monthly_target)
            annual_target = self._clean_input(params.annual_target)

            # 检查数据是否已经存在
            if year:
                query = select(Sale).where(Sale.Year == year)
                sale_target = db.exec(query).all()
                if sale_target:
                    raise CustomException(f"{year}年的销售目标已存在")
            
            if month and yearmonth:
                query = select(Sale).where(Sale.Month == month, Sale.YearMonth == yearmonth)
                sale_target = db.exec(query).all()
                if sale_target:
                    raise CustomException(f"{yearmonth}年{month}月的销售目标已存在")
            
            # 创建新的销售目标
            if year:
                new_target = Sale(
                    Id=uuid.uuid4(),
                    Year=year,
                    Month=None,
                    YearMonth=None,
                    MonthlyTarget=None,
                    AnnualTarget=annual_target,
                    CreatedBy=user_name,
                    CreatedAt=datetime.now(),
                    UpdatedAt=datetime.now()
                )
                db.add(new_target)
                db.commit()
                db.refresh(new_target)
                return new_target
            elif month and yearmonth:
                new_target = Sale(
                    Id=uuid.uuid4(),
                    Year=None,
                    Month=month,
                    YearMonth=yearmonth,
                    MonthlyTarget=monthly_target,
                    AnnualTarget=None,
                    CreatedBy=user_name,
                    CreatedAt=datetime.now(),
                    UpdatedAt=datetime.now()
                )
                db.add(new_target)
                db.commit()
                db.refresh(new_target)
                return new_target
            else:
                raise CustomException("无效的输入参数")
        except Exception as e:
            logger.error(f"创建销售目标失败: {str(e)}")
            raise CustomException(f"创建销售目标失败: {str(e)}")

    async def update_sale_target(self, db: Session, params: SaleTargetUpdate) -> SaleTableResponse:
        """更新销售目标"""
        try:
            # 清理输入参数
            id = self._clean_input(params.id)
            year = self._clean_input(params.year)
            month = self._clean_input(params.month)
            yearmonth = self._clean_input(params.yearmonth)
            monthly_target = self._clean_input(params.monthly_target)
            annual_target = self._clean_input(params.annual_target)

            # 检查数据是否存在
            query = select(Sale).where(Sale.Id == id)
            sale_target = db.exec(query).first()
            if not sale_target:
                raise CustomException("销售目标不存在")
            
            # 更新销售目标
            if year:
                sale_target.Year = year
                sale_target.MonthlyTarget = None
                sale_target.AnnualTarget = annual_target
            elif month and yearmonth:
                sale_target.Month = month
                sale_target.YearMonth = yearmonth
                sale_target.MonthlyTarget = monthly_target
                sale_target.AnnualTarget = None
            else:
                raise CustomException("无效的输入参数")
            
            sale_target.UpdatedAt = datetime.now()
            db.commit()
            db.refresh(sale_target)
            return sale_target
        except Exception as e:
            logger.error(f"更新销售目标失败: {str(e)}")
            raise CustomException(f"更新销售目标失败: {str(e)}")

    async def delete_sale_target(self, db: Session, id: UUID) -> SaleTableResponse:
        """删除销售目标"""
        try:
            # 检查数据是否存在
            query = select(Sale).where(Sale.Id == id)
            sale_target = db.exec(query).first()
            if not sale_target:
                raise CustomException("销售目标不存在")
            
            # 删除销售目标
            db.delete(sale_target)
            db.commit()
            return sale_target
        except Exception as e:
            logger.error(f"删除销售目标失败: {str(e)}")
            raise CustomException(f"删除销售目标失败: {str(e)}")

