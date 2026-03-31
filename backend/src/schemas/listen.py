from pydantic import BaseModel
from datetime import datetime


class ListenResponse(BaseModel):
    status: str
    message: str
    total_plays: int
    counted: bool = True

    class Config:
        from_attributes = True