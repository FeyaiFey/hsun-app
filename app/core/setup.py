import os
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings

def setup_directories():
    """
    初始化应用所需目录
    """
    try:
        # 创建静态文件目录
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        logger.info(f"创建静态文件目录: {static_dir.absolute()}")
        
        # 创建文件上传目录
        file_storage_path = Path("static/files")
        file_storage_path.mkdir(exist_ok=True)
        logger.info(f"创建文件存储目录: {file_storage_path.absolute()}")
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.info(f"创建日志目录: {log_dir.absolute()}")
        
        # 创建临时目录
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        logger.info(f"创建临时目录: {temp_dir.absolute()}")
        
    except Exception as e:
        logger.error(f"初始化目录结构失败: {str(e)}")
        raise 