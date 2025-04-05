from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.schemas.purchase import (PurchaseOrder,PurchaseOrderQuery,PurchaseWip,PurchaseWipQuery)
from app.schemas.assy import (AssyOrder,AssyOrderQuery,AssyWip,AssyWipQuery,AssyOrderItemsQuery,AssyOrderPackageTypeQuery,AssyOrderSupplierQuery,AssyBomQuery,AssyBom)
from app.schemas.stock import (StockQuery,
                             Stock,
                             WaferIdQtyDetailQuery,
                             WaferIdQtyDetail,
                             StockSummaryQuery,
                             StockSummary)
from app.schemas.e10 import (FeatureGroupNameQuery,
                             ItemCodeQuery,
                             ItemNameQuery,
                             WarehouseNameQuery,
                             TestingProgramQuery,
                             BurningProgramQuery,
                             LotCodeQuery)
from app.schemas.report import GlobalReport
from app.core.exceptions import CustomException
from app.core.logger import logger
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io


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

    def get_feature_group_name(self,db:Session,params:FeatureGroupNameQuery)->Dict[str,Any]:
        """获取品号群组"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT FEATURE_GROUP_NAME
                FROM FEATURE_GROUP
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.feature_group_name:
                feature_group_name = params.feature_group_name.upper()
                conditions.append("AND FEATURE_GROUP_NAME LIKE :feature_group_name")
                query_params["feature_group_name"] = f"%{self._clean_input(feature_group_name)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY FEATURE_GROUP_NAME"

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()

            # 转换为模型实例
            feature_group_names = [
                {
                    "label": row.FEATURE_GROUP_NAME,
                    "value": row.FEATURE_GROUP_NAME
                } for row in result
            ]
            return {
                "list": feature_group_names
            }
        except Exception as e:
            logger.error(f"获取品号群组失败: {str(e)}")
            raise CustomException("获取品号群组失败")
        
    def get_item_code(self,db:Session,params:ItemCodeQuery)->Dict[str,Any]:
        """获取品号"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT ITEM_CODE
                FROM ITEM
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.item_code:
                item_code = params.item_code.upper()
                conditions.append("AND ITEM_CODE LIKE :item_code")
                query_params["item_code"] = f"%{self._clean_input(item_code)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序  
            query += " ORDER BY ITEM_CODE"

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()
            
            # 转换为模型实例
            item_codes = [
                {
                    "label": row.ITEM_CODE,
                    "value": row.ITEM_CODE
                } for row in result
            ]
            return {
                "list": item_codes
            }
        except Exception as e:
            logger.error(f"获取品号失败: {str(e)}")
            raise CustomException("获取品号失败")
        
    def get_item_name(self,db:Session,params:ItemNameQuery)->Dict[str,Any]:
        """获取品名"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT ITEM_NAME
                FROM ITEM
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.item_name:
                item_name = params.item_name.upper()
                conditions.append("AND ITEM_NAME LIKE :item_name")
                query_params["item_name"] = f"%{self._clean_input(item_name)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY ITEM_NAME"            

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()
            
            # 转换为模型实例
            item_names = [
                {
                    "label": row.ITEM_NAME,
                    "value": row.ITEM_NAME
                } for row in result
            ]
            return {
                "list": item_names
            }
        except Exception as e:
            logger.error(f"获取品名失败: {str(e)}")
            raise CustomException("获取品名失败")
    
    def get_lot_code(self,db:Session,params:LotCodeQuery)->Dict[str,Any]:
        """获取批号"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT LOT_CODE
                FROM ITEM_LOT
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.lot_code:
                lot_code = params.lot_code.upper()
                conditions.append("AND LOT_CODE LIKE :lot_code")
                query_params["lot_code"] = f"%{self._clean_input(lot_code)}%"
            
            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY LOT_CODE"

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()

            # 转换为模型实例
            lot_codes = [
                {
                    "label": row.LOT_CODE,
                    "value": row.LOT_CODE
                } for row in result
            ]
            return {
                "list": lot_codes
            }
        except Exception as e:
            logger.error(f"获取批号失败: {str(e)}")
            raise CustomException("获取批号失败")
    
    def get_warehouse_name(self,db:Session,params:WarehouseNameQuery)->Dict[str,Any]:
        """获取仓库"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT WAREHOUSE_NAME
                FROM WAREHOUSE
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.warehouse_name:
                warehouse_name = params.warehouse_name.upper()
                conditions.append("AND WAREHOUSE_NAME LIKE :warehouse_name")
                query_params["warehouse_name"] = f"%{self._clean_input(warehouse_name)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY WAREHOUSE_NAME" 

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()
            
            # 转换为模型实例
            warehouse_names = [
                {
                    "label": row.WAREHOUSE_NAME,
                    "value": row.WAREHOUSE_NAME
                } for row in result
            ]
            return {
                "list": warehouse_names
            }
        except Exception as e:
            logger.error(f"获取仓库失败: {str(e)}")
            raise CustomException("获取仓库失败")
        
    def get_testing_program(self,db:Session,params:TestingProgramQuery)->Dict[str,Any]:
        """获取测试程序"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT Z_TESTING_PROGRAM_NAME
                FROM Z_TESTING_PROGRAM
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.testing_program:
                testing_program = params.testing_program.upper()
                conditions.append("AND Z_TESTING_PROGRAM_NAME LIKE :testing_program")
                query_params["testing_program"] = f"%{self._clean_input(testing_program)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY Z_TESTING_PROGRAM_NAME"

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()

            # 转换为模型实例
            testing_programs = [
                {
                    "label": row.Z_TESTING_PROGRAM_NAME,
                    "value": row.Z_TESTING_PROGRAM_NAME
                } for row in result
            ]
            return {
                "list": testing_programs
            }
        except Exception as e:
            logger.error(f"获取测试程序失败: {str(e)}")
            raise CustomException("获取测试程序失败")
        
    def get_burning_program(self,db:Session,params:BurningProgramQuery)->Dict[str,Any]:
        """获取烧录程序"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT Z_BURNING_PROGRAM_NAME
                FROM Z_BURNING_PROGRAM
                WHERE 1=1
            """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.burning_program:
                burning_program = params.burning_program.upper()
                conditions.append("AND Z_BURNING_PROGRAM_NAME LIKE :burning_program")
                query_params["burning_program"] = f"%{self._clean_input(burning_program)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY Z_BURNING_PROGRAM_NAME"

            # 执行查询
            result = db.exec(text(query).bindparams(**query_params)).all()

            # 转换为模型实例
            burning_programs = [
                {
                    "label": row.Z_BURNING_PROGRAM_NAME,
                    "value": row.Z_BURNING_PROGRAM_NAME
                } for row in result
            ]
            return {
                "list": burning_programs
            }
        except Exception as e:
            logger.error(f"获取烧录程序失败: {str(e)}")
            raise CustomException("获取烧录程序失败")
        
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
    
    def get_purchase_supplier(self,db:Session)->List[str]:
        """获取采购供应商"""
        try:
            # 构建基础查询
            base_query = """
                SELECT DISTINCT po.SUPPLIER_FULL_NAME
                FROM PURCHASE_ORDER po
                LEFT JOIN PURCHASE_ORDER_D p
                ON po.PURCHASE_ORDER_ID = p.PURCHASE_ORDER_ID 
                LEFT JOIN ITEM i
                ON p.ITEM_ID = i.ITEM_BUSINESS_ID
                LEFT JOIN PURCHASE_ORDER_SD s
                ON s.PURCHASE_ORDER_D_ID = p.PURCHASE_ORDER_D_ID
                WHERE (p.PURCHASE_TYPE=1) AND (i.ITEM_CODE LIKE N'CL%WF')
            """
            result = db.exec(text(base_query)).all()
            # 提取供应商名称列表
            return [row[0] for row in result if row[0]]  # 确保返回非空的供应商名称列表
        except Exception as e:
            logger.error(f"获取采购供应商失败: {str(e)}")
            raise CustomException("获取采购供应商失败")
        
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

    def get_assy_order_by_params(self,db:Session,params:AssyOrderQuery)->Dict[str,Any]:
        """获取封装订单列表"""
        try:
            # 构建基础查询
            base_query = """
                SELECT *
                FROM (
                    SELECT
                        hpl.ID,
                        hpl.DOC_NO,
                        hpl.ITEM_CODE,
                        hpl.Z_PACKAGE_TYPE_NAME,
                        hpl.LOT_CODE,
                        hpl.BUSINESS_QTY,
                        hpl.RECEIPTED_PRICE_QTY,
                        0 AS WIP_QTY,
                        hpl.Z_PROCESSING_PURPOSE_NAME,
                        hpl.Z_TESTING_PROGRAM_NAME,
                        hpl.Z_ASSEMBLY_CODE,
                        hpl.Z_WIRE_NAME,
                        hpl.REMARK,
                        hpl.PURCHASE_DATE,
                        ISNULL(hpl.FIRST_ARRIVAL_DATE, DATEADD(MONTH, 2, hpl.PURCHASE_DATE)) AS FIRST_ARRIVAL_DATE,
                        hpl.SUPPLIER_FULL_NAME,
                        hpl.RECEIPT_CLOSE
                    FROM HSUN_PACKAGE_LIST hpl
                    UNION ALL
                    SELECT
                        ROW_NUMBER() OVER (ORDER BY PO.PURCHASE_DATE, PO.DOC_NO) + 115617 AS ID,
                        PO.DOC_NO,
                        ITEM.ITEM_CODE,
                        Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_NAME,
                        ITEM_LOT.LOT_CODE,
                        CAST(PO_D.BUSINESS_QTY AS INT) AS BUSINESS_QTY,
                        CAST(PO_D.RECEIPTED_PRICE_QTY AS INT) AS RECEIPTED_PRICE_QTY,
                        CASE 
                            WHEN PO.[CLOSE] = N'2' THEN 0
                            WHEN PO_D.BUSINESS_QTY <> 0 AND (PO_D.RECEIPTED_PRICE_QTY / PO_D.BUSINESS_QTY) > 0.992 THEN 0
                            ELSE CAST(((PO_D.BUSINESS_QTY * 0.996) - PO_D.RECEIPTED_PRICE_QTY) AS INT)
                        END AS WIP_QTY,
                        Z_PROCESSING_PURPOSE.Z_PROCESSING_PURPOSE_NAME,
                        ZTP.Z_TESTING_PROGRAM_NAME,
                        Z_ASSEMBLY_CODE.Z_ASSEMBLY_CODE,
                        Z_WIRE.Z_WIRE_NAME,
                        Z_PACKAGE.REMARK,
                        CAST(PO.PURCHASE_DATE AS DATE) AS PURCHASE_DATE,
                        CAST(PR.CreateDate AS DATE) AS FIRST_ARRIVAL_DATE,
                        PO.SUPPLIER_FULL_NAME,
                        PO_SD.RECEIPT_CLOSE
                    FROM PURCHASE_ORDER PO
                    LEFT JOIN PURCHASE_ORDER_D PO_D 
                        ON PO_D.PURCHASE_ORDER_ID = PO.PURCHASE_ORDER_ID
                    LEFT JOIN PURCHASE_ORDER_SD PO_SD 
                        ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                    LEFT JOIN PURCHASE_ORDER_SSD PO_SSD 
                        ON PO_SSD.PURCHASE_ORDER_SD_ID = PO_SD.PURCHASE_ORDER_SD_ID
                    LEFT JOIN Z_OUT_MO_D 
                        ON PO_SSD.REFERENCE_SOURCE_ID_ROid = Z_OUT_MO_D.Z_OUT_MO_D_ID
                    LEFT JOIN ITEM 
                        ON PO_D.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                    LEFT JOIN ITEM_LOT 
                        ON Z_OUT_MO_D.ITEM_LOT_ID = ITEM_LOT.ITEM_LOT_ID
                    LEFT JOIN Z_ASSEMBLY_CODE 
                        ON Z_OUT_MO_D.Z_PACKAGE_ASSEMBLY_CODE_ID = Z_ASSEMBLY_CODE.Z_ASSEMBLY_CODE_ID
                    LEFT JOIN Z_ASSEMBLY_CODE ZAC
                        ON Z_OUT_MO_D.Z_TESTING_ASSEMBLY_CODE_ID = ZAC.Z_ASSEMBLY_CODE_ID
                    LEFT JOIN Z_TESTING_PROGRAM ZTP
                        ON ZAC.PROGRAM_ROid = ZTP.Z_TESTING_PROGRAM_ID
                    LEFT JOIN Z_PACKAGE 
                        ON Z_ASSEMBLY_CODE.PROGRAM_ROid = Z_PACKAGE.Z_PACKAGE_ID
                    LEFT JOIN Z_PROCESSING_PURPOSE 
                        ON Z_ASSEMBLY_CODE.Z_PROCESSING_PURPOSE_ID = Z_PROCESSING_PURPOSE.Z_PROCESSING_PURPOSE_ID
                    LEFT JOIN Z_LOADING_METHOD 
                        ON Z_LOADING_METHOD.Z_LOADING_METHOD_ID = Z_PACKAGE.Z_LOADING_METHOD_ID
                    LEFT JOIN Z_WIRE 
                        ON Z_WIRE.Z_WIRE_ID = Z_PACKAGE.Z_WIRE_ID
                    LEFT JOIN Z_PACKAGE_TYPE 
                        ON Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_ID = Z_PACKAGE.Z_PACKAGE_TYPE_ID
                    LEFT JOIN FEATURE_GROUP 
                        ON FEATURE_GROUP.FEATURE_GROUP_ID = ITEM.FEATURE_GROUP_ID
                    OUTER APPLY (
                        SELECT TOP 1 *
                        FROM PURCHASE_RECEIPT_D PRD
                        WHERE PRD.ORDER_SOURCE_ID_ROid = PO_SD.PURCHASE_ORDER_SD_ID
                        ORDER BY PRD.CreateDate
                    ) PR
                    WHERE PO.PURCHASE_TYPE = 2 
                        AND PO.PURCHASE_DATE > '2024-10-21' 
                        AND ITEM.ITEM_CODE LIKE N'BC%AB' 
                        AND PO.SUPPLIER_FULL_NAME <> N'温州镁芯微电子有限公司'  
                        AND PO.SUPPLIER_FULL_NAME <> N'苏州荐恒电子科技有限公司'  
                        AND PO.SUPPLIER_FULL_NAME <> N'深圳市华新源科技有限公司'
                ) AS CombinedResults
                WHERE 1=1
            """

            # 构建查询条件
            conditions = []
            query_params = {}
            
            # 参数验证和清理
            if params.doc_no and isinstance(params.doc_no, str):
                conditions.append("AND UPPER(DOC_NO) LIKE UPPER(:doc_no)")
                query_params["doc_no"] = f"%{self._clean_input(params.doc_no)}%"
                
            if params.item_code and isinstance(params.item_code, str):
                conditions.append("AND UPPER(ITEM_CODE) LIKE UPPER(:item_code)")
                query_params["item_code"] = f"%{self._clean_input(params.item_code)}%"
            
            if params.lot_code and isinstance(params.lot_code, str):
                conditions.append("AND UPPER(LOT_CODE) LIKE UPPER(:lot_code)")
                query_params["lot_code"] = f"%{self._clean_input(params.lot_code)}%"
            
            if params.supplier and isinstance(params.supplier, str):
                conditions.append("AND SUPPLIER_FULL_NAME LIKE :supplier")
                query_params["supplier"] = f"%{self._clean_input(params.supplier)}%"
                
            if params.package_type and isinstance(params.package_type, str):
                conditions.append("AND UPPER(Z_PACKAGE_TYPE_NAME) LIKE UPPER(:package_type)")
                query_params["package_type"] = f"%{self._clean_input(params.package_type)}%"
                
            if params.assembly_code and isinstance(params.assembly_code, str):
                conditions.append("AND UPPER(Z_ASSEMBLY_CODE) LIKE UPPER(:assembly_code)")
                query_params["assembly_code"] = f"%{self._clean_input(params.assembly_code)}%"
                
            if params.is_closed is not None:
                if params.is_closed == 0:
                    conditions.append("AND RECEIPT_CLOSE = 0")
                else:
                    conditions.append("AND RECEIPT_CLOSE != 0")

            if params.order_date_start:
                conditions.append("AND PURCHASE_DATE >= :order_date_start")
                query_params["order_date_start"] = params.order_date_start

            if params.order_date_end:
                conditions.append("AND PURCHASE_DATE <= :order_date_end")
                query_params["order_date_end"] = params.order_date_end
                
            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)
            
            # 添加排序
            query += " ORDER BY PURCHASE_DATE, DOC_NO"
            
            # 添加分页
            if params.pageIndex and params.pageSize:
                offset = (params.pageIndex - 1) * params.pageSize
                query += " OFFSET :offset ROWS FETCH NEXT :pageSize ROWS ONLY"
                query_params["offset"] = offset
                query_params["pageSize"] = params.pageSize

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()
            
            # 获取总记录数
            count_query = f"""
                SELECT COUNT(1) 
                FROM (
                    SELECT
                        hpl.ID,
                        hpl.DOC_NO,
                        hpl.ITEM_CODE,
                        hpl.Z_PACKAGE_TYPE_NAME,
                        hpl.LOT_CODE,
                        hpl.BUSINESS_QTY,
                        hpl.RECEIPTED_PRICE_QTY,
                        0 AS WIP_QTY,
                        hpl.Z_PROCESSING_PURPOSE_NAME,
                        hpl.Z_TESTING_PROGRAM_NAME,
                        hpl.Z_ASSEMBLY_CODE,
                        hpl.Z_WIRE_NAME,
                        hpl.REMARK,
                        hpl.PURCHASE_DATE,
                        ISNULL(hpl.FIRST_ARRIVAL_DATE, DATEADD(MONTH, 2, hpl.PURCHASE_DATE)) AS FIRST_ARRIVAL_DATE,
                        hpl.SUPPLIER_FULL_NAME,
                        hpl.RECEIPT_CLOSE
                    FROM HSUN_PACKAGE_LIST hpl
                    UNION ALL
                    SELECT
                        ROW_NUMBER() OVER (ORDER BY PO.PURCHASE_DATE, PO.DOC_NO) + 115617 AS ID,
                        PO.DOC_NO,
                        ITEM.ITEM_CODE,
                        Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_NAME,
                        ITEM_LOT.LOT_CODE,
                        CAST(PO_D.BUSINESS_QTY AS INT) AS BUSINESS_QTY,
                        CAST(PO_D.RECEIPTED_PRICE_QTY AS INT) AS RECEIPTED_PRICE_QTY,
                        CASE 
                            WHEN PO.[CLOSE] = N'2' THEN 0
                            WHEN PO_D.BUSINESS_QTY <> 0 AND (PO_D.RECEIPTED_PRICE_QTY / PO_D.BUSINESS_QTY) > 0.992 THEN 0
                            ELSE CAST(((PO_D.BUSINESS_QTY * 0.996) - PO_D.RECEIPTED_PRICE_QTY) AS INT)
                        END AS WIP_QTY,
                        Z_PROCESSING_PURPOSE.Z_PROCESSING_PURPOSE_NAME,
                        ZTP.Z_TESTING_PROGRAM_NAME,
                        Z_ASSEMBLY_CODE.Z_ASSEMBLY_CODE,
                        Z_WIRE.Z_WIRE_NAME,
                        Z_PACKAGE.REMARK,
                        CAST(PO.PURCHASE_DATE AS DATE) AS PURCHASE_DATE,
                        CAST(PR.CreateDate AS DATE) AS FIRST_ARRIVAL_DATE,
                        PO.SUPPLIER_FULL_NAME,
                        PO_SD.RECEIPT_CLOSE
                    FROM PURCHASE_ORDER PO
                    LEFT JOIN PURCHASE_ORDER_D PO_D 
                        ON PO_D.PURCHASE_ORDER_ID = PO.PURCHASE_ORDER_ID
                    LEFT JOIN PURCHASE_ORDER_SD PO_SD 
                        ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                    LEFT JOIN PURCHASE_ORDER_SSD PO_SSD 
                        ON PO_SSD.PURCHASE_ORDER_SD_ID = PO_SD.PURCHASE_ORDER_SD_ID
                    LEFT JOIN Z_OUT_MO_D 
                        ON PO_SSD.REFERENCE_SOURCE_ID_ROid = Z_OUT_MO_D.Z_OUT_MO_D_ID
                    LEFT JOIN ITEM 
                        ON PO_D.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                    LEFT JOIN ITEM_LOT 
                        ON Z_OUT_MO_D.ITEM_LOT_ID = ITEM_LOT.ITEM_LOT_ID
                    LEFT JOIN Z_ASSEMBLY_CODE 
                        ON Z_OUT_MO_D.Z_PACKAGE_ASSEMBLY_CODE_ID = Z_ASSEMBLY_CODE.Z_ASSEMBLY_CODE_ID
                    LEFT JOIN Z_ASSEMBLY_CODE ZAC
                        ON Z_OUT_MO_D.Z_TESTING_ASSEMBLY_CODE_ID = ZAC.Z_ASSEMBLY_CODE_ID
                    LEFT JOIN Z_TESTING_PROGRAM ZTP
                        ON ZAC.PROGRAM_ROid = ZTP.Z_TESTING_PROGRAM_ID
                    LEFT JOIN Z_PACKAGE 
                        ON Z_ASSEMBLY_CODE.PROGRAM_ROid = Z_PACKAGE.Z_PACKAGE_ID
                    LEFT JOIN Z_PROCESSING_PURPOSE 
                        ON Z_ASSEMBLY_CODE.Z_PROCESSING_PURPOSE_ID = Z_PROCESSING_PURPOSE.Z_PROCESSING_PURPOSE_ID
                    LEFT JOIN Z_LOADING_METHOD 
                        ON Z_LOADING_METHOD.Z_LOADING_METHOD_ID = Z_PACKAGE.Z_LOADING_METHOD_ID
                    LEFT JOIN Z_WIRE 
                        ON Z_WIRE.Z_WIRE_ID = Z_PACKAGE.Z_WIRE_ID
                    LEFT JOIN Z_PACKAGE_TYPE 
                        ON Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_ID = Z_PACKAGE.Z_PACKAGE_TYPE_ID
                    LEFT JOIN FEATURE_GROUP 
                        ON FEATURE_GROUP.FEATURE_GROUP_ID = ITEM.FEATURE_GROUP_ID
                    OUTER APPLY (
                        SELECT TOP 1 *
                        FROM PURCHASE_RECEIPT_D PRD
                        WHERE PRD.ORDER_SOURCE_ID_ROid = PO_SD.PURCHASE_ORDER_SD_ID
                        ORDER BY PRD.CreateDate
                    ) PR
                    WHERE PO.PURCHASE_TYPE = 2 
                        AND PO.PURCHASE_DATE > '2024-10-21' 
                        AND ITEM.ITEM_CODE LIKE N'BC%AB' 
                        AND PO.SUPPLIER_FULL_NAME <> N'温州镁芯微电子有限公司'  
                        AND PO.SUPPLIER_FULL_NAME <> N'苏州荐恒电子科技有限公司'  
                        AND PO.SUPPLIER_FULL_NAME <> N'深圳市华新源科技有限公司'
                ) t
                WHERE 1=1 {' '.join(conditions)}
            """
            total = db.execute(text(count_query).bindparams(**{k:v for k,v in query_params.items() if k not in ['offset', 'pageSize']})).scalar()
            
            # 转换为响应对象
            assy_orders = [
                AssyOrder(
                    ID=row.ID,
                    DOC_NO=row.DOC_NO,
                    ITEM_CODE=row.ITEM_CODE,
                    Z_PACKAGE_TYPE_NAME=row.Z_PACKAGE_TYPE_NAME,
                    LOT_CODE=row.LOT_CODE,
                    BUSINESS_QTY=row.BUSINESS_QTY,
                    RECEIPTED_PRICE_QTY=row.RECEIPTED_PRICE_QTY,
                    WIP_QTY=row.WIP_QTY,
                    Z_PROCESSING_PURPOSE_NAME=row.Z_PROCESSING_PURPOSE_NAME,
                    Z_TESTING_PROGRAM_NAME=row.Z_TESTING_PROGRAM_NAME,
                    Z_ASSEMBLY_CODE=row.Z_ASSEMBLY_CODE,
                    Z_WIRE_NAME=row.Z_WIRE_NAME,
                    REMARK=row.REMARK,
                    PURCHASE_DATE=row.PURCHASE_DATE,
                    FIRST_ARRIVAL_DATE=row.FIRST_ARRIVAL_DATE,
                    SUPPLIER_FULL_NAME=row.SUPPLIER_FULL_NAME,
                    RECEIPT_CLOSE=row.RECEIPT_CLOSE
                ) for row in result
            ]
            return {
                "list": assy_orders,
                "total": total or 0
            }
        except Exception as e:
            logger.error(f"查询封装订单失败: {str(e)}")
            raise CustomException("查询封装订单失败")
    
    def get_assy_bom_by_params(self, db: Session, params: AssyBomQuery) -> Dict[str, Any]:
        """根据参数获取封装订单BOM"""
        try:
            # 构建基础查询
            base_query = """
                SELECT * FROM
                (
                SELECT * FROM HSUN_BOM_LIST
                UNION ALL
                SELECT 
                ROW_NUMBER() OVER (ORDER BY PO.PURCHASE_DATE,PO.DOC_NO) + 16820 AS ID,
                PO.DOC_NO,
                ZOMSD.Z_MAIN_CHIP,
                ITEM.ITEM_CODE,
                ITEM.ITEM_NAME,
                IL.LOT_CODE,
                CAST(ZOMSD.BUSINESS_QTY AS FLOAT) AS BUSINESS_QTY,
                CAST(ZOMSD.SECOND_QTY AS FLOAT) AS SECOND_QTY,
                ZOMSD.Z_WF_ID_STRING
                FROM PURCHASE_ORDER PO
                LEFT JOIN PURCHASE_ORDER_D PO_D
                ON PO.PURCHASE_ORDER_ID = PO_D.PURCHASE_ORDER_ID
                LEFT JOIN PURCHASE_ORDER_SD PO_SD
                ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                LEFT JOIN PURCHASE_ORDER_SSD PO_SSD
                ON PO_SSD.PURCHASE_ORDER_SD_ID = PO_SD.PURCHASE_ORDER_SD_ID
                LEFT JOIN Z_OUT_MO_D ZOMD
                ON ZOMD.Z_OUT_MO_D_ID = PO_SSD.REFERENCE_SOURCE_ID_ROid
                LEFT JOIN Z_OUT_MO_SD ZOMSD
                ON ZOMSD.Z_OUT_MO_D_ID = ZOMD.Z_OUT_MO_D_ID
                LEFT JOIN ITEM
                ON ZOMSD.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                LEFT JOIN ITEM_LOT IL
                ON IL.ITEM_LOT_ID = ZOMSD.ITEM_LOT_ID
                WHERE PO_D.PURCHASE_TYPE=2)
                AS ALL_BOM
                WHERE 1=1
            """

            # 添加查询条件
            if params.doc_no:
                base_query += " AND DOC_NO = :doc_no"

            # 执行查询
            result = db.execute(text(base_query).bindparams(doc_no=params.doc_no)).all()
            
            # 构造返回结果
            return {
                "list": [
                    AssyBom(
                        MAIN_CHIP=row.MAIN_CHIP,
                        ITEM_CODE=row.ITEM_CODE,
                        ITEM_NAME=row.ITEM_NAME,
                        LOT_CODE_NAME=row.LOT_CODE_NAME,
                        BUSINESS_QTY=row.BUSINESS_QTY,
                        SECOND_QTY=row.SECOND_QTY,
                        WAFER_ID=row.WAFER_ID
                    ) for row in result
                ]
            }
        except Exception as e:
            logger.error(f"获取封装订单BOM失败: {str(e)}")
            raise CustomException("获取封装订单BOM失败")
    
    def export_assy_order_to_excel(self, db: Session, params: AssyOrderQuery) -> bytes:
        """导出封装订单数据到Excel"""
        try:
            # 获取数据
            result = self.get_assy_order_by_params(db, params)
            assy_orders = result["list"]
            
            # 创建工作簿和工作表
            wb = Workbook()
            ws = wb.active
            ws.title = "封装订单"
            
            # 定义表头
            headers = [
                "订单编号", "芯片名称", "封装形式", "打印批号", "订单数量", 
                "收货数量", "在制数量", "加工方式", "测试程序", 
                "打线图号", "打线材料", "备注", "订单日期", "首到日期", 
                "供应商", "状态"
            ]
            
            # 设置列宽
            column_widths = {
                'A': 15,  # 订单号
                'B': 20,  # 品号
                'C': 15,  # 封装形式
                'D': 15,  # 打印批号
                'E': 12,  # 订单数量
                'F': 12,  # 收货数量
                'G': 12,  # 在制数量
                'H': 15,  # 加工方式
                'I': 15,  # 测试程序
                'J': 15,  # 打线图号
                'K': 10,  # 打线材料
                'L': 20,  # 备注
                'M': 12,  # 订单日期
                'N': 12,  # 首到日期
                'O': 25,  # 供应商
                'P': 10   # 状态
            }
            
            # 设置样式
            header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                ws.column_dimensions[get_column_letter(col)].width = column_widths[get_column_letter(col)]
            
            # 写入数据
            for row, order in enumerate(assy_orders, 2):
                data = [
                    order.DOC_NO,
                    order.ITEM_CODE,
                    order.Z_PACKAGE_TYPE_NAME,
                    order.LOT_CODE,
                    order.BUSINESS_QTY,
                    order.RECEIPTED_PRICE_QTY,
                    order.WIP_QTY,
                    order.Z_PROCESSING_PURPOSE_NAME,
                    order.Z_TESTING_PROGRAM_NAME,
                    order.Z_ASSEMBLY_CODE,
                    order.Z_WIRE_NAME,
                    order.REMARK,
                    order.PURCHASE_DATE.strftime('%Y-%m-%d') if order.PURCHASE_DATE else '',
                    order.FIRST_ARRIVAL_DATE.strftime('%Y-%m-%d') if order.FIRST_ARRIVAL_DATE else '',
                    order.SUPPLIER_FULL_NAME,
                    '已关闭' if order.RECEIPT_CLOSE else '未关闭'
                ]
                
                for col, value in enumerate(data, 1):
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = cell_alignment
                    cell.border = border
                    
                    # 设置数字列的格式
                    if col in [5, 6, 7]:  # 订单数量、已收货数量、在制数量
                        cell.number_format = '#,##0'
            
            # 冻结首行
            ws.freeze_panes = 'A2'
            
            # 保存到内存
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            return excel_file.getvalue()
            
        except Exception as e:
            logger.error(f"导出封装订单Excel失败: {str(e)}")
            raise CustomException("导出封装订单Excel失败")
        
    def get_assy_wip_by_params(self,db:Session,params:AssyWipQuery)->Dict[str,Any]:
        """获取封装在制"""
        try:
            # 构建基础查询
            base_query = """
                SELECT 
                WIP.[订单号],
                PO.SUPPLIER_FULL_NAME,
                ITEM.ITEM_CODE,
                ZPP.Z_PROCESSING_PURPOSE_NAME,
                CASE 
                    WHEN WIP.[当前工序] = N'已完成' THEN NULL
                    ELSE DATEDIFF(DAY, WIP.modified_at, GETDATE()) 
                END
                AS STRANDED,
                WIP.[当前工序],
                WIP.[预计交期],
                WIP.finished_at,
                WIP.[在线合计],
                WIP.[仓库库存],
                WIP.[扣留信息],
                WIP.[次日预计],
                WIP.[三日预计],
                WIP.[七日预计],
                WIP.[研磨],
                WIP.[切割],
                WIP.[待装片],
                WIP.[装片],
                WIP.[银胶固化],
                WIP.[等离子清洗1],
                WIP.[键合],
                WIP.[三目检],
                WIP.[等离子清洗2],
                WIP.[塑封],
                WIP.[后固化],
                WIP.[回流焊],
                WIP.[电镀],
                WIP.[打印],
                WIP.[后切割],
                WIP.[切筋成型],
                WIP.[测编打印],
                WIP.[外观检],
                WIP.[包装],
                WIP.[待入库]
                FROM huaxinAdmin_wip_assy WIP
                INNER JOIN PURCHASE_ORDER PO ON PO.DOC_NO = WIP.[订单号]
                LEFT JOIN PURCHASE_ORDER_D PO_D ON PO.PURCHASE_ORDER_ID = PO_D.PURCHASE_ORDER_ID
                LEFT JOIN PURCHASE_ORDER_SD PO_SD ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                LEFT JOIN PURCHASE_ORDER_SSD PO_SSD ON PO_SSD.PURCHASE_ORDER_SD_ID = PO_SD.PURCHASE_ORDER_SD_ID
                LEFT JOIN Z_OUT_MO_D ZOMD ON PO_SSD.REFERENCE_SOURCE_ID_ROid = ZOMD.Z_OUT_MO_D_ID
                LEFT JOIN ITEM ON PO_D.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                LEFT JOIN ITEM_LOT ON ZOMD.ITEM_LOT_ID = ITEM_LOT.ITEM_LOT_ID
                LEFT JOIN Z_ASSEMBLY_CODE ZAC ON ZOMD.Z_PACKAGE_ASSEMBLY_CODE_ID = ZAC.Z_ASSEMBLY_CODE_ID
                LEFT JOIN Z_PACKAGE ON ZAC.PROGRAM_ROid = Z_PACKAGE.Z_PACKAGE_ID
                LEFT JOIN Z_PROCESSING_PURPOSE ZPP ON ZAC.Z_PROCESSING_PURPOSE_ID = ZPP.Z_PROCESSING_PURPOSE_ID
                WHERE 1=1 AND ITEM.ITEM_CODE LIKE N'BC%AB'
            """
            result = db.execute(text(base_query)).all()
            
            # 构建查询条件
            conditions = []
            query_params = {}
            
            # 参数验证和清理
            if params.doc_no and isinstance(params.doc_no, str):
                conditions.append("AND WIP.[订单号] LIKE :doc_no")
                query_params["doc_no"] = f"%{self._clean_input(params.doc_no)}%"
            
            if params.item_code and isinstance(params.item_code, str):
                conditions.append("AND ITEM.ITEM_CODE LIKE :item_code")
                query_params["item_code"] = f"%{self._clean_input(params.item_code)}%"
                
            if params.supplier and isinstance(params.supplier, str):
                conditions.append("AND PO.SUPPLIER_FULL_NAME LIKE :supplier")
                query_params["supplier"] = f"%{self._clean_input(params.supplier)}%"
                
            if params.current_process and isinstance(params.current_process, str):
                conditions.append("AND WIP.[当前工序] LIKE :current_process")
                query_params["current_process"] = f"%{self._clean_input(params.current_process)}%"
                
            if params.is_finished is not None:
                if params.is_finished == 1:
                    conditions.append("AND WIP.[当前工序] = N'已完成'")
                else:
                    conditions.append("AND WIP.[当前工序] != N'已完成'")
                    
            if params.is_stranded is not None:
                if params.is_stranded == 0:
                    conditions.append("""
                                      AND CASE 
                                      WHEN WIP.[当前工序] = N'已完成' THEN NULL
                                      ELSE DATEDIFF(DAY, WIP.modified_at, GETDATE()) 
                                      END = 0
                                      """)
                else:
                    conditions.append("""
                                      AND CASE 
                                      WHEN WIP.[当前工序] = N'已完成' THEN NULL
                                      ELSE DATEDIFF(DAY, WIP.modified_at, GETDATE()) 
                                      END != 0
                                      """)
                    
            if params.days is not None:
                if params.days == 1:
                    conditions.append("AND WIP.[次日预计] > 0")
                elif params.days == 3:
                    conditions.append("AND WIP.[三日预计] > 0")
                elif params.days == 7:
                    conditions.append("AND WIP.[七日预计] > 0")
                    
            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)
            
            # 添加排序
            query += " ORDER BY WIP.[订单号]"
            
            # 添加分页
            if params.pageIndex and params.pageSize:
                offset = (params.pageIndex - 1) * params.pageSize
                query += " OFFSET :offset ROWS FETCH NEXT :pageSize ROWS ONLY"
                query_params["offset"] = offset
                query_params["pageSize"] = params.pageSize
                
            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()
            
            # 获取总记录数
            count_query = f"""
                SELECT COUNT(1)
                FROM huaxinAdmin_wip_assy WIP
                LEFT JOIN PURCHASE_ORDER PO ON PO.DOC_NO = WIP.[订单号]
                LEFT JOIN PURCHASE_ORDER_D PO_D ON PO.PURCHASE_ORDER_ID = PO_D.PURCHASE_ORDER_ID
                LEFT JOIN PURCHASE_ORDER_SD PO_SD ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                LEFT JOIN PURCHASE_ORDER_SSD PO_SSD ON PO_SSD.PURCHASE_ORDER_SD_ID = PO_SD.PURCHASE_ORDER_SD_ID 
                LEFT JOIN Z_OUT_MO_D ZOMD ON PO_SSD.REFERENCE_SOURCE_ID_ROid = ZOMD.Z_OUT_MO_D_ID
                LEFT JOIN ITEM ON PO_D.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                LEFT JOIN ITEM_LOT ON ZOMD.ITEM_LOT_ID = ITEM_LOT.ITEM_LOT_ID
                LEFT JOIN Z_ASSEMBLY_CODE ZAC ON ZOMD.Z_PACKAGE_ASSEMBLY_CODE_ID = ZAC.Z_ASSEMBLY_CODE_ID
                LEFT JOIN Z_PACKAGE ON ZAC.PROGRAM_ROid = Z_PACKAGE.Z_PACKAGE_ID
                LEFT JOIN Z_PROCESSING_PURPOSE ZPP ON ZAC.Z_PROCESSING_PURPOSE_ID = ZPP.Z_PROCESSING_PURPOSE_ID 
                WHERE 1=1
                {' '.join(conditions)}
            """
            total = db.execute(text(count_query).bindparams(**{k:v for k,v in query_params.items() if k not in ['offset', 'pageSize']})).scalar()
            
            # 转换为响应对象
            assy_wips = [
                AssyWip(
                    DOC_NO=row.订单号,
                    SUPPLIER_FULL_NAME=row.SUPPLIER_FULL_NAME,
                    ITEM_CODE=row.ITEM_CODE,
                    Z_PROCESSING_PURPOSE_NAME=row.Z_PROCESSING_PURPOSE_NAME,
                    STRANDED=row.STRANDED,
                    CURRENT_PROCESS=row.当前工序,
                    EXPECTED_DELIVERY_DATE=row.预计交期,
                    FINISHED_AT=row.finished_at,
                    ONLINE_TOTAL=row.在线合计,
                    WAREHOUSE_INVENTORY=row.仓库库存,
                    HOLD_INFO=row.扣留信息,
                    NEXT_DAY_EXPECTED=row.次日预计,
                    THREE_DAY_EXPECTED=row.三日预计,
                    SEVEN_DAY_EXPECTED=row.七日预计,
                    POLISHING=row.研磨,
                    CUTTING=row.切割,
                    WAITING_FOR_INSTALLATION=row.待装片,
                    INSTALLATION=row.装片,
                    SILVER_GLUE_CURE=row.银胶固化,
                    PLASMA_CLEANING_1=row.等离子清洗1,
                    BONDING=row.键合,
                    THREE_POINT_INSPECTION=row.三目检,
                    PLASMA_CLEANING_2=row.等离子清洗2,
                    SEALING=row.塑封,
                    POST_CURE=row.后固化,
                    REFLOW_SOLDERING=row.回流焊,
                    ELECTROPLATING=row.电镀,
                    PRINTING=row.打印,
                    POST_CUTTING=row.后切割,
                    CUTTING_AND_SHAPING=row.切筋成型,
                    MEASUREMENT_AND_PRINTING=row.测编打印,
                    APPEARANCE_INSPECTION=row.外观检,    
                    PACKING=row.包装,
                    WAITING_FOR_WAREHOUSE_INVENTORY=row.待入库
                ) for row in result
            ]
            
            return {
                "list": assy_wips,
                "total": total or 0
            }
            
        except Exception as e:
            logger.error(f"查询封装在制失败: {str(e)}")
            raise CustomException("查询封装在制失败")
        
    def get_assy_order_items(self,db:Session,params:AssyOrderItemsQuery)->Dict[str,Any]:
        """获取封装在制品号"""
        try:
            base_query = """
                SELECT DISTINCT ITEM_CODE
                FROM ITEM
                WHERE ITEM_CODE LIKE N'BC%AB'
            """

            # 构建查询条件
            conditions = []
            query_params = {}

            if params.item_code:
                # 将输入的品号转换为大写
                item_code = params.item_code.upper()
                conditions.append("AND ITEM_CODE LIKE :item_code")
                query_params["item_code"] = f"%{self._clean_input(item_code)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions) 

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            items = [
                {
                    "label": row.ITEM_CODE,
                    "value": row.ITEM_CODE
                } for row in result
            ]

            return {
                "list": items
            }
        except Exception as e:
            logger.error(f"获取封装在制品号失败: {str(e)}")
            raise CustomException("获取封装在制品号失败")
    
    def get_assy_order_package_type(self,db:Session,params:AssyOrderPackageTypeQuery)->Dict[str,Any]:
        """获取封装订单类型"""
        try:
            base_query = """
                SELECT DISTINCT Z_PACKAGE_TYPE_NAME
                FROM Z_PACKAGE_TYPE
                WHERE 1=1
            """

            # 构建查询条件
            conditions = []
            query_params = {}

            if params.package_type:
                # 将输入的封装类型转换为大写
                package_type = params.package_type.upper()
                conditions.append("AND Z_PACKAGE_TYPE_NAME LIKE :package_type")
                query_params["package_type"] = f"%{self._clean_input(package_type)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            package_types = [
                {
                    "label": row.Z_PACKAGE_TYPE_NAME,
                    "value": row.Z_PACKAGE_TYPE_NAME
                } for row in result
            ]   

            return {
                "list": package_types
            }
        except Exception as e:
            logger.error(f"获取封装订单类型失败: {str(e)}")
            raise CustomException("获取封装订单类型失败")
        
    def get_assy_order_supplier(self,db:Session,params:AssyOrderSupplierQuery)->Dict[str,Any]:
        """获取封装订单供应商"""
        try:
            base_query = """
                SELECT DISTINCT SUPPLIER_FULL_NAME
                FROM PURCHASE_ORDER
                WHERE 1=1
            """

            # 构建查询条件
            conditions = []
            query_params = {}

            if params.supplier:
                conditions.append("AND SUPPLIER_FULL_NAME LIKE :supplier")
                query_params["supplier"] = f"%{self._clean_input(params.supplier)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            suppliers = [
                {
                    "label": row.SUPPLIER_FULL_NAME,
                    "value": row.SUPPLIER_FULL_NAME
                } for row in result
            ]

            return {
                "list": suppliers
            }
        except Exception as e:
            logger.error(f"获取封装订单供应商失败: {str(e)}")
            raise CustomException("获取封装订单供应商失败")
        
    def get_stock_by_params(self,db:Session,params:StockQuery)->Dict[str,Any]:
        """获取库存"""
        try:
            base_query = """
                    SELECT FG.FEATURE_GROUP_NAME,
                    ITEM.ITEM_CODE,ITEM.ITEM_NAME,
                    IL.LOT_CODE,
                    W.WAREHOUSE_NAME,
                    CAST(SUM(A.INVENTORY_QTY) AS INT) AS INVENTORY_QTY,CAST(SUM(A.SECOND_QTY) AS FLOAT) AS SECOND_QTY,
                    B.Z_BIN_LEVEL_NAME,
                    T.Z_TESTING_PROGRAM_NAME,
                    BP.Z_BURNING_PROGRAM_NAME
                    FROM Z_WF_IC_WAREHOUSE_BIN A
                    LEFT JOIN ITEM
                    ON ITEM.ITEM_BUSINESS_ID = A.ITEM_ID
                    LEFT JOIN ITEM_LOT IL
                    ON IL.ITEM_LOT_ID = A.ITEM_LOT_ID
                    LEFT JOIN FEATURE_GROUP FG
                    ON FG.FEATURE_GROUP_ID = ITEM.FEATURE_GROUP_ID
                    LEFT JOIN Z_BIN_LEVEL B
                    ON B.Z_BIN_LEVEL_ID = A.Z_BIN_LEVEL_ID
                    LEFT JOIN Z_TESTING_PROGRAM T
                    ON T.Z_TESTING_PROGRAM_ID = A.Z_TESTING_PROGRAM_ID
                    LEFT JOIN Z_BURNING_PROGRAM BP
                    ON BP.Z_BURNING_PROGRAM_ID = A.Z_BURNING_PROGRAM_ID
                    LEFT JOIN WAREHOUSE W
                    ON A.WAREHOUSE_ID = W.WAREHOUSE_ID
                    GROUP BY FG.FEATURE_GROUP_NAME,ITEM.ITEM_CODE,ITEM.ITEM_NAME,IL.LOT_CODE,W.WAREHOUSE_NAME,B.Z_BIN_LEVEL_NAME,
                    T.Z_TESTING_PROGRAM_NAME,BP.Z_BURNING_PROGRAM_NAME
                    HAVING SUM(A.INVENTORY_QTY) > 0 
                    """
            # 构建查询条件
            having_conditions = []
            query_params = {}

            # 参数验证和清理
            if params.feature_group_name:
                feature_group_names = [self._clean_input(name) for name in params.feature_group_name]
                placeholders = [f":feature_group_name_{i}" for i in range(len(feature_group_names))]
                having_conditions.append(f"AND FG.FEATURE_GROUP_NAME IN ({','.join(placeholders)})")
                for i, name in enumerate(feature_group_names):
                    query_params[f"feature_group_name_{i}"] = name

            if params.item_code:
                item_codes = [self._clean_input(code) for code in params.item_code]
                placeholders = [f":item_code_{i}" for i in range(len(item_codes))]
                having_conditions.append(f"AND ITEM.ITEM_CODE IN ({','.join(placeholders)})")
                for i, code in enumerate(item_codes):
                    query_params[f"item_code_{i}"] = code

            if params.item_name:
                item_names = [self._clean_input(name) for name in params.item_name]
                item_name_conditions = []
                for i, name in enumerate(item_names):
                    item_name_conditions.append(f"UPPER(ITEM.ITEM_NAME) LIKE UPPER(:item_name_{i})")
                    query_params[f"item_name_{i}"] = f"%{name}%"
                having_conditions.append(f"AND ({' OR '.join(item_name_conditions)})")

            if params.lot_code:
                lot_codes = [self._clean_input(lot) for lot in params.lot_code]
                lot_code_conditions = []
                for i, lot in enumerate(lot_codes):
                    lot_code_conditions.append(f"UPPER(IL.LOT_CODE) LIKE UPPER(:lot_code_{i})")
                    query_params[f"lot_code_{i}"] = f"%{lot}%"
                having_conditions.append(f"AND ({' OR '.join(lot_code_conditions)})")

            if params.warehouse_name:
                warehouse_names = [self._clean_input(name) for name in params.warehouse_name]
                placeholders = [f":warehouse_name_{i}" for i in range(len(warehouse_names))]
                having_conditions.append(f"AND W.WAREHOUSE_NAME IN ({','.join(placeholders)})")
                for i, name in enumerate(warehouse_names):
                    query_params[f"warehouse_name_{i}"] = name

            if params.testing_program:
                testing_programs = [self._clean_input(name) for name in params.testing_program]
                placeholders = [f":testing_program_{i}" for i in range(len(testing_programs))]
                having_conditions.append(f"AND UPPER(T.Z_TESTING_PROGRAM_NAME) IN ({','.join([f'UPPER({p})' for p in placeholders])})")
                for i, name in enumerate(testing_programs):
                    query_params[f"testing_program_{i}"] = name

            if params.burning_program:
                burning_programs = [self._clean_input(name) for name in params.burning_program]
                placeholders = [f":burning_program_{i}" for i in range(len(burning_programs))]
                having_conditions.append(f"AND UPPER(BP.Z_BURNING_PROGRAM_NAME) IN ({','.join([f'UPPER({p})' for p in placeholders])})")
                for i, name in enumerate(burning_programs):
                    query_params[f"burning_program_{i}"] = name

            # 构建完整的 SQL 查询语句
            if having_conditions:
                query = f"{base_query} {' '.join(having_conditions)} ORDER BY ITEM.ITEM_CODE,IL.LOT_CODE"
            else:
                query = f"{base_query} ORDER BY ITEM.ITEM_CODE,IL.LOT_CODE"

            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            stocks = [
                Stock(
                    FEATURE_GROUP_NAME=row.FEATURE_GROUP_NAME,
                    ITEM_CODE=row.ITEM_CODE,
                    ITEM_NAME=row.ITEM_NAME,
                    LOT_CODE=row.LOT_CODE,
                    WAREHOUSE_NAME=row.WAREHOUSE_NAME,
                    INVENTORY_QTY=row.INVENTORY_QTY,
                    SECOND_QTY=row.SECOND_QTY,
                    Z_BIN_LEVEL_NAME=row.Z_BIN_LEVEL_NAME,
                    Z_TESTING_PROGRAM_NAME=row.Z_TESTING_PROGRAM_NAME,
                    Z_BURNING_PROGRAM_NAME=row.Z_BURNING_PROGRAM_NAME
                ) for row in result
            ]
            return {"list": stocks}
        except Exception as e:
            logger.error(f"查询库存失败: {str(e)}")
            raise CustomException("查询库存失败")
    
    def get_wafer_id_qty_detail_by_params(self,db:Session,params:WaferIdQtyDetailQuery)->List[WaferIdQtyDetail]:
        """根据参数获取晶圆ID数量明细"""
        try:
            base_query = """
                SELECT 
                ITEM.ITEM_CODE,ITEM.ITEM_NAME,
                IL.LOT_CODE,
                T.Z_TESTING_PROGRAM_NAME,
                (A.WF_ID + '#') AS WF_ID,
                B.Z_BIN_LEVEL_NAME,
                CAST(A.INVENTORY_QTY AS INT) AS INVENTORY_QTY,CAST(A.SECOND_QTY AS FLOAT) AS SECOND_QTY,
                W.WAREHOUSE_NAME
                FROM Z_WF_IC_WAREHOUSE_BIN A
                LEFT JOIN ITEM
                ON ITEM.ITEM_BUSINESS_ID = A.ITEM_ID
                LEFT JOIN ITEM_LOT IL
                ON IL.ITEM_LOT_ID = A.ITEM_LOT_ID
                LEFT JOIN FEATURE_GROUP FG
                ON FG.FEATURE_GROUP_ID = ITEM.FEATURE_GROUP_ID
                LEFT JOIN Z_BIN_LEVEL B
                ON B.Z_BIN_LEVEL_ID = A.Z_BIN_LEVEL_ID
                LEFT JOIN Z_TESTING_PROGRAM T
                ON T.Z_TESTING_PROGRAM_ID = A.Z_TESTING_PROGRAM_ID
                LEFT JOIN WAREHOUSE W
                ON A.WAREHOUSE_ID = W.WAREHOUSE_ID
                WHERE A.INVENTORY_QTY > 0
                """
            # 构建查询条件
            conditions = []
            query_params = {}

            if params.item_code:
                conditions.append("AND ITEM.ITEM_CODE LIKE :item_code")
                query_params["item_code"] = f"%{self._clean_input(params.item_code)}%"

            if params.lot_code:
                conditions.append("AND IL.LOT_CODE LIKE :lot_code")
                query_params["lot_code"] = f"%{self._clean_input(params.lot_code)}%"
                
            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            # 添加排序
            query += " ORDER BY ITEM.ITEM_CODE,IL.LOT_CODE,CAST(A.WF_ID AS INT)"
            
            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            wafer_id_qty_details = [
                WaferIdQtyDetail(
                    ITEM_CODE=row.ITEM_CODE,
                    LOT_CODE=row.LOT_CODE,
                    Z_TESTING_PROGRAM_NAME=row.Z_TESTING_PROGRAM_NAME,
                    WF_ID=row.WF_ID,
                    Z_BIN_LEVEL_NAME=row.Z_BIN_LEVEL_NAME,
                    INVENTORY_QTY=row.INVENTORY_QTY,
                    SECOND_QTY=row.SECOND_QTY,
                    WAREHOUSE_NAME=row.WAREHOUSE_NAME
                ) for row in result
            ]

            return {"list": wafer_id_qty_details}
        
        except Exception as e:
            logger.error(f"获取晶圆ID数量明细失败: {str(e)}")
            raise CustomException(status_code=500, message="获取晶圆ID数量明细失败")
    
    def get_stock_summary_by_params(self,db:Session,params:StockSummaryQuery)->List[StockSummary]:
        """根据参数获取库存汇总"""
        try:
            base_query = """
                SELECT 
                FG.FEATURE_GROUP_NAME,
                ITEM.ITEM_NAME,
                W.WAREHOUSE_NAME,
                CAST(SUM(A.INVENTORY_QTY) AS INT) AS INVENTORY_QTY,
                AVG(DATEDIFF(Month, ITEM.CreateDate , GETDATE())) AS AVERAGE_STOCK_AGE
                FROM Z_WF_IC_WAREHOUSE_BIN A
                LEFT JOIN ITEM
                ON ITEM.ITEM_BUSINESS_ID = A.ITEM_ID
                LEFT JOIN FEATURE_GROUP FG
                ON FG.FEATURE_GROUP_ID = ITEM.FEATURE_GROUP_ID
                LEFT JOIN WAREHOUSE W
                ON A.WAREHOUSE_ID = W.WAREHOUSE_ID
                WHERE W.WAREHOUSE_NAME NOT LIKE N'%原材料%'
            """
            # 构建查询条件
            conditions = []
            query_params = {}
            if params.item_name:
                conditions.append("AND ITEM.ITEM_NAME LIKE :item_name")
                query_params["item_name"] = f"%{self._clean_input(params.item_name)}%"

            if params.feature_group_name:
                conditions.append("AND FG.FEATURE_GROUP_NAME LIKE :feature_group_name")
                query_params["feature_group_name"] = f"%{self._clean_input(params.feature_group_name)}%"

            if params.warehouse_name:
                conditions.append("AND W.WAREHOUSE_NAME LIKE :warehouse_name")
                query_params["warehouse_name"] = f"%{self._clean_input(params.warehouse_name)}%"

            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)

            query += """ GROUP BY FG.FEATURE_GROUP_NAME,ITEM.ITEM_NAME,W.WAREHOUSE_NAME
                        HAVING SUM(A.INVENTORY_QTY) > 0
                        ORDER BY ITEM.ITEM_NAME
                    """
            # 执行查询
            stmt = text(query).bindparams(**query_params)
            result = db.execute(stmt).all()

            # 转换为响应对象
            stock_summaries = [
                StockSummary(
                    FEATURE_GROUP_NAME=row.FEATURE_GROUP_NAME,
                    ITEM_NAME=row.ITEM_NAME,
                    WAREHOUSE_NAME=row.WAREHOUSE_NAME,
                    INVENTORY_QTY=row.INVENTORY_QTY,
                    AVERAGE_STOCK_AGE=row.AVERAGE_STOCK_AGE
                ) for row in result
            ]
            return {"list": stock_summaries}
        except Exception as e:
            logger.error(f"获取库存汇总失败: {str(e)}")
            raise CustomException("获取库存汇总失败")

    def export_stock_by_params(self,db:Session,params:StockQuery)->bytes:
        """导出库存数据到Excel"""
        try:
            # 获取库存数据
            result = self.get_stock_by_params(db, params)
            stock_list = result["list"]
            
            # 创建Excel工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "库存数据"
            
            # 定义表头
            headers = ["品号群组", "物料名称", "物料编码", "批号", "BIN等级", "测试程序", "烧录程序","仓库","库存数量","数量片数"]
            
            # 设置列宽
            column_widths = {
               'A': 15,
               'B': 25,
               'C': 30,
               'D': 20,
               'E': 10,
               'F': 20,
               'G': 20,
               'H': 20,
               'I': 12,
               'J': 10
            }
            
            # 设置样式
            header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                ws.column_dimensions[get_column_letter(col)].width = column_widths[get_column_letter(col)]
            
            # 写入数据
            for row, order in enumerate(stock_list, 2):
                data = [
                    order.FEATURE_GROUP_NAME if order.FEATURE_GROUP_NAME else '',
                    order.ITEM_NAME if order.ITEM_NAME else '',
                    order.ITEM_CODE if order.ITEM_CODE else '',
                    order.LOT_CODE if order.LOT_CODE else '',
                    order.Z_BIN_LEVEL_NAME if order.Z_BIN_LEVEL_NAME else '',
                    order.Z_TESTING_PROGRAM_NAME if order.Z_TESTING_PROGRAM_NAME else '',
                    order.Z_BURNING_PROGRAM_NAME if order.Z_BURNING_PROGRAM_NAME else '',
                    order.WAREHOUSE_NAME if order.WAREHOUSE_NAME else '',
                    order.INVENTORY_QTY if order.INVENTORY_QTY is not None else 0,
                    order.SECOND_QTY if order.SECOND_QTY is not None else 0.0
                ]

                for col, value in enumerate(data, 1):
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = cell_alignment
                    cell.border = border
                    
                    # 设置数字列的格式
                    if col in [9, 10]:  # 库存数量、数量片数
                        cell.number_format = '#,##0'
                    
            # 冻结首行
            ws.freeze_panes = 'A2'
            
            # 保存到内存
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            return excel_file.getvalue()
            
        except Exception as e:
            logger.error(f"导出库存Excel失败: {str(e)}")
            raise CustomException("导出库存Excel失败")
        
    def get_global_report(self,db:Session)->List[GlobalReport]:
        """获取综合报表"""
        try:
            base_query = text("""
                WITH SD AS(
                SELECT 
                    STK.ITEM_NAME,
                    STK.TOTAL_FINISHED_GOODS,
                    STK.TOP_FINISHED_GOODS,
                    STK.BACK_FINISHED_GOODS,
                    STK.TOTAL_SEMI_MANUFACTURED,
                    STK.TOP_SEMI_MANUFACTURED,
                    STK.BACK_SEMI_MANUFACTURED,
                    SGK.SG_QTY,
                    SGK.SG_FINISHED_GOODS,
                    SGK.SG_SEMI_MANUFACTURED,
                    NO_TESTED_WAFER,
                    TESTED_WAFER,
                    OUTSOURCING_WAFER
                FROM
                    (
                    SELECT 
                    ITEM_NAME,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CP%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS TOTAL_FINISHED_GOODS,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CP%ZY%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS TOP_FINISHED_GOODS,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CP%BY%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS BACK_FINISHED_GOODS,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'BC%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS TOTAL_SEMI_MANUFACTURED,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'BC%ZY%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS TOP_SEMI_MANUFACTURED,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'BC%BY%' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS BACK_SEMI_MANUFACTURED,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CL%WF' THEN SECOND_QTY ELSE 0 END) AS FLOAT) AS NO_TESTED_WAFER,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CL%CP' THEN SECOND_QTY ELSE 0 END) AS FLOAT) AS TESTED_WAFER,
                    CAST(SUM(CASE WHEN ITEM_CODE LIKE N'CL%WG' THEN INVENTORY_QTY ELSE 0 END) AS INT) AS OUTSOURCING_WAFER
                    FROM
                    (
                        SELECT 
                        ITEM.ITEM_CODE,
                        CASE 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                            ELSE ITEM.ITEM_NAME
                        END AS ITEM_NAME,
                        SUM(A.INVENTORY_QTY) AS INVENTORY_QTY,
                        SUM(A.SECOND_QTY) AS SECOND_QTY
                        FROM Z_WF_IC_WAREHOUSE_BIN A
                        LEFT JOIN ITEM
                            ON ITEM.ITEM_BUSINESS_ID = A.ITEM_ID
                        LEFT JOIN WAREHOUSE W
                            ON A.WAREHOUSE_ID = W.WAREHOUSE_ID
                        WHERE A.INVENTORY_QTY > 0
                        GROUP BY
                            ITEM.ITEM_CODE,
                            CASE 
                                WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                                WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                                WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                                ELSE ITEM.ITEM_NAME
                            END
                        ) AS NT
                    GROUP BY ITEM_NAME
                    ) AS STK
                LEFT JOIN 
                    (SELECT 
                        CASE 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                            ELSE ITEM.ITEM_NAME
                        END AS ITEM_NAME,
                        CAST(SUM(A.INVENTORY_QTY) AS INT) AS SG_QTY,
                        CAST(SUM(CASE WHEN W.WAREHOUSE_NAME=N'苏工院（半成品）' THEN A.INVENTORY_QTY ELSE 0 END) AS INT) AS SG_SEMI_MANUFACTURED,
                        CAST(SUM(CASE WHEN W.WAREHOUSE_NAME=N'苏工院（产成品）' THEN A.INVENTORY_QTY ELSE 0 END) AS INT) AS SG_FINISHED_GOODS
                        FROM Z_WF_IC_WAREHOUSE_BIN A
                        LEFT JOIN ITEM
                        ON ITEM.ITEM_BUSINESS_ID = A.ITEM_ID
                        LEFT JOIN WAREHOUSE W
                        ON A.WAREHOUSE_ID = W.WAREHOUSE_ID
                        WHERE A.INVENTORY_QTY > 0 AND (W.WAREHOUSE_NAME = N'苏工院（半成品）' OR W.WAREHOUSE_NAME = N'苏工院（产成品）')
                        GROUP BY 
                        CASE 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                            ELSE ITEM.ITEM_NAME
                        END) AS SGK
                    ON STK.ITEM_NAME = SGK.ITEM_NAME
                    ),
                    
                WIP AS
                (	
                    SELECT
                    ITEM_NAME,
                    SUM(CASE WHEN ITEM_CODE LIKE N'CL%WF' THEN WIP_QTY ELSE 0 END ) AS PURCHASE_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'CL%WG' THEN WIP_QTY ELSE 0 END ) AS OUTSOURCING_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'BC%AB' THEN WIP_QTY ELSE 0 END ) AS PACKAGE_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'BC%ZY%AB' THEN WIP_QTY ELSE 0 END ) AS PACKAGE_TOP_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'BC%BY%AB' THEN WIP_QTY ELSE 0 END ) AS PACKAGE_BACK_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'CL%CP' THEN WIP_QTY ELSE 0 END ) AS CP_WIP_QTY,
                    SUM(CASE WHEN ITEM_CODE LIKE N'CP%' THEN WIP_QTY ELSE 0 END ) AS SECONDARY_OUTSOURCING_WIP_QTY
                    FROM
                    (	
                        SELECT
                            ITEM.ITEM_CODE,
                            CASE 
                                    WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                                    WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                                    WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                                    ELSE ITEM.ITEM_NAME
                                END AS ITEM_NAME,
                            SUM(
                            CASE 
                                    WHEN PO.[CLOSE] <> N'0' THEN 0
                                    WHEN PO_D.BUSINESS_QTY <> 0 AND (PO_D.RECEIPTED_PRICE_QTY / PO_D.BUSINESS_QTY) > 0.992 THEN 0
                                    ELSE CAST((PO_D.BUSINESS_QTY*0.996 - PO_D.RECEIPTED_PRICE_QTY) AS INT)
                            END) AS WIP_QTY
                        FROM PURCHASE_ORDER PO
                        LEFT JOIN PURCHASE_ORDER_D PO_D 
                                ON PO_D.PURCHASE_ORDER_ID = PO.PURCHASE_ORDER_ID
                        LEFT JOIN PURCHASE_ORDER_SD PO_SD 
                                ON PO_SD.PURCHASE_ORDER_D_ID = PO_D.PURCHASE_ORDER_D_ID
                        LEFT JOIN ITEM
                                ON PO_D.ITEM_ID = ITEM.ITEM_BUSINESS_ID
                        WHERE PO_SD.RECEIPT_CLOSE = 0
                                AND  
                                ((CASE 
                                        WHEN PO.[CLOSE] <> N'0' THEN 0
                                        WHEN PO_D.BUSINESS_QTY <> 0 AND (PO_D.RECEIPTED_PRICE_QTY / PO_D.BUSINESS_QTY) > 0.992 THEN 0
                                        ELSE CAST(((PO_D.BUSINESS_QTY * 0.996) - PO_D.RECEIPTED_PRICE_QTY) AS INT)
                                END) > 996
                                OR PO.PURCHASE_DATE > DATEADD(MONTH, -3, GETDATE()))
                        GROUP BY 
                        ITEM.ITEM_CODE,
                        CASE 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-BY' THEN REPLACE(ITEM.ITEM_NAME, '-BY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZY' THEN REPLACE(ITEM.ITEM_NAME, '-ZY', '') 
                            WHEN RIGHT(ITEM.ITEM_NAME,3)='-ZB' THEN REPLACE(ITEM.ITEM_NAME, '-ZB', '')
                            ELSE ITEM.ITEM_NAME
                        END) AS NT
                    GROUP BY ITEM_NAME
                ),
                BL AS
                (
                SELECT 
                ROW_NUMBER() OVER (ORDER BY MAIN_CHIP,DEPUTY_CHIP,CHIP_NAME) + 10000 AS ROW,
                BOM.*
                FROM
                (
                SELECT 
                MAX(CASE WHEN RowNum = 1 THEN NT.WAFER_NAME END) AS MAIN_CHIP,
                MAX(CASE WHEN RowNum = 2 THEN NT.WAFER_NAME END) AS DEPUTY_CHIP,
                    CHIP_NAME
                FROM
                (
                SELECT LEFT(IT.ITEM_NAME, LEN(IT.ITEM_NAME)-3) AS CHIP_NAME,ROW_NUMBER() OVER(PARTITION BY IT.ITEM_CODE ORDER BY BD.Z_MAIN_CHIP) AS RowNum,ITEM.ITEM_NAME AS WAFER_NAME
                FROM BOM_PRODUCT BP
                LEFT JOIN ITEM IT
                ON BP.ITEM_ID = IT.ITEM_BUSINESS_ID
                LEFT JOIN BOM_D BD
                ON BD.BOM_ID =BP.BOM_ID 
                LEFT JOIN ITEM 
                ON BD.SOURCE_ID_ROid = ITEM.ITEM_BUSINESS_ID
                WHERE IT.STATUS != 3 AND IT.ITEM_NAME <> N'AZ1' AND IT.ITEM_CODE LIKE N'BC%AB'
                ) AS NT
                GROUP BY NT.CHIP_NAME
                ) AS BOM 
                )

                SELECT
                BL.ROW,
                BL.MAIN_CHIP,
                BL.CHIP_NAME,
                ISNULL(SD1.TOTAL_FINISHED_GOODS, 0) AS TOTAL_FINISHED_GOODS,
                ISNULL(SD1.TOP_FINISHED_GOODS, 0) AS TOP_FINISHED_GOODS,
                ISNULL(SD1.BACK_FINISHED_GOODS, 0) AS BACK_FINISHED_GOODS,
                ISNULL(SD1.TOTAL_SEMI_MANUFACTURED, 0) AS TOTAL_SEMI_MANUFACTURED,
                ISNULL(SD1.TOP_SEMI_MANUFACTURED, 0) AS TOP_SEMI_MANUFACTURED,
                ISNULL(SD1.BACK_SEMI_MANUFACTURED, 0) AS BACK_SEMI_MANUFACTURED,
                ISNULL(WIP3.PACKAGE_WIP_QTY, 0) AS PACKAGE_WIP_QTY,
                ISNULL(WIP3.PACKAGE_TOP_WIP_QTY, 0) AS PACKAGE_TOP_WIP_QTY,
                ISNULL(WIP3.PACKAGE_BACK_WIP_QTY, 0) AS PACKAGE_BACK_WIP_QTY,
                ISNULL(SD1.SG_QTY, 0) AS SG_QTY,
                ISNULL(SD1.SG_FINISHED_GOODS, 0) AS SG_FINISHED_GOODS,
                ISNULL(SD1.SG_SEMI_MANUFACTURED, 0) AS SG_SEMI_MANUFACTURED,
                ISNULL(WIP3.SECONDARY_OUTSOURCING_WIP_QTY, 0) AS SECONDARY_OUTSOURCING_WIP_QTY,
                ISNULL(WIP1.PURCHASE_WIP_QTY, 0) AS PURCHASE_WIP_QTY,
                ISNULL(WIP1.CP_WIP_QTY, 0) AS CP_WIP_QTY,
                ISNULL(SD2.NO_TESTED_WAFER, 0) AS NO_TESTED_WAFER,
                ISNULL(SD2.TESTED_WAFER, 0) AS TESTED_WAFER,
                BL.DEPUTY_CHIP,
                ISNULL(WIP2.OUTSOURCING_WIP_QTY, 0) AS OUTSOURCING_WIP_QTY,
                ISNULL(SD3.OUTSOURCING_WAFER, 0) AS OUTSOURCING_WAFER
                FROM BL
                LEFT JOIN SD SD1 ON SD1.ITEM_NAME = BL.CHIP_NAME
                LEFT JOIN SD SD2 ON SD2.ITEM_NAME = BL.MAIN_CHIP
                LEFT JOIN SD SD3 ON SD3.ITEM_NAME = BL.DEPUTY_CHIP
                LEFT JOIN WIP WIP1 ON WIP1.ITEM_NAME = BL.MAIN_CHIP
                LEFT JOIN WIP WIP2 ON WIP2.ITEM_NAME = BL.DEPUTY_CHIP
                LEFT JOIN WIP WIP3 ON WIP3.ITEM_NAME = BL.CHIP_NAME
                ORDER BY BL.ROW
            """)
            result = db.execute(base_query).all()
            
            # 将查询结果转换为GlobalReport对象列表
            reports = []
            for row in result:
                report_data = {
                    "ROW": row.ROW,
                    "MAIN_CHIP": row.MAIN_CHIP,
                    "CHIP_NAME": row.CHIP_NAME,
                    "TOTAL_FINISHED_GOODS": row.TOTAL_FINISHED_GOODS if row.TOTAL_FINISHED_GOODS != 0 else None,
                    "TOP_FINISHED_GOODS": row.TOP_FINISHED_GOODS if row.TOP_FINISHED_GOODS != 0 else None,
                    "BACK_FINISHED_GOODS": row.BACK_FINISHED_GOODS if row.BACK_FINISHED_GOODS != 0 else None,
                    "TOTAL_SEMI_MANUFACTURED": row.TOTAL_SEMI_MANUFACTURED if row.TOTAL_SEMI_MANUFACTURED != 0 else None,
                    "TOP_SEMI_MANUFACTURED": row.TOP_SEMI_MANUFACTURED if row.TOP_SEMI_MANUFACTURED != 0 else None,
                    "BACK_SEMI_MANUFACTURED": row.BACK_SEMI_MANUFACTURED if row.BACK_SEMI_MANUFACTURED != 0 else None,
                    "PACKAGE_WIP_QTY": row.PACKAGE_WIP_QTY if row.PACKAGE_WIP_QTY != 0 else None,
                    "PACKAGE_TOP_WIP_QTY": row.PACKAGE_TOP_WIP_QTY if row.PACKAGE_TOP_WIP_QTY != 0 else None,
                    "PACKAGE_BACK_WIP_QTY": row.PACKAGE_BACK_WIP_QTY if row.PACKAGE_BACK_WIP_QTY != 0 else None,
                    "SG_QTY": row.SG_QTY if row.SG_QTY != 0 else None,
                    "SG_FINISHED_GOODS": row.SG_FINISHED_GOODS if row.SG_FINISHED_GOODS != 0 else None,
                    "SG_SEMI_MANUFACTURED": row.SG_SEMI_MANUFACTURED if row.SG_SEMI_MANUFACTURED != 0 else None,
                    "SECONDARY_OUTSOURCING_WIP_QTY": row.SECONDARY_OUTSOURCING_WIP_QTY if row.SECONDARY_OUTSOURCING_WIP_QTY != 0 else None,
                    "PURCHASE_WIP_QTY": row.PURCHASE_WIP_QTY if row.PURCHASE_WIP_QTY != 0 else None,
                    "CP_WIP_QTY": row.CP_WIP_QTY if row.CP_WIP_QTY != 0 else None,
                    "NO_TESTED_WAFER": row.NO_TESTED_WAFER if row.NO_TESTED_WAFER != 0 else None,
                    "TESTED_WAFER": row.TESTED_WAFER if row.TESTED_WAFER != 0 else None,
                    "DEPUTY_CHIP": row.DEPUTY_CHIP,
                    "OUTSOURCING_WIP_QTY": row.OUTSOURCING_WIP_QTY if row.OUTSOURCING_WIP_QTY != 0 else None,
                    "OUTSOURCING_WAFER": row.OUTSOURCING_WAFER if row.OUTSOURCING_WAFER != 0 else None
                }
                reports.append(GlobalReport(**report_data))
            
            return reports
        except Exception as e:
            logger.error(f"获取综合报表失败: {str(e)}")
            raise CustomException("获取综合报表失败")

    def export_global_report(self,db:Session)->bytes:
        """导出综合报表Excel"""
        try:
            reports = self.get_global_report(db)
            wb = Workbook()
            ws = wb.active
            ws.title = "外协报表"

            headers = [
                "行号",
                "主芯片",
                "芯片名称",
                "产成品数量",
                "产成品正印数量",
                "产成品背印数量",
                "半成品数量",
                "半成品正印数量",
                "半成品背印数量",
                "封装在制数量",
                "封装正印在制数量",
                "封装背印在制数量",
                "苏工院库存数量",
                "苏工院产成品数量",
                "苏工院半成品数量",
                "二次委外在制数量",
                "采购在制数量",
                "中测数量",
                "未测晶圆",
                "已测晶圆",
                "副芯片",
                "外购在途数量",
                "外购圆片数量"
            ]
            
            # 设置列宽
            column_widths = {
                'A': 15,
                'B': 25,
                'C': 20,
                'D': 10,
                'E': 10,
                'F': 10,
                'G': 10,
                'H': 10,
                'I': 10,
                'J': 10,
                'K': 10,
                'L': 10,
                'M': 10,
                'N': 10,
                'O': 10,
                'P': 10,
                'Q': 10,
                'R': 10,
                'S': 10,
                'T': 10,
                'U': 10,
                'V': 10,
                'W': 10
            }

            # 设置样式
            header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                ws.column_dimensions[get_column_letter(col)].width = column_widths[get_column_letter(col)]
            
            # 写入数据
            for row, report in enumerate(reports, 2):
                data = [
                    report.ROW,
                    report.MAIN_CHIP,
                    report.CHIP_NAME,
                    report.TOTAL_FINISHED_GOODS,
                    report.TOP_FINISHED_GOODS,
                    report.BACK_FINISHED_GOODS,
                    report.TOTAL_SEMI_MANUFACTURED,
                    report.TOP_SEMI_MANUFACTURED,
                    report.BACK_SEMI_MANUFACTURED,
                    report.PACKAGE_WIP_QTY,
                    report.PACKAGE_TOP_WIP_QTY,
                    report.PACKAGE_BACK_WIP_QTY,
                    report.SG_QTY,
                    report.SG_FINISHED_GOODS,
                    report.SG_SEMI_MANUFACTURED,
                    report.SECONDARY_OUTSOURCING_WIP_QTY,
                    report.PURCHASE_WIP_QTY,
                    report.CP_WIP_QTY,
                    report.NO_TESTED_WAFER,
                    report.TESTED_WAFER,
                    report.DEPUTY_CHIP,
                    report.OUTSOURCING_WIP_QTY,
                    report.OUTSOURCING_WAFER
                ]
                for col, value in enumerate(data, 1):
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = cell_alignment
                    cell.border = border

            # 冻结第一行
            ws.freeze_panes = 'A2'

            # 保存到内存
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            return excel_file.getvalue()
            
        except Exception as e:
            logger.error(f"导出外协报表Excel失败: {str(e)}")
            raise CustomException("导出外协报表Excel失败")

