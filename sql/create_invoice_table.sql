-- 创建发票主表
CREATE TABLE huaxinAdmin_Invoices (
    InvoiceID BIGINT IDENTITY(1,1) PRIMARY KEY,
    FileName NVARCHAR(255) NOT NULL,
    InvoiceType NVARCHAR(100),
    InvoiceNumber NVARCHAR(50) UNIQUE NOT NULL,
    IssueDate DATE,
    Issuer NVARCHAR(100),
    
    -- 购买方信息
    BuyerName NVARCHAR(255),
    BuyerTaxNumber NVARCHAR(50),
    
    -- 销售方信息
    SellerName NVARCHAR(255),
    SellerTaxNumber NVARCHAR(50),
    
    -- 金额信息
    TotalAmount DECIMAL(18,2),
    TotalTax DECIMAL(18,2),
    TotalAmountInWords NVARCHAR(255),
    TotalAmountInNumbers DECIMAL(18,2),
    
    -- 状态字段：0-作废，1-正常
    Status INT NOT NULL DEFAULT 1,
    
    -- 系统字段
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE()
);

-- 创建基本索引
CREATE INDEX IX_Invoices_InvoiceNumber ON huaxinAdmin_Invoices(InvoiceNumber);
CREATE INDEX IX_Invoices_IssueDate ON huaxinAdmin_Invoices(IssueDate);
CREATE INDEX IX_Invoices_BuyerName ON huaxinAdmin_Invoices(BuyerName);
CREATE INDEX IX_Invoices_SellerName ON huaxinAdmin_Invoices(SellerName);
CREATE INDEX IX_Invoices_Status ON huaxinAdmin_Invoices(Status);
GO

-- 创建更新时间触发器
CREATE TRIGGER TR_Invoices_UpdatedAt
ON huaxinAdmin_Invoices
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE huaxinAdmin_Invoices 
    SET UpdatedAt = GETDATE()
    WHERE InvoiceID IN (SELECT InvoiceID FROM inserted);
END;
GO

PRINT '数据库创建完成！';
PRINT '包含内容：';
PRINT '- 主表：huaxinAdmin_Invoices（发票主表）';
PRINT '- 基本索引：发票号码、开票日期、购买方、销售方、状态';
PRINT '- 状态字段：0-作废，1-正常（默认）';
PRINT '- 自动更新时间戳功能';
PRINT '- 简洁设计，专注核心发票信息管理';