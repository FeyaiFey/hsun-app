from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class IResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(..., description="状态码")
    msg: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }
