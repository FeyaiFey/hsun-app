from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.responses import Response
from fastapi import status
from datetime import datetime

# 定义成功响应的状态码
SUCCESS_CODE = 200

# 定义泛型类型
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """统一的响应模型"""
    code: int = SUCCESS_CODE
    data: Optional[T] = None
    message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponseModel(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    name: str
    response: Optional[dict] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CustomResponse:
    """自定义响应处理类"""
    @staticmethod
    def success(*, data: Any = None, message: str = "Success") -> JSONResponse:
        response_model = ResponseModel(
            code=SUCCESS_CODE,
            data=data,
            message=message
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_model.model_dump(mode='json')
        )

    @staticmethod
    def error(*, 
              code: int = status.HTTP_400_BAD_REQUEST,
              message: str = "Error",
              name: str = "BadRequest",
              response_data: dict = None) -> JSONResponse:
        error_model = ErrorResponseModel(
            code=code,
            message=message,
            name=name,
            response=response_data
        )
        return JSONResponse(
            status_code=code,
            content=error_model.model_dump(mode='json')
        )

    @staticmethod
    def file_response(file_data: bytes, filename: str) -> Response:
        """文件响应处理"""
        return Response(
            content=file_data,
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        ) 