from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class MetricsResponse(BaseModel):
    total_users: int
    new_users_last_week: int
    total_revenue: float
    revenue_growth: float  
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

class UserMetricsResponse(BaseModel):
    total_users: int
    new_users_last_week: int
    active_users_last_month: int          
    total_subscriptions: int              
    avg_purchases_per_user: float
    total_purchases_amount: Decimal

class DailyUserRegistrationsResponse(BaseModel):
    date: date
    count: int

class DailyUserPurchasesResponse(BaseModel):
    date: date
    purchase_count: int
    total_amount: Decimal

class TopBuyerResponse(BaseModel):
    user_id: int
    full_name: str
    login: str
    total_spent: Decimal
    purchases_count: int

class TopListenerResponse(BaseModel):
    user_id: int
    full_name: str
    login: str
    listen_count: int

class UserRoleDistributionResponse(BaseModel):
    role: str
    count: int