import os
import sys

# 获取项目根目录路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from sqlalchemy import text

from app.db.session import get_db_context
from app.core.logger import logger



def test_database_connection():
    """测试数据库连接"""
    try:
        with get_db_context() as db:
            result = db.exec(text("SELECT 1"))
            assert result.scalar() == 1
            print("数据库连接成功!")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise
        
def test_get_all_tables():
    """获取所有表名"""
    try:
        with get_db_context() as db:
            # 查询所有用户表
            query = text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            result = db.exec(query)
            tables = result.fetchall()
            
            print("\n数据库中的所有表:")
            for table in tables:
                print(f"- {table[0]}")
            
            return tables
    except Exception as e:
        logger.error(f"获取表信息失败: {str(e)}")
        raise
        
def test_get_table_structure():
    """获取所有表的结构"""
    try:
        with get_db_context() as db:
            # 获取所有表名
            tables_query = text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = db.exec(tables_query).fetchall()
            
            print("\n表结构详情:")
            for table in tables:
                table_name = table[0]
                print(f"\n表名: {table_name}")
                print("-" * 50)
                
                # 获取表结构
                columns_query = text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = :table_name
                """).bindparams(table_name=table_name)
                
                columns = db.exec(columns_query).fetchall()
                
                print("列名\t\t数据类型\t长度\t允许空\t默认值")
                print("-" * 50)
                for col in columns:
                    print(f"{col[0]}\t\t{col[1]}\t\t{col[2]}\t{col[3]}\t{col[4]}")
                    
    except Exception as e:
        logger.error(f"获取表结构失败: {str(e)}")
        raise

if __name__ == '__main__':
    # 运行所有测试函数
    test_database_connection()
    test_get_all_tables()
    test_get_table_structure()