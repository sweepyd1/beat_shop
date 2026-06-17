from pydantic import BaseModel
from datetime import datetime
from schemas.track import TrackResponse

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    added_at: datetime
    track: TrackResponse  

    class Config:
        from_attributes = True