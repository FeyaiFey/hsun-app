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
from app.schemas.sale import (
    SaleTableQuery, SaleTableResponse, SaleTargetCreate, SaleTargetUpdate,
    SaleTargetSummaryQuery, SaleTargetSummary, SaleTargetSummaryResponse,
    SaleTargetDetailQuery, SaleTargetDetail, SaleTargetDetailResponse
)

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

    async def get_sale_target_summary(self, db: Session, params: SaleTargetSummaryQuery) -> List[SaleTargetSummaryResponse]:
        """获取销售目标汇总"""
        try:
            # 清理输入参数
            year = self._clean_input(params.year)
            month = self._clean_input(params.month)

            # 绑定参数
            where_clause = ""
            if year:
                where_clause += f" AND STS.[YEAR] = {year}"
            if month:
                where_clause += f" AND STS.[MONTH] = {month}"

            # 构建查询条件
            base_query = text(f"""
                DECLARE @yyyy INT = {year};
                DECLARE @mm INT = {month};

                WITH
                    SalesTotalSummary AS
                        (
                        SELECT NT.[YEAR],[MONTH],ADMIN_UNIT_NAME,EMPLOYEE_NAME,SUM(PRICE_QTY) AS PRICE_QTY,SUM(AMOUNT) AS AMOUNT
                        FROM
                            (
                            ( 
                                SELECT 
                                YEAR(SI.TRANSACTION_DATE) AS [YEAR],
                                MONTH(SI.TRANSACTION_DATE) AS [MONTH],
                                CAST(((DATEDIFF(DAY, DATEFROMPARTS(YEAR(SI.TRANSACTION_DATE),MONTH(SI.TRANSACTION_DATE),1), SI.TRANSACTION_DATE) + 0.9 )/7 + 1) AS INT) AS WeekOfMonth,
                                AU.ADMIN_UNIT_NAME,
                                E.EMPLOYEE_NAME,
                                ITEM.ITEM_CODE,
                                ITEM.ITEM_NAME,
                                ITEM.SHORTCUT,
                                SID.PRICE_QTY,
                                SID.AMOUNT
                                FROM SALES_DELIVERY SD
                                LEFT JOIN SALES_DELIVERY_D SDD
                                ON SD.SALES_DELIVERY_ID = SDD.SALES_DELIVERY_ID
                                LEFT JOIN SALES_ISSUE_D SID
                                ON SID.SOURCE_ID_ROid = SDD. SALES_DELIVERY_D_ID
                                LEFT JOIN SALES_ISSUE SI
                                ON SI.SALES_ISSUE_ID = SID.SALES_ISSUE_ID
                                LEFT JOIN EMPLOYEE E
                                ON SD.Owner_Emp = E.EMPLOYEE_ID
                                LEFT JOIN EMPLOYEE_D ED
                                ON ED.EMPLOYEE_ID = E.EMPLOYEE_ID
                                LEFT JOIN ADMIN_UNIT AU
                                ON AU.ADMIN_UNIT_ID = ED.ADMIN_UNIT_ID
                                LEFT JOIN ITEM
                                ON SDD.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                                WHERE SD.CATEGORY = '24' AND YEAR(SI.TRANSACTION_DATE) = @yyyy AND MONTH(SI.TRANSACTION_DATE) = @mm
                            )
                            UNION ALL
                            (
                                SELECT 
                                YEAR(SR.TRANSACTION_DATE) AS [YEAR],
                                MONTH(SR.TRANSACTION_DATE) AS [MONTH],
                                CAST(((DATEDIFF(DAY, DATEFROMPARTS(YEAR(SR.TRANSACTION_DATE),MONTH(SR.TRANSACTION_DATE),1), SR.TRANSACTION_DATE) + 0.9 )/7 + 1) AS INT) AS WeekOfMonth,
                                AU.ADMIN_UNIT_NAME,
                                E.EMPLOYEE_NAME,
                                ITEM.ITEM_CODE,
                                ITEM.ITEM_NAME,
                                ITEM.SHORTCUT,
                                SRD.PRICE_QTY * -1 AS PRICE_QTY,
                                SRD.AMOUNT * -1 AS AMOUNT
                                FROM SALES_RETURN SR
                                LEFT JOIN SALES_RETURN_D SRD
                                ON SR.SALES_RETURN_ID = SRD.SALES_RETURN_ID
                                LEFT JOIN EMPLOYEE E
                                ON SR.Owner_Emp = E.EMPLOYEE_ID
                                LEFT JOIN EMPLOYEE_D ED
                                ON ED.EMPLOYEE_ID = E.EMPLOYEE_ID
                                LEFT JOIN ADMIN_UNIT AU
                                ON AU.ADMIN_UNIT_ID = ED.ADMIN_UNIT_ID
                                LEFT JOIN ITEM
                                ON SRD.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                                WHERE SR.CATEGORY = '26' 
                            )
                            ) AS NT
                            WHERE NT.YEAR > 0 AND NT.[YEAR] = @yyyy AND NT.[MONTH] = @mm
                            GROUP BY NT.[YEAR],NT.[MONTH],NT.ADMIN_UNIT_NAME,NT.EMPLOYEE_NAME
                        ),
                    SalesForecastSummary AS 
                        (
                            SELECT 
                            YEAR(SFDD.TIME_BUCKET_SECTION) AS [YEAR],
                            MONTH(SFDD.TIME_BUCKET_SECTION) AS [MONTH],
                            E.EMPLOYEE_NAME,
                            SUM(SFDD.FORECAST_QTY) AS FORECAST_QTY
                            FROM SALES_FORECAST_DOC SFD
                            LEFT JOIN SALES_FORECAST_DOC_D SFDD
                            ON SFDD.SALES_FORECAST_DOC_ID = SFD.SALES_FORECAST_DOC_ID
                            LEFT JOIN EMPLOYEE E
                            ON E.EMPLOYEE_ID = SFD.Owner_Emp
                            LEFT JOIN ITEM 
                            ON ITEM.ITEM_BUSINESS_ID = SFDD.ITEM_ID
                            WHERE SFDD.COLUMN_NO = 'COLUMN001' AND YEAR(SFDD.TIME_BUCKET_SECTION) = @yyyy AND MONTH(SFDD.TIME_BUCKET_SECTION) = @mm
                            GROUP BY YEAR(SFDD.TIME_BUCKET_SECTION),MONTH(SFDD.TIME_BUCKET_SECTION), E.EMPLOYEE_NAME
                        )
                    
                    SELECT 
                    SFS.[YEAR],
                    SFS.[MONTH],
                    STS.ADMIN_UNIT_NAME,
                    STS.[EMPLOYEE_NAME],
                    CAST(SFS.FORECAST_QTY AS INT) AS FORECAST_QTY,
                    STS.PRICE_QTY,
                    CAST(STS.PRICE_QTY/SFS.FORECAST_QTY*100 AS DECIMAL(10,2)) AS PERCENTAGE
                    FROM SalesForecastSummary SFS
                    LEFT JOIN SalesTotalSummary STS
                    ON SFS.[YEAR]=STS.[YEAR] AND SFS.[MONTH]=STS.[MONTH] AND SFS.EMPLOYEE_NAME=STS.EMPLOYEE_NAME
                    ORDER BY SFS.[YEAR],SFS.[MONTH],STS.ADMIN_UNIT_NAME DESC,STS.[EMPLOYEE_NAME];
                """)

            # 执行查询
            sale_targets = db.exec(base_query).all()
            
            # 将查询结果转换为响应格式
            result_list = []
            for target in sale_targets:
                result_list.append(SaleTargetSummary(
                    YEAR=target.YEAR,
                    MONTH=target.MONTH,
                    ADMIN_UNIT_NAME=target.ADMIN_UNIT_NAME,
                    EMPLOYEE_NAME=target.EMPLOYEE_NAME,
                    FORECAST_QTY=target.FORECAST_QTY,
                    PRICE_QTY=target.PRICE_QTY,
                    PERCENTAGE=target.PERCENTAGE
                ))
            
            return SaleTargetSummaryResponse(list=result_list)
        except Exception as e:
            logger.error(f"获取销售目标汇总失败: {str(e)}")
            raise CustomException(f"获取销售目标汇总失败: {str(e)}")

    async def get_sale_target_detail(self, db: Session, params: SaleTargetDetailQuery) -> List[SaleTargetDetailResponse]:
        """获取销售目标详情"""
        try:
            # 清理输入参数
            year = self._clean_input(params.year)
            month = self._clean_input(params.month)
            employee_name = self._clean_input(params.employee_name)

            # 构建查询条件
            where_clause = ""
            if year:
                where_clause += f" AND SS.[YEAR] = {year}"
            if month:
                where_clause += f" AND SS.[MONTH] = {month}"
            if employee_name:
                where_clause += f" AND SS.[EMPLOYEE_NAME] = '{employee_name}'"

            # 构建查询条件
            base_query = text(f"""
                DECLARE @YYYY INT = {year};
                DECLARE @MM INT = {month};
                DECLARE @EN NVARCHAR(255) = '{employee_name}';

                    WITH
                        SalesSummary AS
                        (
                        SELECT NT.[YEAR],[MONTH],ADMIN_UNIT_NAME,EMPLOYEE_NAME,ITEM_NAME,SHORTCUT,SUM(PRICE_QTY) AS PRICE_QTY,SUM(AMOUNT) AS AMOUNT
                        FROM
                            (
                            ( 
                                SELECT 
                                YEAR(SI.TRANSACTION_DATE) AS [YEAR],
                                MONTH(SI.TRANSACTION_DATE) AS [MONTH],
                                AU.ADMIN_UNIT_NAME,
                                E.EMPLOYEE_NAME,
                                ITEM.ITEM_CODE,
                                dbo.RemoveSpecificStrings(ITEM.ITEM_CODE, 'CP-,DG-,-Blank+TR,- Blank+TR,-Blank+TS,-FT+TR,-PGM+TR,-WG+TR,-PGM+TS,-PGM,- PGM,-FT,-TR,+TS+TR,-Blank,-WG,-AB,+TR') AS ITEM_NAME,
                                ITEM.SHORTCUT,
                                SID.PRICE_QTY,
                                SID.AMOUNT
                                FROM SALES_DELIVERY SD
                                LEFT JOIN SALES_DELIVERY_D SDD
                                ON SD.SALES_DELIVERY_ID = SDD.SALES_DELIVERY_ID
                                LEFT JOIN SALES_ISSUE_D SID
                                ON SID.SOURCE_ID_ROid = SDD. SALES_DELIVERY_D_ID
                                LEFT JOIN SALES_ISSUE SI
                                ON SI.SALES_ISSUE_ID = SID.SALES_ISSUE_ID
                                LEFT JOIN EMPLOYEE E
                                ON SD.Owner_Emp = E.EMPLOYEE_ID
                                LEFT JOIN EMPLOYEE_D ED
                                ON ED.EMPLOYEE_ID = E.EMPLOYEE_ID
                                LEFT JOIN ADMIN_UNIT AU
                                ON AU.ADMIN_UNIT_ID = ED.ADMIN_UNIT_ID
                                LEFT JOIN ITEM
                                ON SDD.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                                WHERE SD.CATEGORY = '24' AND YEAR(SI.TRANSACTION_DATE) = @YYYY AND MONTH(SI.TRANSACTION_DATE) = @MM AND E.EMPLOYEE_NAME = @EN
                            )
                            UNION ALL
                            (
                                SELECT 
                                YEAR(SR.TRANSACTION_DATE) AS [YEAR],
                                MONTH(SR.TRANSACTION_DATE) AS [MONTH],
                                AU.ADMIN_UNIT_NAME,
                                E.EMPLOYEE_NAME,
                                ITEM.ITEM_CODE,
                                dbo.RemoveSpecificStrings(ITEM.ITEM_CODE, 'CP-,DG-,-Blank+TR,- Blank+TR,-Blank+TS,-FT+TR,-PGM+TR,-WG+TR,-PGM+TS,-PGM,- PGM,-FT,-TR,+TS+TR,-Blank,-WG,-AB,+TR') AS ITEM_NAME,
                                ITEM.SHORTCUT,
                                SRD.PRICE_QTY * -1 AS PRICE_QTY,
                                SRD.AMOUNT * -1 AS AMOUNT
                                FROM SALES_RETURN SR
                                LEFT JOIN SALES_RETURN_D SRD
                                ON SR.SALES_RETURN_ID = SRD.SALES_RETURN_ID
                                LEFT JOIN EMPLOYEE E
                                ON SR.Owner_Emp = E.EMPLOYEE_ID
                                LEFT JOIN EMPLOYEE_D ED
                                ON ED.EMPLOYEE_ID = E.EMPLOYEE_ID
                                LEFT JOIN ADMIN_UNIT AU
                                ON AU.ADMIN_UNIT_ID = ED.ADMIN_UNIT_ID
                                LEFT JOIN ITEM
                                ON SRD.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                                WHERE SR.CATEGORY = '26' AND YEAR(SR.TRANSACTION_DATE) = @YYYY AND MONTH(SR.TRANSACTION_DATE) = @MM AND E.EMPLOYEE_NAME = @EN
                            )
                            ) AS NT
                            WHERE NT.YEAR > 0
                            GROUP BY NT.[YEAR],[MONTH],ADMIN_UNIT_NAME,EMPLOYEE_NAME,ITEM_NAME,SHORTCUT
                        ),
                    SalesForecast AS 
                        (
                            SELECT 
                            SFD.DOC_NO,
                            SFD.DOC_DATE,
                            SFD.CATEGORY,
                            SFD.BEGIN_DATE,
                            SFD.END_DATE,
                            SFD.FORECAST_VERSION,
                            SFD.BUCKET_SECTION_STRING,
                            SFD.FORECAST_DATE,
                            E.EMPLOYEE_NAME,
                            AU.ADMIN_UNIT_NAME,
                            ITEM.ITEM_CODE,
                            ITEM.SHORTCUT,
                            dbo.RemoveSpecificStrings(ITEM.ITEM_CODE, 'CP-,DG-,-Blank+TR,- Blank+TR,-Blank+TS,-FT+TR,-PGM+TR,-WG+TR,-PGM+TS,-PGM,- PGM,-FT,-TR,+TS+TR,-Blank,-WG,-AB,+TR') AS ITEM_NAME,
                            SFDD.COLUMN_NO,
                            SFDD.TIME_BUCKET_SECTION,
                            SFDD.SECTION_END_DATE,
                            SFDD.FORECAST_QTY
                            FROM SALES_FORECAST_DOC SFD
                            LEFT JOIN SALES_FORECAST_DOC_D SFDD
                            ON SFDD.SALES_FORECAST_DOC_ID = SFD.SALES_FORECAST_DOC_ID
                            LEFT JOIN EMPLOYEE E
                            ON E.EMPLOYEE_ID = SFD.Owner_Emp
                            LEFT JOIN EMPLOYEE_D ED
                            ON ED.EMPLOYEE_ID = E.EMPLOYEE_ID
                            LEFT JOIN ADMIN_UNIT AU
                            ON AU.ADMIN_UNIT_ID = ED.ADMIN_UNIT_ID
                            LEFT JOIN ITEM 
                            ON ITEM.ITEM_BUSINESS_ID = SFDD.ITEM_ID
                            WHERE SFDD.FORECAST_QTY > 0 AND SFDD.COLUMN_NO = 'COLUMN001' AND YEAR(SFDD.TIME_BUCKET_SECTION) = @YYYY AND MONTH(SFDD.TIME_BUCKET_SECTION) = @MM AND E.EMPLOYEE_NAME = @EN
                        )
                        

                    SELECT 
                        YEAR(SF.TIME_BUCKET_SECTION) AS [YEAR],
                        MONTH(SF.TIME_BUCKET_SECTION) AS [MONTH],
                        SF.ADMIN_UNIT_NAME,
                        SF.EMPLOYEE_NAME,
                        SF.SHORTCUT,
                        SF.ITEM_NAME,
                        CAST(SF.FORECAST_QTY AS INT) AS FORECAST_QTY,
                        CAST(SS.PRICE_QTY AS INT) AS PRICE_QTY,
                        CAST(SS.PRICE_QTY/SF.FORECAST_QTY*100 AS DECIMAL(18,2)) AS PERCENTAGE
                    FROM SalesForecast SF
                    LEFT JOIN SalesSummary SS
                    ON SF.EMPLOYEE_NAME = SS.EMPLOYEE_NAME AND SF.ITEM_NAME = SS.ITEM_NAME AND YEAR(SF.TIME_BUCKET_SECTION) = SS.[YEAR] AND MONTH(SF.TIME_BUCKET_SECTION) = SS.[MONTH]
                    ORDER BY YEAR(SF.TIME_BUCKET_SECTION),MONTH(SF.TIME_BUCKET_SECTION),SF.EMPLOYEE_NAME;
                """)

            # 执行查询
            sale_targets = db.exec(base_query).all()
            
            # 将查询结果转换为响应格式
            result_list = []
            for target in sale_targets:
                result_list.append(SaleTargetDetail(
                    YEAR=target.YEAR,
                    MONTH=target.MONTH,
                    ADMIN_UNIT_NAME=target.ADMIN_UNIT_NAME,
                    EMPLOYEE_NAME=target.EMPLOYEE_NAME,
                    SHORTCUT=target.SHORTCUT,
                    ITEM_NAME=target.ITEM_NAME,
                    FORECAST_QTY=target.FORECAST_QTY,
                    PRICE_QTY=target.PRICE_QTY,
                    PERCENTAGE=target.PERCENTAGE
                ))
            
            return SaleTargetDetailResponse(list=result_list)
        except Exception as e:
            logger.error(f"获取销售目标详情失败: {str(e)}")
            raise CustomException(f"获取销售目标详情失败: {str(e)}")


    
