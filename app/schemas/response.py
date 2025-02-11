from typing import Any, Generic, TypeVar, Optional, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")

class AxiosHeaders(BaseModel):
    """Axios 响应头模型"""
    content_type: str = Field(default="application/json", alias="Content-Type")

class AxiosResponseModel(BaseModel, Generic[T]):
    """Axios 响应模型"""
    data: Optional[T] = Field(None, description="响应数据")
    status: int = Field(..., description="HTTP状态码")
    statusText: str = Field(..., description="HTTP状态描述")
    headers: AxiosHeaders = Field(default_factory=AxiosHeaders)
    config: Dict[str, Any] = Field(default_factory=dict)

class IResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(..., description="状态码")
    data: T = Field(None, description="响应数据")

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "data": None
            }
        }
