from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class GenreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    image_url: Optional[str] = None   

class GenreCreate(GenreBase):
    pass

class GenreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    image_url: Optional[str] = None   

class GenreResponse(GenreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)