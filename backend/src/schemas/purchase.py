
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from schemas.track import TrackResponse  

class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    purchase_date: datetime
    amount: float
    status: str
    track: Optional[TrackResponse] = None

    class Config:
        from_attributes = True
        
class LicenseTypeEnum(str, Enum):
    standard = "standard"
    extended = "extended"
    exclusive = "exclusive"
class PurchaseRequest(BaseModel):
    track_id: int                     
    buyer_name: str
    buyer_email: EmailStr
    license_type: LicenseTypeEnum
    comment: str | None = None       