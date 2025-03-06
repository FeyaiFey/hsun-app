from typing import List, Optional, Union, Dict, Any
from sqlmodel import Session, select, text
from app.schemas.purchase import (PurchaseOrder,PurchaseOrderQuery,PurchaseWip,PurchaseWipQuery)
from app.schemas.assy import (AssyOrder,AssyOrderQuery,AssyWip,AssyWipQuery,AssyOrderItemsQuery,AssyOrderPackageTypeQuery,AssyOrderSupplierQuery)
from app.schemas.stock import (StockQuery,Stock,WaferIdQtyDetailQuery,WaferIdQtyDetail)
from app.schemas.e10 import (FeatureGroupNameQuery,ItemCodeQuery,ItemNameQuery,WarehouseNameQuery,TestingProgramQuery,BurningProgramQuery,LotCodeQuery)
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
        """获取封装订单列表
        
        Args:
            db: 数据库会话
            params: 查询参数
            
        Returns:
            Dict[str,Any]: 包含封装订单列表和总数的字典
        """
        try:
            # 构建基础查询
            base_query = """
                SELECT 
                    PO.DOC_NO,
                    CAST(PO.PURCHASE_DATE AS DATE) AS PURCHASE_DATE,
                    PO.SUPPLIER_FULL_NAME,
                    PO.[CLOSE],
                    CAST(PO_D.BUSINESS_QTY AS INT) AS BUSINESS_QTY,
                    CAST(PO_D.RECEIPTED_PRICE_QTY AS INT) AS RECEIPTED_PRICE_QTY,
                    CASE 
                        WHEN PO.[CLOSE] = N'2' THEN 0
                        WHEN (PO_D.RECEIPTED_PRICE_QTY / PO_D.BUSINESS_QTY) > 0.992 THEN 0
                        ELSE CAST(((PO_D.BUSINESS_QTY * 0.996) - PO_D.RECEIPTED_PRICE_QTY) AS INT)
                    END AS WIP_QTY,
                    CAST(PO_D.PRICE AS FLOAT) AS PRICE,
                    ITEM.ITEM_CODE,
                    ITEM_LOT.LOT_CODE,
                    Z_ASSEMBLY_CODE.Z_ASSEMBLY_CODE,
                    Z_PROCESSING_PURPOSE.Z_PROCESSING_PURPOSE_NAME,
                    Z_PACKAGE.REMARK,
                    Z_LOADING_METHOD.Z_LOADING_METHOD_NAME,
                    Z_WIRE.Z_WIRE_NAME,
                    Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_NAME,
                    FEATURE_GROUP.FEATURE_GROUP_NAME
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
                WHERE ITEM.ITEM_CODE LIKE N'BC%AB'
            """
            
            # 构建查询条件
            conditions = []
            query_params = {}
            
            # 参数验证和清理
            if params.doc_no and isinstance(params.doc_no, str):
                conditions.append("AND PO.DOC_NO LIKE :doc_no")
                query_params["doc_no"] = f"%{self._clean_input(params.doc_no)}%"
                
            if params.item_code and isinstance(params.item_code, list):
                item_codes = [self._clean_input(code) for code in params.item_code]
                placeholders = [f":item_code_{i}" for i in range(len(item_codes))]
                conditions.append(f"AND ITEM.ITEM_CODE IN ({','.join(placeholders)})")
                for i, code in enumerate(item_codes):
                    query_params[f"item_code_{i}"] = code
            
            if params.supplier and isinstance(params.supplier, list):
                suppliers = [self._clean_input(supplier) for supplier in params.supplier]
                placeholders = [f":supplier_{i}" for i in range(len(suppliers))]
                conditions.append(f"AND PO.SUPPLIER_FULL_NAME IN ({','.join(placeholders)})")
                for i, supplier in enumerate(suppliers):
                    query_params[f"supplier_{i}"] = supplier
                
            if params.package_type and isinstance(params.package_type, list):
                package_types = [self._clean_input(package_type) for package_type in params.package_type]
                placeholders = [f":package_type_{i}" for i in range(len(package_types))]
                conditions.append(f"AND Z_PACKAGE_TYPE.Z_PACKAGE_TYPE_NAME IN ({','.join(placeholders)})")
                for i, package_type in enumerate(package_types):
                    query_params[f"package_type_{i}"] = package_type
                
            if params.is_closed is not None:
                if params.is_closed == 0:
                    conditions.append("AND PO.[CLOSE] = 0")
                else:
                    conditions.append("AND PO.[CLOSE] != 0")

            if params.order_date_start:
                conditions.append("AND PO.PURCHASE_DATE >= :order_date_start")
                query_params["order_date_start"] = params.order_date_start

            if params.order_date_end:
                conditions.append("AND PO.PURCHASE_DATE <= :order_date_end")
                query_params["order_date_end"] = params.order_date_end
                
            # 拼接查询条件
            query = base_query + " " + " ".join(conditions)
            
            # 添加排序
            query += " ORDER BY PO.PURCHASE_DATE,PO.DOC_NO"

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
                WHERE ITEM.ITEM_CODE LIKE N'BC%AB'
                {' '.join(conditions)}
            """
            total = db.execute(text(count_query).bindparams(**{k:v for k,v in query_params.items() if k not in ['offset', 'pageSize']})).scalar()
            
            # 转换为响应对象
            assy_orders = [
                AssyOrder(
                    DOC_NO=row.DOC_NO,
                    PURCHASE_DATE=row.PURCHASE_DATE,
                    SUPPLIER_FULL_NAME=row.SUPPLIER_FULL_NAME,
                    CLOSE=row.CLOSE,
                    BUSINESS_QTY=row.BUSINESS_QTY,
                    RECEIPTED_PRICE_QTY=row.RECEIPTED_PRICE_QTY,
                    WIP_QTY=row.WIP_QTY,
                    PRICE=row.PRICE,
                    ITEM_CODE=row.ITEM_CODE,
                    LOT_CODE=row.LOT_CODE,
                    Z_ASSEMBLY_CODE=row.Z_ASSEMBLY_CODE,
                    Z_PROCESSING_PURPOSE_NAME=row.Z_PROCESSING_PURPOSE_NAME,
                    Z_PACKAGE_TYPE_NAME=row.Z_PACKAGE_TYPE_NAME,
                    FEATURE_GROUP_NAME=row.FEATURE_GROUP_NAME
                ) for row in result
            ]
            return {
                "list": assy_orders,
                "total": total or 0
            }
        except Exception as e:
            logger.error(f"查询封装订单失败: {str(e)}")
            raise CustomException("查询封装订单失败")
        
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
                    SELECT TOP 100
                    FG.FEATURE_GROUP_NAME,
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
                placeholders = [f":item_name_{i}" for i in range(len(item_names))]
                having_conditions.append(f"AND ITEM.ITEM_NAME IN ({','.join(placeholders)})")
                for i, name in enumerate(item_names):
                    query_params[f"item_name_{i}"] = name

            if params.warehouse_name:
                warehouse_names = [self._clean_input(name) for name in params.warehouse_name]
                placeholders = [f":warehouse_name_{i}" for i in range(len(warehouse_names))]
                having_conditions.append(f"AND W.WAREHOUSE_NAME IN ({','.join(placeholders)})")
                for i, name in enumerate(warehouse_names):
                    query_params[f"warehouse_name_{i}"] = name

            if params.testing_program:
                testing_programs = [self._clean_input(name) for name in params.testing_program]
                placeholders = [f":testing_program_{i}" for i in range(len(testing_programs))]
                having_conditions.append(f"AND T.Z_TESTING_PROGRAM_NAME IN ({','.join(placeholders)})")
                for i, name in enumerate(testing_programs):
                    query_params[f"testing_program_{i}"] = name

            if params.burning_program:
                burning_programs = [self._clean_input(name) for name in params.burning_program]
                placeholders = [f":burning_program_{i}" for i in range(len(burning_programs))]
                having_conditions.append(f"AND BP.Z_BURNING_PROGRAM_NAME IN ({','.join(placeholders)})")
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
                    BIN_LEVEL_NAME=row.Z_BIN_LEVEL_NAME,
                    TESTING_PROGRAM=row.Z_TESTING_PROGRAM_NAME,
                    BURNING_PROGRAM=row.Z_BURNING_PROGRAM_NAME
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
                    ITEM_NAME=row.ITEM_NAME,
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
            

