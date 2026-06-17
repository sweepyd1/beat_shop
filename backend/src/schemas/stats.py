from pydantic import BaseModel
from typing import List

class StatsResponse(BaseModel):
    sales_this_month: int = 0
    monthly_earnings: float = 0.0
    average_rating: float = 0.0
    sales_chart: List[int] = []   
    followers_count: int = 0