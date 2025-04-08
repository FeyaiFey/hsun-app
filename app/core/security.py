from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Optional, Union, Any, Dict
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_token(token: str) -> Dict[str, Any]:
    """
    验证JWT token
    
    Args:
        token: JWT token字符串
    
    Returns:
        dict: token中的信息
        
    Raises:
        CustomException: token无效时抛出
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if not payload:
            raise CustomException(
                code=status.HTTP_401_UNAUTHORIZED,
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )
        
        # 验证令牌版本
        if payload.get("version") != settings.TOKEN_VERSION:
            logger.warning("令牌版本不匹配")
            raise CustomException(
                code=status.HTTP_401_UNAUTHORIZED,
                message=get_error_message(ErrorCode.TOKEN_INVALID)
            )
            
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("令牌已过期")
        raise CustomException(
            code=status.HTTP_401_UNAUTHORIZED,
            message=get_error_message(ErrorCode.TOKEN_EXPIRED)
        )
    except jwt.JWTError as e:
        logger.error(f"令牌验证失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_401_UNAUTHORIZED,
            message=get_error_message(ErrorCode.TOKEN_INVALID)
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
        
    Raises:
        CustomException: 密码验证失败时抛出
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码验证失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_401_UNAUTHORIZED,
            message=get_error_message(ErrorCode.PASSWORD_ERROR),
            name="AuthenticationError"
        )

def get_password_hash(password: str) -> str:
    """获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 密码哈希
        
    Raises:
        CustomException: 密码哈希失败时抛出
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"密码哈希失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
        
    Raises:
        CustomException: 创建令牌失败时抛出
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({
            "exp": expire,
            "version": settings.TOKEN_VERSION  # 添加版本号
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建访问令牌失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR)
        )

def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建刷新令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
        
    Raises:
        CustomException: 创建令牌失败时抛出
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建刷新令牌失败: {str(e)}")
        raise CustomException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(ErrorCode.SYSTEM_ERROR),
            name="SystemError"
        )
