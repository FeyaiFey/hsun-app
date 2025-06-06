from typing import Dict, Any, Optional, List
from sqlmodel import Session


from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.error_codes import ErrorCode, get_error_message
from app.schemas.sale import (
    SaleTableQuery, SaleTableResponse, SaleTargetCreate, SaleTargetUpdate,
    SaleTargetSummaryQuery, SaleTargetSummaryResponse,
    SaleTargetDetailQuery, SaleTargetDetailResponse,
    SaleAmountAnalyzeQuery, SaleAmountAnalyzeResponse,
    SaleAnalysisPannelResponse, SaleForecastResponse,
    SaleAmountQuery, SaleAmountResponse,
    SaleAmountBarChartQuery, SaleAmountBarChartEChartsResponse
)
from app.crud.sale import CRUSale


class SaleService:
    def __init__(self,db: Optional[Session] = None):
        self._db = db
        self.crud_sale = CRUSale()

    async def get_sale_table(self,db: Session,params: SaleTableQuery) -> List[SaleTableResponse]:
        return await self.crud_sale.get_sale_table(db,params)

    async def create_sale_target(self,db: Session,user_name: str,params: SaleTargetCreate) -> SaleTableResponse:
        return await self.crud_sale.create_sale_target(db,user_name,params)
    
    async def update_sale_target(self,db: Session,params: SaleTargetUpdate) -> SaleTableResponse:
        return await self.crud_sale.update_sale_target(db,params)
    
    async def delete_sale_target(self,db: Session,id: str) -> SaleTableResponse:
        return await self.crud_sale.delete_sale_target(db,id)

    async def get_sale_target_summary(self,db: Session,params: SaleTargetSummaryQuery) -> SaleTargetSummaryResponse:
        return await self.crud_sale.get_sale_target_summary(db,params)

    async def export_sale_target_summary(self,db: Session,params: SaleTargetSummaryQuery) -> bytes:
        return await self.crud_sale.export_sale_target_summary(db,params)

    async def get_sale_target_detail(self,db: Session,params: SaleTargetDetailQuery) -> SaleTargetDetailResponse:
        return await self.crud_sale.get_sale_target_detail(db,params)

    async def get_sale_amount_analyze(self,db: Session,params: SaleAmountAnalyzeQuery) -> SaleAmountAnalyzeResponse:
        return await self.crud_sale.get_sale_amount_analyze(db,params)

    async def get_sale_analysis_pannel(self,db: Session) -> SaleAnalysisPannelResponse:
        return await self.crud_sale.get_sale_analysis_pannel(db)

    async def get_sale_forecast(self,db: Session) -> SaleForecastResponse:
        return await self.crud_sale.get_sale_forecast(db)

    async def get_sale_analyze_amount(self,db: Session,params: SaleAmountQuery) -> SaleAmountResponse:
        return await self.crud_sale.get_sale_analyze_amount(db,params)

    async def get_sale_amount_bar_chart(self,db: Session,params: SaleAmountBarChartQuery) -> SaleAmountBarChartEChartsResponse:
        return await self.crud_sale.get_sale_amount_bar_chart(db,params)

    async def get_sale_percentage_bar_chart(self,db: Session,params: SaleAmountBarChartQuery) -> SaleAmountBarChartEChartsResponse:
        return await self.crud_sale.get_sale_percentage_bar_chart(db,params)
