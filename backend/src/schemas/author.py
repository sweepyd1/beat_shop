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

class AuthorResponse(AuthorBase):
    id: int
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuthorDetailResponse(AuthorResponse):
    tracks_count: int = 0