from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.models.wip import FabWip, AssyWip
from app.schemas.wip import FabWipQuery

class CRUDFabWip:
    """晶圆厂WIP CRUD操作类"""

    def __init__(self, model: FabWip):
        self.model = model

    def get_fab_wip(
        self,
        db: Session,
        *,
        query_params: Optional[FabWipQuery] = None
    ) -> List[FabWip]:
        """获取晶圆厂WIP列表
        
        Args:
            db: 数据库会话
            query_params: 查询参数
            
        Returns:
            List[FabWip]: WIP列表
        """
        # 构建基础查询
        statement = select(self.model)
        
        # 如果有查询参数，添加条件
        if query_params:
            if query_params.purchaseOrder:
                statement = statement.where(
                    self.model.purchaseOrder.like(f"%{query_params.purchaseOrder}%")
                )
            if query_params.lot:
                statement = statement.where(
                    self.model.lot.like(f"%{query_params.lot}%")
                )
            if query_params.itemName:
                statement = statement.where(
                    self.model.itemName.like(f"%{query_params.itemName}%")
                )
            if query_params.forecastDate:
                statement = statement.where(
                    self.model.forecastDate == query_params.forecastDate
                )
            if query_params.supplier:
                statement = statement.where(
                    self.model.supplier.like(f"%{query_params.supplier}%")
                )
        
        # 按批号排序
        statement = statement.order_by(self.model.lot)
        
        return db.exec(statement).all()

class CRUDAssyWip:
    """封装厂WIP CRUD操作类"""

    def __init__(self, model: AssyWip):
        self.model = model

    def get_assy_wip(self, db: Session) -> List[AssyWip]:
        """获取封装厂WIP"""
        query = select(self.model)
        return db.exec(query).all()
    
    def get_assy_wip_by_order(self, db: Session, order: str) -> Optional[AssyWip]:
        """通过订单号获取封装厂WIP"""
        query = select(self.model).where(self.model.订单号 == order)
        return db.exec(query).first()

