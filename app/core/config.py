from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import secrets
from pathlib import Path

class Settings(BaseSettings):
    # 基础配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HsunAdmin"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "基于FastAPI的后台管理系统"
    DEBUG: bool = True

    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1  # 1 小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1  # 1 天
    ALGORITHM: str = "HS256"

    # 数据库配置
    DB_AUTH_TYPE: str = "sql"
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_SERVER: str = "localhost"
    DB_DATABASE: str = "hsun_admin"
    DB_USER: str = "sa"
    DB_PASSWORD: str = "123456"
    SQL_DEBUG: bool = False

    # 数据库连接池配置
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    POOL_PRE_PING: bool = True

    # 跨域配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # 文件上传配置
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # 缓存配置
    CACHE_EXPIRE: int = 60 * 60  # 1小时

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/app.log")

    # 邮件配置
    IMAP_SERVER: str = "s220s.chinaemail.cn"
    SMTP_PORT: int = 465
    EMAIL_ACCOUNT: str = "wxb1@h-sun.com"
    EMAIL_PASSWORD: str = "496795ef2tsWaJol"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8',
        extra='allow'  # 允许额外的字段
    )

# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 确保日志目录存在
settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
