import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from app.core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """配置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 按大小轮转的文件处理器
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 按时间轮转的文件处理器
    time_handler = TimedRotatingFileHandler(
        log_dir / "app.daily.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    time_handler.setFormatter(formatter)
    logger.addHandler(time_handler)
    
    # 错误日志单独记录
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

# 创建全局日志记录器
logger = setup_logger("hsun-backend") 