from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AuthorBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150)
    bio: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    bio: Optional[str] = None

class AuthorResponse(BaseModel):
    id: int
    full_name: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AuthorDetailResponse(AuthorResponse):
    user_id: int
    followers_count: int = 0
    total_earnings: float = 0.0
    tracks_count: int = 0
    # при желании добавим средний рейтинг
    average_rating: float = 0.0