-- 创建文件夹表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'huaxinAdmin_folders')
BEGIN
    CREATE TABLE huaxinAdmin_folders (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        parent_id INT NULL,
        user_id INT NULL,
        is_public BIT NOT NULL DEFAULT 0,
        is_deleted BIT NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT SYSDATETIME(),
        updated_at DATETIME NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_folders_parent FOREIGN KEY (parent_id) REFERENCES huaxinAdmin_folders(id) ON DELETE NO ACTION
    );
    
    PRINT '文件夹表 huaxinAdmin_folders 创建成功';
END
ELSE
BEGIN
    PRINT '文件夹表 huaxinAdmin_folders 已存在，跳过创建';
END

-- 创建文件表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'huaxinAdmin_files')
BEGIN
    CREATE TABLE huaxinAdmin_files (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        original_name NVARCHAR(255) NOT NULL,
        extension NVARCHAR(50) NULL,
        mime_type NVARCHAR(100) NULL,
        size BIGINT NOT NULL,
        path NVARCHAR(500) NOT NULL,
        folder_id INT NULL,
        user_id INT NULL,
        is_folder BIT NOT NULL DEFAULT 0,
        is_public BIT NOT NULL DEFAULT 0,
        is_deleted BIT NOT NULL DEFAULT 0,
        tags NVARCHAR(255) NULL,
        created_at DATETIME NOT NULL DEFAULT SYSDATETIME(),
        updated_at DATETIME NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_files_folder FOREIGN KEY (folder_id) REFERENCES huaxinAdmin_folders(id) ON DELETE SET NULL
    );
    
    PRINT '文件表 huaxinAdmin_files 创建成功';
END
ELSE
BEGIN
    PRINT '文件表 huaxinAdmin_files 已存在，跳过创建';
END

-- 创建索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_files_folder_id' AND object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE INDEX IX_files_folder_id ON huaxinAdmin_files(folder_id);
    PRINT '文件表索引 IX_files_folder_id 创建成功';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_files_user_id' AND object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE INDEX IX_files_user_id ON huaxinAdmin_files(user_id);
    PRINT '文件表索引 IX_files_user_id 创建成功';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_files_extension' AND object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE INDEX IX_files_extension ON huaxinAdmin_files(extension);
    PRINT '文件表索引 IX_files_extension 创建成功';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_files_is_deleted' AND object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE INDEX IX_files_is_deleted ON huaxinAdmin_files(is_deleted);
    PRINT '文件表索引 IX_files_is_deleted 创建成功';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_folders_parent_id' AND object_id = OBJECT_ID('huaxinAdmin_folders'))
BEGIN
    CREATE INDEX IX_folders_parent_id ON huaxinAdmin_folders(parent_id);
    PRINT '文件夹表索引 IX_folders_parent_id 创建成功';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_folders_user_id' AND object_id = OBJECT_ID('huaxinAdmin_folders'))
BEGIN
    CREATE INDEX IX_folders_user_id ON huaxinAdmin_folders(user_id);
    PRINT '文件夹表索引 IX_folders_user_id 创建成功';
END

-- 为全文索引创建唯一键索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UX_files_id' AND object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE UNIQUE INDEX UX_files_id ON huaxinAdmin_files(id);
    PRINT '全文搜索唯一索引 UX_files_id 创建成功';
END;

-- 分隔开全文索引部分，避免语法错误
-- 创建全文目录
IF NOT EXISTS (SELECT * FROM sys.fulltext_catalogs WHERE name = 'FileCatalog')
BEGIN
    CREATE FULLTEXT CATALOG FileCatalog;
    PRINT '全文索引目录 FileCatalog 创建成功';
END;

-- 创建全文索引（如果需要为文件名和标签提供更好的搜索功能）
IF NOT EXISTS (SELECT * FROM sys.fulltext_indexes WHERE object_id = OBJECT_ID('huaxinAdmin_files'))
BEGIN
    CREATE FULLTEXT INDEX ON huaxinAdmin_files(
        name LANGUAGE 2052,
        original_name LANGUAGE 2052,
        tags LANGUAGE 2052
    )
    KEY INDEX UX_files_id ON FileCatalog
    WITH CHANGE_TRACKING AUTO;
    
    PRINT '文件表全文索引创建成功';
END
ELSE
BEGIN
    PRINT '文件表全文索引已存在，跳过创建';
END;

-- 创建初始根文件夹（如果需要）
IF NOT EXISTS (SELECT * FROM huaxinAdmin_folders WHERE parent_id IS NULL AND name = '根目录')
BEGIN
    INSERT INTO huaxinAdmin_folders (name, parent_id, is_public, user_id)
    VALUES ('根目录', NULL, 1, NULL);
    
    PRINT '创建根文件夹成功';
END
ELSE
BEGIN
    PRINT '根文件夹已存在，跳过创建';
END 