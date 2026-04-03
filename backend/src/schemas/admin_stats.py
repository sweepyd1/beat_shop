from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class MetricsResponse(BaseModel):
    total_users: int
    new_users_last_week: int
    total_revenue: float
    revenue_growth: float  # в процентах
    total_purchases: int
    avg_check: float
    total_listens: int

class DailySalesResponse(BaseModel):
    date: date
    revenue: float

class DailyUsersResponse(BaseModel):
    date: date
    count: int

class TopTrackResponse(BaseModel):
    id: int
    title: str
    author_name: str
    genre_name: str
    sales_count: int
    revenue: float
    cover_url: Optional[str] = None

class GenreSalesResponse(BaseModel):
    genre_id: int
    genre_name: str
    revenue: float