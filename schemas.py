# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    disabled: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class PodCreate(BaseModel):
    duration_minutes: int


class PodOut(BaseModel):
    id: int
    container_id: str
    user_id: int
    created_at: datetime
    expires_at: datetime
    status: str

    class Config:
        orm_mode = True
