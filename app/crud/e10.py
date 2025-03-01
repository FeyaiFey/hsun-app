from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.schemas.e10 import PurchaseOrder, PurchaseOrderQuery, PurchaseWip, PurchaseWipQuery, PurchaseWipSupplierResponse
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
                    CASE 
                        WHEN s.RECEIPT_CLOSE = 0 OR s.RECEIPT_CLOSE IS NULL THEN CAST(p.BUSINESS_QTY - ISNULL(s.RECEIPTED_BUSINESS_QTY, 0) AS INT)
                        ELSE 0
                    END AS WIP_QTY,
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
                
            if params.purchase_date_start:
                conditions.append("AND CAST(po.PURCHASE_DATE AS DATE) >= :purchase_date_start")
                query_params["purchase_date_start"] = params.purchase_date_start
            
            if params.purchase_date_end:
                conditions.append("AND CAST(po.PURCHASE_DATE AS DATE) <= :purchase_date_end")
                query_params["purchase_date_end"] = params.purchase_date_end
            # 添加收货结束状态查询条件
            if params.receipt_close is not None:
                if params.receipt_close == 0:
                    conditions.append("AND (s.RECEIPT_CLOSE = 0 OR s.RECEIPT_CLOSE IS NULL)")
                else:
                    conditions.append("AND s.RECEIPT_CLOSE > 0")

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)
            
            # 添加排序
            query += " ORDER BY po.PURCHASE_DATE, po.DOC_NO"

            # 添加分页
            if params.pageIndex and params.pageSize:
                offset = (params.pageIndex - 1) * params.pageSize
                query += " OFFSET :offset ROWS FETCH NEXT :pageSize ROWS ONLY"
                query_params["offset"] = offset
                query_params["pageSize"] = params.pageSize

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.exec(stmt).all()
            
            # 获取总记录数
            count_query = f"""
                SELECT COUNT(1)
                FROM PURCHASE_ORDER po
                LEFT JOIN PURCHASE_ORDER_D p ON po.PURCHASE_ORDER_ID = p.PURCHASE_ORDER_ID 
                LEFT JOIN ITEM i ON p.ITEM_ID = i.ITEM_BUSINESS_ID
                LEFT JOIN PURCHASE_ORDER_SD s ON s.PURCHASE_ORDER_D_ID = p.PURCHASE_ORDER_D_ID
                WHERE (p.PURCHASE_TYPE=1) AND (i.ITEM_CODE LIKE N'CL%WF')
                {' '.join(conditions)}
            """
            total = db.exec(text(count_query).bindparams(**{k:v for k,v in query_params.items() if k not in ['offset', 'pageSize']})).scalar()
            
            # 转换为模型实例
            purchase_orders = [
                PurchaseOrder(
                    SUPPLIER_FULL_NAME=row.SUPPLIER_FULL_NAME,
                    DOC_NO=row.DOC_NO,
                    PURCHASE_DATE=row.PURCHASE_DATE,
                    REMARK=row.REMARK,
                    ITEM_CODE=row.ITEM_CODE,
                    ITEM_NAME=row.ITEM_NAME,
                    SHORTCUT=row.SHORTCUT,
                    BUSINESS_QTY=row.BUSINESS_QTY,
                    SECOND_QTY=row.SECOND_QTY,
                    RECEIPTED_BUSINESS_QTY=row.RECEIPTED_BUSINESS_QTY,
                    WIP_QTY=row.WIP_QTY,
                    PRICE=round(row.PRICE, 4) if row.PRICE else None,
                    AMOUNT=round(row.AMOUNT, 4) if row.AMOUNT else None,
                    RECEIPT_CLOSE=row.RECEIPT_CLOSE
                ) for row in result
            ]
            
            return {
                "list": purchase_orders,
                "total": total or 0
            }
            
        except Exception as e:
            # 记录错误但不暴露详细信息
            logger.error(f"查询采购订单失败: {str(e)}")
            raise CustomException("查询采购订单失败")
        
    def get_purchase_wip_by_params(self,db:Session,params:PurchaseWipQuery)->List[PurchaseWip]:
        """根据参数获取采购在途"""
        try:
            # 构建基础查询
            base_query = """
                SELECT
                    purchaseOrder,
                    itemName,
                    lot,
                    qty,
                    status,
                    stage,
                    layerCount,
                    remainLayer,
                    currentPosition,
                    forecastDate,
                    supplier,
                    finished_at,
                    CASE 
                        WHEN forecastDate IS NULL THEN 0
                        ELSE DATEDIFF(DAY, modified_at, GETDATE())
                    END AS stranded,
                    CASE 
                        WHEN NOT finished_at IS NULL THEN DATEDIFF(DAY, create_at, GETDATE())
                        ELSE NULL
                    END AS leadTime
                FROM huaxinAdmin_wip_fab
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            # 参数验证和清理
            if params.purchase_order and isinstance(params.purchase_order, str):
                conditions.append("AND purchaseOrder LIKE :purchase_order")
                query_params["purchase_order"] = f"%{self._clean_input(params.purchase_order)}%"

            if params.item_name and isinstance(params.item_name, str):
                conditions.append("AND itemName LIKE :item_name")
                query_params["item_name"] = f"%{self._clean_input(params.item_name)}%"
            
            if params.supplier and isinstance(params.supplier, str):
                conditions.append("AND supplier LIKE :supplier")
                query_params["supplier"] = f"%{self._clean_input(params.supplier)}%"
            
            if params.status and isinstance(params.status, str):
                conditions.append("AND status LIKE :status")
                query_params["status"] = f"%{self._clean_input(params.status)}%"

            if params.is_finished is not None:
                if params.is_finished == 1:
                    conditions.append("AND finished_at IS NOT NULL")
                else:
                    conditions.append("AND finished_at IS NULL")

            if params.is_stranded is not None:
                if params.is_stranded == 1:
                    conditions.append("AND CASE WHEN forecastDate IS NULL THEN 0 ELSE DATEDIFF(DAY, modified_at, GETDATE()) END > 0")
                else:
                    conditions.append("AND CASE WHEN forecastDate IS NULL THEN 0 ELSE DATEDIFF(DAY, modified_at, GETDATE()) END <= 0")

            if params.days is not None:
                conditions.append("AND forecastDate <= DATEADD(DAY, :days, GETDATE())")
                query_params["days"] = params.days

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY purchaseOrder"

            # 添加分页
            if params.pageIndex and params.pageSize:
                offset = (params.pageIndex - 1) * params.pageSize
                query += " OFFSET :offset ROWS FETCH NEXT :pageSize ROWS ONLY"
                query_params["offset"] = offset
                query_params["pageSize"] = params.pageSize

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.exec(stmt).all()

            # 获取总记录数
            count_query = f"""
                SELECT COUNT(1)
                FROM huaxinAdmin_wip_fab
                WHERE 1=1
                {' '.join(conditions)}
            """
            total = db.exec(text(count_query).bindparams(**{k:v for k,v in query_params.items() if k not in ['offset', 'pageSize']})).scalar()

            # 转换为模型实例
            purchase_wips = [
                PurchaseWip(
                    purchaseOrder=row.purchaseOrder,
                    itemName=row.itemName,
                    lot=row.lot,
                    qty=row.qty,
                    status=row.status,
                    stage=row.stage,
                    layerCount=row.layerCount,
                    remainLayerCount=row.remainLayer,
                    currentPosition=row.currentPosition,
                    forecastDate=row.forecastDate,
                    supplier=row.supplier,
                    finished_at=row.finished_at,
                    stranded=row.stranded,
                    leadTime=row.leadTime
                ) for row in result
            ]

            return {
                "list": purchase_wips,
                "total": total or 0
            }
            
        except Exception as e:
            logger.error(f"查询采购在途失败: {str(e)}")
            raise CustomException("查询采购在途失败")
        
    def get_purchase_wip_supplier(self,db:Session)->List[str]:
        """获取采购在制供应商"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT supplier
                FROM huaxinAdmin_wip_fab
                WHERE supplier IS NOT NULL
                ORDER BY supplier
                """
            result = db.exec(text(base_query)).all()
            # 提取供应商名称列表
            return [row[0] for row in result if row[0]]  # 确保返回非空的供应商名称列表
        except Exception as e:
            logger.error(f"获取采购在制供应商失败: {str(e)}")
            raise CustomException("获取采购在制供应商失败")
