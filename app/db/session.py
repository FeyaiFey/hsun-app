from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Optional, Any, Generator
from app.core.config import settings
from app.core.logger import logger


auth_type = settings.DB_AUTH_TYPE

if auth_type == "sql":
    conn_str = (
        f"DRIVER={{{settings.DB_DRIVER}}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_DATABASE};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
        f"TrustServerCertificate=yes"
    )
else:
    # 本地数据库
    conn_str = (
        f"DRIVER=ODBC Driver 17 for SQL Server;"
        f"SERVER=localhost;"
        f"DATABASE=E10;"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes"
    )
# 配置数据库连接池
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={conn_str}",
    poolclass=QueuePool,
    pool_size=settings.POOL_SIZE,              # 连接池大小
    max_overflow=settings.MAX_OVERFLOW,          # 超过 pool_size 后最多可以创建的连接数
    pool_timeout=settings.POOL_TIMEOUT,          # 获取连接的超时时间
    pool_recycle=settings.POOL_RECYCLE,        # 连接重置时间(30分钟)
    pool_pre_ping=settings.POOL_PRE_PING,       # 连接前检查
    echo=settings.SQL_DEBUG   # SQL调试模式
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入使用的数据库会话生成器"""
    db = Session(engine)
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """上下文管理器方式使用的数据库会话"""
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
