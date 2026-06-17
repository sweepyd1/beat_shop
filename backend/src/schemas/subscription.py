from pydantic import BaseModel
from datetime import datetime
from .author import AuthorResponse  

class SubscriptionResponse(BaseModel):
    id: int
    subscribed_at: datetime
    author: AuthorResponse  

    class Config:
        from_attributes = True