from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class IResponse(BaseModel, Generic[T]):
    code: int
    data: T

    class Config:
        arbitrary_types_allowed = True
