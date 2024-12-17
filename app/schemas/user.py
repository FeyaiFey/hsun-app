from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    nickname: str
    department: str
    avatar_url: str
    token: str

class Department(BaseModel):
    id: int
    name: str

class DepartmentResponse(BaseModel):
    departments: List[Department]

