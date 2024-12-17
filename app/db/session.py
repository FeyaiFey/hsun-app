from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from app.core.config import settings
from app.core.logger import logger

# 配置数据库连接池
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,              # 连接池大小
    max_overflow=10,          # 超过 pool_size 后最多可以创建的连接数
    pool_timeout=30,          # 获取连接的超时时间
    pool_recycle=1800,        # 连接重置时间(30分钟)
    pool_pre_ping=True,       # 连接前检查
    echo=settings.SQL_DEBUG   # SQL调试模式
)

def get_db():
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
def get_db_context():
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
