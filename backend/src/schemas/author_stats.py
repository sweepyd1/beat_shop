from pydantic import BaseModel
from typing import List, Optional

class LicenseSalesStats(BaseModel):
    license_type: str
    count: int
    total_amount: float

class TopTrackStats(BaseModel):
    track_id: int
    title: str
    cover_url: Optional[str]
    sales_count: int
    plays: int
    revenue: float

class MonthlyEarnings(BaseModel):
    month: str  
    amount: float

class AuthorFullStatsResponse(BaseModel):
    
    total_tracks: int
    total_plays: int
    total_favorites: int
    total_subscribers: int
    total_earnings: float

    
    sales_this_month: int
    monthly_earnings: float

    
    sales_chart_last_7_days: List[int]  
    plays_chart_last_7_days: List[int]  
    earnings_last_6_months: List[MonthlyEarnings]

    
    sales_by_license: List[LicenseSalesStats]

    
    top_tracks_by_sales: List[TopTrackStats]
    top_tracks_by_plays: List[TopTrackStats]

    
    average_rating: float