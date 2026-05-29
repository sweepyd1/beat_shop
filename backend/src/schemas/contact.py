from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    message: str
    # user_id может быть передан из токена, но необязателен

class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: datetime
    is_read: bool
    user_id: Optional[int] = None

    class Config:
        from_attributes = True