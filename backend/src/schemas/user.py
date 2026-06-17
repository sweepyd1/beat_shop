

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150, description="ФИО пользователя")
    login: str = Field(..., min_length=3, max_length=50, description="Логин")
    email: EmailStr = Field(..., description="Email")
    role:str = Field(..., min_length=1, max_length=150, description="Роль пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72, description="Пароль")
    
    @validator('password')
    def validate_password_length(cls, v):
        """Дополнительная проверка длины пароля для bcrypt"""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Пароль слишком длинный. Максимальная длина 72 символа в UTF-8')
        return v


class UserLogin(BaseModel):
    login: str = Field(..., description="Логин или email")
    password: str = Field(..., description="Пароль")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    
    @validator('password')
    def validate_password_length(cls, v):
        if v and len(v.encode('utf-8')) > 72:
            raise ValueError('Пароль слишком длинный. Максимальная длина 72 символа в UTF-8')
        return v


class UserResponse(UserBase):
    id: int
    registered_at: datetime
    is_active: bool
    role:str
    avatar_url: Optional[str] = None 

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    favorites_count: int = 0
    purchases_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  
    exp: int  
    type: str = "access"  