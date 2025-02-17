import uuid
from datetime import datetime, date
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    """品号信息"""
    __tablename__ = "ITEM"

    ITEM_BUSINESS_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    ITEM_CODE: str = Field(default=None, nullable=False, description="品号", readonly=True)
    ITEM_NAME: str = Field(default=None, nullable=True, description="品名", readonly=True)
    ITEM_DESC: str = Field(default=None, nullable=True, description="品号描述", readonly=True)
    SHORTCUT: str = Field(default=None, nullable=True, description="快捷码", readonly=True)
    FEATURE_GROUP_ID: uuid.UUID = Field(default=None, nullable=True, description="品号群组ID", readonly=True)
    Z_WAFER_MODEL: str = Field(default=None, nullable=True, description="晶圆型号", readonly=True)
    Z_GROSS_DIE: str = Field(default=None, nullable=True, description="晶圆Gross Die", readonly=True)
    Z_MATERIALS_STATUS: str = Field(default=None, nullable=True, description="料件状态", readonly=True)
    
    
class FEATURE_GROUP(SQLModel, table=True):
    """品号群组"""
    __tablename__ = "FEATURE_GROUP"

    FEATURE_GROUP_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    FEATURE_GROUP_CODE: str = Field(default=None, nullable=True, description="品号群组代码", readonly=True)
    FEATURE_GROUP_NAME: str = Field(default=None, nullable=True, description="品号群组名称", readonly=True)


class WAREHOUSE(SQLModel, table=True):
    """仓库"""
    __tablename__ = "WAREHOUSE"

    WAREHOUSE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    WAREHOUSE_CODE: str = Field(default=None, nullable=True, description="仓库代码", readonly=True)
    WAREHOUSE_NAME: str = Field(default=None, nullable=True, description="仓库名称", readonly=True)

class ITEM_LOT(SQLModel, table=True):
    """品号批次"""
    __tablename__ = "ITEM_LOT"

    ITEM_LOT_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    ITEM_LOT_CODE: str = Field(default=None, nullable=True, description="品号批次代码", readonly=True)

class Z_BIN_LEVEL(SQLModel, table=True):
    """BIN等级"""
    __tablename__ = "Z_BIN_LEVEL"

    Z_BIN_LEVEL_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_BIN_LEVEL_CODE: str = Field(default=None, nullable=True, description="BIN等级代码", readonly=True)
    Z_BIN_LEVEL_NAME: str = Field(default=None, nullable=True, description="BIN等级名称", readonly=True)

class Z_TESTING_PROGRAM(SQLModel, table=True):
    """测试程序"""
    __tablename__ = "Z_TESTING_PROGRAM"

    Z_TESTING_PROGRAM_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_TESTING_PROGRAM_CODE: str = Field(default=None, nullable=True, description="测试程序代码", readonly=True)
    Z_TESTING_PROGRAM_NAME: str = Field(default=None, nullable=True, description="测试程序名称", readonly=True)
    REMARK: str = Field(default=None, nullable=True, description="备注", readonly=True)

class Z_BURNING_PROGRAM(SQLModel, table=True):
    """烧录程序"""
    __tablename__ = "Z_BURNING_PROGRAM"

    Z_BURNING_PROGRAM_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_BURNING_PROGRAM_CODE: str = Field(default=None, nullable=True, description="烧录程序代码", readonly=True)
    Z_BURNING_PROGRAM_NAME: str = Field(default=None, nullable=True, description="烧录程序名称", readonly=True)
    REMARK: str = Field(default=None, nullable=True, description="备注", readonly=True)
    CUSTOM_FIELD01: str = Field(default=None, nullable=True, description="FTP", readonly=True)

class Z_PROCESSING_PURPOSE(SQLModel, table=True):
    """加工方式"""
    __tablename__ = "Z_PROCESSING_PURPOSE"

    Z_PROCESSING_PURPOSE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_PROCESSING_PURPOSE_CODE: str = Field(default=None, nullable=True, description="加工方式代码", readonly=True)
    Z_PROCESSING_PURPOSE_NAME: str = Field(default=None, nullable=True, description="加工方式名称", readonly=True)

class Z_ASSEMBLY_CODE(SQLModel, table=True):
    """组合代码"""
    __tablename__ = "Z_ASSEMBLY_CODE"

    Z_ASSEMBLY_CODE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_ASSEMBLY_CODE: str = Field(default=None, nullable=True, description="组合代码", readonly=True)  # 打线图/测试程序代码
    Z_PROCESSING_PURPOSE_ID: uuid.UUID = Field(default=None, nullable=True, description="加工方式ID", readonly=True)
    CUSTOM_FIELD10: str = Field(default=None, nullable=True, description="测试流程", readonly=True)

class Z_PACKAGE(SQLModel, table=True):
    """封装"""
    __tablename__ = "Z_PACKAGE"

    Z_PACKAGE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_PACKAGE_CODE: str = Field(default=None, nullable=True, description="封装代码", readonly=True)
    Z_PACKAGE_NAME: str = Field(default=None, nullable=True, description="封装名称", readonly=True)

class Z_PACKAGE_TYPE(SQLModel, table=True):
    """封装形式"""
    __tablename__ = "Z_PACKAGE_TYPE"

    Z_PACKAGE_TYPE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_PACKAGE_TYPE_NAME: str = Field(default=None, nullable=True, description="封装类型名称", readonly=True)

class Z_WIRE(SQLModel, table=True):
    """线材"""
    __tablename__ = "Z_WIRE"

    Z_WIRE_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_WIRE_NAME: str = Field(default=None, nullable=True, description="线材名称", readonly=True)

class Z_LOADING_METHOD(SQLModel, table=True):
    """装片方式"""
    __tablename__ = "Z_LOADING_METHOD"

    Z_LOADING_METHOD_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_LOADING_METHOD_NAME: str = Field(default=None, nullable=True, description="装片方式名称", readonly=True)
    
# 采购订单列表
class PURCHASE_ORDER(SQLModel, table=True):
    """采购订单"""
    __tablename__ = "PURCHASE_ORDER"

    PURCHASE_ORDER_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    DOC_NO: str = Field(default=None, nullable=True, description="单据号", readonly=True)
    DOC_DATE: date = Field(default=None, nullable=True, description="单据日期", readonly=True)
    SUPPLIER_FULL_NAME: str = Field(default=None, nullable=True, description="供应商全称", readonly=True)
    CLOSE: int = Field(default=None, nullable=True, description="关闭", readonly=True) # 0未结束, 2已结束
    
class PURCHASE_ORDER_D(SQLModel, table=True):
    """采购订单明细"""
    __tablename__ = "PURCHASE_ORDER_D"

    PURCHASE_ORDER_D_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    PURCHASE_ORDER_ID: uuid.UUID = Field(default=None, nullable=True, description="采购订单ID", readonly=True)
    ITEM_ID: str = Field(default=None, nullable=True, description="品号", readonly=True)
    PRICE: float = Field(default=None, nullable=True, description="单价", readonly=True)
    Z_TESTING_ASSEMBLY_CODE_ID: uuid.UUID = Field(default=None, nullable=True, description="测试程序ID", readonly=True)
    Z_PACKAGE_ASSEMBLY_CODE_ID: uuid.UUID = Field(default=None, nullable=True, description="封装组合代码ID", readonly=True)

class PURCHASE_ORDER_SD(SQLModel, table=True):
    """采购订单收获信息"""
    __tablename__ = "PURCHASE_ORDER_SD"

    PURCHASE_ORDER_SD_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    PURCHASE_ORDER_D_ID: uuid.UUID = Field(default=None, nullable=True, description="采购订单明细ID", readonly=True)
    BUSINESS_QTY: float = Field(default=None, nullable=True, description="业务数量", readonly=True)
    RECEIPTED_BUSINESS_QTY: float = Field(default=None, nullable=True, description="收货数量", readonly=True)
    RECEIPT_CLOSE: int = Field(default=None, nullable=True, description="收货关闭", readonly=True) # 0未结束, 2已结束

class PURCHASE_ORDER_SSD(SQLModel, table=True):
    """采购订单SD明细"""
    __tablename__ = "PURCHASE_ORDER_SSD"

    PURCHASE_ORDER_SSD_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    PURCHASE_ORDER_SD_ID: uuid.UUID = Field(default=None, nullable=True, description="采购订单SDID", readonly=True)
    LastModifiedDate: datetime = Field(default=None, nullable=True, description="最后收货日期", readonly=True)
    SOURCE_ID_ROid: str = Field(default=None, nullable=True, description="来源单号", readonly=True)
    REFERENCE_SOURCE_ID_ROid: str = Field(default=None, nullable=True, description="来源单号", readonly=True)

# 委外工单列表
class MO(SQLModel, table=True):
    """委外工单"""
    __tablename__ = "MO"

    MO_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    STATUS: int = Field(default=None, nullable=True, description="状态", readonly=True) # 0未开始, 1进行中, 2已完成, 3已关闭
    ACTUAL_COMPLETE_DATE: date = Field(default=None, nullable=True, description="实际完成日期", readonly=True)

class Z_OUT_MO_D(SQLModel, table=True):
    """委外工单明细"""
    __tablename__ = "Z_OUT_MO_D"

    Z_OUT_MO_D_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    ITEM_LOT_ID: uuid.UUID = Field(default=None, nullable=True, description="品号批次ID", readonly=True)
    REMARK: str = Field(default=None, nullable=True, description="备注", readonly=True)

class Z_OUT_MO_SD(SQLModel, table=True):
    """委外工单SD"""
    __tablename__ = "Z_OUT_MO_SD"

    Z_OUT_MO_SD_ID: uuid.UUID = Field(default=None, primary_key=True, nullable=False, description="ID", readonly=True)
    Z_OUT_MO_D_ID: uuid.UUID = Field(default=None, nullable=True, description="委外工单明细ID", readonly=True)
    ITEM_ID: str = Field(default=None, nullable=True, description="品号ID", readonly=True)
    ITEM_LOT_ID: uuid.UUID = Field(default=None, nullable=True, description="品号批次ID", readonly=True)
    BUSINESS_QTY: float = Field(default=None, nullable=True, description="业务数量", readonly=True)
    SECOND_QTY: float = Field(default=None, nullable=True, description="第二数量", readonly=True)
    Z_WF_ID_STRING: str = Field(default=None, nullable=True, description="WF ID", readonly=True)
    Z_MAIN_CHIP: str = Field(default=None, nullable=True, description="主芯片ID", readonly=True)

# 视图
# 所有采购订单



    
    
    
    
    



    

    
