from pydantic import BaseModel
from datetime import datetime
from .track import TrackResponse  # предположим, что TrackResponse определён в schemas/track.py

class PurchaseResponse(BaseModel):
    id: int
    purchase_date: datetime
    amount: float
    track: TrackResponse  # или можно создать упрощённую версию трека

    class Config:
        from_attributes = True