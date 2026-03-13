from pydantic import BaseModel
from datetime import datetime
from .track import TrackResponse

class FavoriteResponse(BaseModel):
    id: int
    added_at: datetime
    track: TrackResponse

    class Config:
        from_attributes = True