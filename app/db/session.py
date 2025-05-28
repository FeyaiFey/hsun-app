from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
from contextlib import contextmanager
from typing import Optional, Any, Generator
import time
import threading
import signal
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
        f"TrustServerCertificate=yes;"
        f"Connection Timeout={settings.DB_CONNECTION_TIMEOUT};"
        f"Command Timeout={settings.DB_COMMAND_TIMEOUT};"
    )
else:
    # 本地数据库
    conn_str = (
        f"DRIVER=ODBC Driver 18 for SQL Server;"
        f"SERVER=localhost;"
        f"DATABASE=E10;"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout={settings.DB_CONNECTION_TIMEOUT};"
        f"Command Timeout={settings.DB_COMMAND_TIMEOUT};"
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
    echo=settings.SQL_DEBUG,   # SQL调试模式
    connect_args={
        "timeout": settings.DB_CONNECTION_TIMEOUT,
        "autocommit": False
    }
)

# 存储活跃连接的字典
active_connections = {}
connection_lock = threading.Lock()

@event.listens_for(engine, "connect")
def set_connection_timeout(dbapi_connection, connection_record):
    """设置连接超时"""
    try:
        # 记录连接创建时间
        with connection_lock:
            active_connections[id(dbapi_connection)] = {
                'connection': dbapi_connection,
                'created_at': time.time(),
                'last_activity': time.time()
            }
        
        # 设置查询超时
        if hasattr(dbapi_connection, 'timeout'):
            dbapi_connection.timeout = settings.DB_QUERY_TIMEOUT
            
        logger.info(f"数据库连接已建立，连接ID: {id(dbapi_connection)}")
    except Exception as e:
        logger.error(f"设置连接超时失败: {str(e)}")

@event.listens_for(engine, "close")
def remove_connection_tracking(dbapi_connection, connection_record):
    """移除连接跟踪"""
    try:
        with connection_lock:
            conn_id = id(dbapi_connection)
            if conn_id in active_connections:
                del active_connections[conn_id]
        logger.info(f"数据库连接已关闭，连接ID: {id(dbapi_connection)}")
    except Exception as e:
        logger.error(f"移除连接跟踪失败: {str(e)}")

def cleanup_expired_connections():
    """清理过期连接"""
    if not settings.DB_AUTO_DISCONNECT:
        return
        
    current_time = time.time()
    expired_connections = []
    
    with connection_lock:
        # 创建一个副本来避免在迭代时修改字典
        connections_copy = dict(active_connections)
        
    # 检查过期连接
    for conn_id, conn_info in connections_copy.items():
        try:
            # 检查连接是否超过最大执行时间
            if current_time - conn_info['last_activity'] > settings.DB_MAX_EXECUTION_TIME:
                # 检查连接是否仍然有效
                connection = conn_info['connection']
                
                # 检查连接状态
                if hasattr(connection, 'closed') and connection.closed:
                    # 连接已经关闭，只需要从跟踪字典中移除
                    with connection_lock:
                        if conn_id in active_connections:
                            del active_connections[conn_id]
                    logger.info(f"移除已关闭的连接，连接ID: {conn_id}")
                    continue
                
                # 检查连接是否还活着
                try:
                    # 尝试执行一个简单的查询来检查连接状态
                    if hasattr(connection, 'execute'):
                        # 对于某些连接类型，可以尝试ping
                        pass
                    expired_connections.append((conn_id, conn_info))
                except Exception:
                    # 连接已经不可用，标记为过期
                    expired_connections.append((conn_id, conn_info))
                    
        except Exception as e:
            logger.error(f"检查连接状态失败，连接ID: {conn_id}, 错误: {str(e)}")
            # 如果检查失败，也将其标记为需要清理
            expired_connections.append((conn_id, conn_info))
    
    # 关闭过期连接
    for conn_id, conn_info in expired_connections:
        try:
            connection = conn_info['connection']
            
            # 再次检查连接是否已经关闭
            if hasattr(connection, 'closed') and connection.closed:
                logger.debug(f"连接已关闭，跳过关闭操作，连接ID: {conn_id}")
            else:
                # 尝试关闭连接
                connection.close()
                logger.warning(f"自动断开超时连接，连接ID: {conn_id}, 活跃时间: {current_time - conn_info['created_at']:.2f}秒")
            
            # 从跟踪字典中移除
            with connection_lock:
                if conn_id in active_connections:
                    del active_connections[conn_id]
                    
        except Exception as e:
            # 记录错误但不抛出异常，避免影响其他连接的清理
            logger.debug(f"关闭连接时出现预期错误（连接可能已关闭），连接ID: {conn_id}, 错误: {str(e)}")
            
            # 即使关闭失败，也要从跟踪字典中移除
            with connection_lock:
                if conn_id in active_connections:
                    del active_connections[conn_id]

class TimeoutSession(Session):
    """支持超时的数据库会话"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_time = time.time()
        self._timeout = settings.DB_QUERY_TIMEOUT

def get_db() -> Generator[TimeoutSession, None, None]:
    """FastAPI 依赖注入使用的数据库会话生成器"""
    # 清理过期连接
    cleanup_expired_connections()
    
    db = TimeoutSession(engine)
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[TimeoutSession, None, None]:
    """上下文管理器方式使用的数据库会话"""
    # 清理过期连接
    cleanup_expired_connections()
    
    db = TimeoutSession(engine)
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
