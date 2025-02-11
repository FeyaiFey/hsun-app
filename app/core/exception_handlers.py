from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError

from app.core.exceptions import CustomException
from app.core.response import CustomResponse
from app.core.error_codes import ErrorCode, get_error_message

async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    """处理自定义异常"""
    return CustomResponse.error(
        code=exc.code,
        message=exc.message,
        name=exc.__class__.__name__
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求参数验证异常"""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = error.get("loc", [])[-1]  # 获取字段名
        error_type = error.get("type", "")
        
        # 用户名验证错误处理
        if field == "username":
            if "string_too_long" in error_type:
                max_length = error.get("ctx", {}).get("limit_value", 50)
                error_messages.append(f"用户名长度不能超过{max_length}个字符")
            elif "value_error.missing" in error_type:
                error_messages.append("用户名不能为空")
            else:
                error_messages.append("用户名格式不正确")
                
        # 邮箱验证错误处理
        elif field == "email":
            if "value_error.missing" in error_type:
                error_messages.append("邮箱不能为空")
            elif "value_error.email" in error_type:
                error_messages.append("邮箱格式不正确")
            else:
                error_messages.append("邮箱格式有误")
                
        # 密码验证错误处理
        elif field == "password":
            if "value_error.missing" in error_type:
                error_messages.append("密码不能为空")
            elif "string_too_short" in error_type:
                min_length = error.get("ctx", {}).get("limit_value", 6)
                error_messages.append(f"密码长度不能少于{min_length}个字符")
            elif "string_too_long" in error_type:
                max_length = error.get("ctx", {}).get("limit_value", 20)
                error_messages.append(f"密码长度不能超过{max_length}个字符")
            else:
                error_messages.append("密码格式不正确")
                
        # 部门ID验证错误处理
        elif field == "department_id":
            if "type_error.integer" in error_type:
                error_messages.append("部门ID必须是整数")
            else:
                error_messages.append("部门ID格式不正确")
                
        # 状态验证错误处理
        elif field == "status":
            if "type_error.integer" in error_type:
                error_messages.append("状态值必须是整数")
            else:
                error_messages.append("状态值格式不正确")
        
        # 其他字段的验证错误
        else:
            error_messages.append(get_error_message(ErrorCode.PARAM_ERROR))
    
    # 如果没有具体错误消息，使用默认错误消息
    if not error_messages:
        error_messages.append(get_error_message(ErrorCode.PARAM_ERROR))
    
    return CustomResponse.error(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=" | ".join(error_messages),
        name="ValidationError",
        response_data={"detail": exc.errors()}
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """处理数据库异常"""
    return CustomResponse.error(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=get_error_message(ErrorCode.DB_ERROR),
        name="DatabaseError"
    )

async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
    """处理JWT相关异常"""
    return CustomResponse.error(
        code=status.HTTP_401_UNAUTHORIZED,
        message=get_error_message(ErrorCode.TOKEN_INVALID),
        name="AuthenticationError"
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理其他未捕获的异常"""
    return CustomResponse.error(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=get_error_message(ErrorCode.SYSTEM_ERROR),
        name="InternalServerError"
    ) 