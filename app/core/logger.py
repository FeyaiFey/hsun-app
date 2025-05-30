import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings

def setup_simple_logger():
    """设置简单的日志系统"""
    # 创建日志目录
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger("hsun-app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 日志格式
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT
    )
    
    # 控制台处理器
    if settings.LOG_ENABLE_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if settings.LOG_ENABLE_FILE:
        # 应用日志
        file_handler = RotatingFileHandler(
        log_dir / "app.log",
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
        # 错误日志
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

# 创建全局日志记录器
logger = setup_simple_logger()

def log_request(method: str, path: str, duration: float, status_code: int, error: str = None):
    """记录请求日志"""
    status = "成功" if status_code < 400 else "失败"
    message = f"请求 {method} {path} - {status} - {duration:.3f}s - 状态码:{status_code}"
    
    if error:
        logger.error(f"{message} - 错误: {error}")
    elif status_code >= 400:
        logger.warning(message)
    else:
        logger.info(message)

def log_error(message: str, exc_info=None):
    """记录错误日志，包含详细堆栈"""
    if exc_info is None:
        exc_info = sys.exc_info()
    
    error_msg = message
    if exc_info and exc_info[0]:
        error_msg += f"\n异常类型: {exc_info[0].__name__}"
        error_msg += f"\n异常信息: {str(exc_info[1])}"
        error_msg += f"\n详细堆栈:\n{''.join(traceback.format_exception(*exc_info))}"
    
    logger.error(error_msg) 