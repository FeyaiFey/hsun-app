from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.schemas.e10 import PurchaseOrder, PurchaseOrderQuery
from app.core.exceptions import CustomException
from app.core.logger import logger


class CRUDE10:
    """E10 CRUD操作类"""

    def _clean_input(self, value: str) -> str:
        """清理输入参数，移除潜在的危险字符
        
        Args:
            value: 输入字符串
            
        Returns:
            清理后的字符串
        """
        # 移除常见的 SQL 注入字符
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_']
        cleaned = value
        for char in dangerous_chars:
            cleaned = cleaned.replace(char, '')
        return cleaned

    def get_purchase_order_by_params(self, db: Session, params: PurchaseOrderQuery) -> List[PurchaseOrder]:
        """根据参数获取采购订单"""
        try:
            # 构建基础查询
            base_query = """
                SELECT
                    po.SUPPLIER_FULL_NAME,
                    po.DOC_NO,
                    CAST(po.PURCHASE_DATE AS DATE) AS PURCHASE_DATE,
                    p.REMARK,
                    i.ITEM_CODE,
                    i.ITEM_NAME,
                    i.SHORTCUT,
                    CAST(p.BUSINESS_QTY AS INT) AS 'BUSINESS_QTY',
                    CAST(p.SECOND_QTY AS INT) AS 'SECOND_QTY',
                    CAST(s.RECEIPTED_BUSINESS_QTY AS INT) AS 'RECEIPTED_BUSINESS_QTY',
                    CAST(p.PRICE AS FLOAT(4)) AS PRICE,
                    CAST(p.AMOUNT AS FLOAT(4)) AS AMOUNT,
                    s.RECEIPT_CLOSE
                FROM PURCHASE_ORDER po
                LEFT JOIN PURCHASE_ORDER_D p
                ON po.PURCHASE_ORDER_ID = p.PURCHASE_ORDER_ID 
                LEFT JOIN ITEM i
                ON p.ITEM_ID = i.ITEM_BUSINESS_ID
                LEFT JOIN PURCHASE_ORDER_SD s
                ON s.PURCHASE_ORDER_D_ID = p.PURCHASE_ORDER_D_ID
                WHERE (p.PURCHASE_TYPE=1) AND (i.ITEM_CODE LIKE N'CL%WF')
            """
            
            # 构建查询条件
            conditions = []
            query_params = {}
            
            # 参数验证和清理
            if params.doc_no and isinstance(params.doc_no, str):
                conditions.append("AND po.DOC_NO LIKE :doc_no")
                query_params["doc_no"] = f"%{self._clean_input(params.doc_no)}%"
                
            if params.item_code and isinstance(params.item_code, str):
                conditions.append("AND i.ITEM_CODE LIKE :item_code")
                query_params["item_code"] = f"%{self._clean_input(params.item_code)}%"
                
            if params.item_name and isinstance(params.item_name, str):
                conditions.append("AND i.ITEM_NAME LIKE :item_name")
                query_params["item_name"] = f"%{self._clean_input(params.item_name)}%"
                
            if params.supplier and isinstance(params.supplier, str):
                conditions.append("AND po.SUPPLIER_FULL_NAME LIKE :supplier")
                query_params["supplier"] = f"%{self._clean_input(params.supplier)}%"
                
            if params.purchase_date:
                conditions.append("AND CAST(po.PURCHASE_DATE AS DATE) = :purchase_date")
                query_params["purchase_date"] = params.purchase_date

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)
            
            # 添加排序
            query += " ORDER BY po.PURCHASE_DATE, po.DOC_NO"

            # 执行查询
            result = db.exec(text(query), query_params).all()
            
            # 转换为模型实例
            return [PurchaseOrder(**row) for row in result]
            
        except Exception as e:
            # 记录错误但不暴露详细信息
            logger.error(f"查询采购订单失败: {str(e)}")
            raise CustomException("查询采购订单失败")
