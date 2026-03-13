from pydantic import BaseModel
from datetime import datetime
from .author import AuthorResponse  # предположим, что AuthorResponse определён в schemas/author.py

class SubscriptionResponse(BaseModel):
    id: int
    subscribed_at: datetime
    author: AuthorResponse  # должен включать id, name (full_name), photo_url, followers_count

    class Config:
        from_attributes = True