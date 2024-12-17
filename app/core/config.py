from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    SQL_DEBUG: bool = False
    
    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30天
    
    # 邮件配置
    IMAP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[str] = None
    EMAIL_ACCOUNT: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
