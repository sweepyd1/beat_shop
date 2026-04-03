from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from database.models import Genre, Purchase, Track
from .base import BaseRepository

class PurchaseRepository(BaseRepository[Purchase]):
    def __init__(self, session):
        super().__init__(Purchase, session)

    async def get_user_purchases(self, user_id: int) -> List[Purchase]:
        result = await self.session.execute(
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .options(
                selectinload(Purchase.track).selectinload(Track.author),
                selectinload(Purchase.track).selectinload(Track.genre)   # Add this line
            )
            .order_by(Purchase.purchase_date.desc())
        )
        return result.scalars().all()
    async def get_author_total_earnings(self, author_id: int) -> float:
        result = await self.session.execute(
            select(func.sum(Purchase.amount))
            .join(Track, Track.id == Purchase.track_id)
            .where(Track.author_id == author_id)
        )
        return result.scalar_one() or 0.0

    async def get_author_monthly_stats(self, author_id: int):
        now = datetime.now()
        first_day = datetime(now.year, now.month, 1)
        result = await self.session.execute(
            select(
                func.count(Purchase.id).label('sales_count'),
                func.sum(Purchase.amount).label('total_amount')
            )
            .join(Track, Track.id == Purchase.track_id)
            .where(Track.author_id == author_id, Purchase.purchase_date >= first_day)
        )
        row = result.one()
        return row.sales_count or 0, row.total_amount or 0.0

    async def get_last_7_days_sales(self, author_id: int) -> List[int]:
        from datetime import timedelta
        now = datetime.now()
        days = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0)
            day_end = (now - timedelta(days=i-1)).replace(hour=0, minute=0, second=0) if i > 0 else now
            result = await self.session.execute(
                select(func.sum(Purchase.amount))
                .join(Track, Track.id == Purchase.track_id)
                .where(Track.author_id == author_id, Purchase.purchase_date >= day_start, Purchase.purchase_date < day_end)
            )
            days.append(int(result.scalar_one() or 0))
        return days
    async def total_revenue(self) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Purchase.amount), 0))
        )
        return result.scalar_one() or 0.0

    async def revenue_for_period(self, start_date: datetime, end_date: datetime) -> float:
        result = await self.session.execute(
            select(func.sum(Purchase.amount))
            .where(Purchase.purchase_date >= start_date, Purchase.purchase_date < end_date)
        )
        return result.scalar_one() or 0.0

    async def total_purchases_count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Purchase))
        return result.scalar_one() or 0

    async def average_check(self) -> float:
        result = await self.session.execute(select(func.avg(Purchase.amount)))
        return result.scalar_one() or 0.0

    async def revenue_grouped_by_day(self, days_back: int = 7) -> list[tuple[date, float]]:
        start_date = datetime.now().date() - timedelta(days=days_back-1)
        result = await self.session.execute(
            select(
                func.date(Purchase.purchase_date).label('day'),
                func.sum(Purchase.amount).label('revenue')
            )
            .where(Purchase.purchase_date >= start_date)
            .group_by(func.date(Purchase.purchase_date))
            .order_by('day')
        )
        return [(row.day, row.revenue or 0.0) for row in result]

    async def revenue_by_genre(self) -> list[tuple[int, str, float]]:
        result = await self.session.execute(
            select(
                Genre.id,
                Genre.name,
                func.coalesce(func.sum(Purchase.amount), 0).label('revenue')  # ← coalesce
            )
            .join(Track, Track.id == Purchase.track_id)
            .join(Genre, Genre.id == Track.genre_id)
            .group_by(Genre.id, Genre.name)
            .order_by(func.coalesce(func.sum(Purchase.amount), 0).desc())
        )
        return [(row.id, row.name, row.revenue or 0.0) for row in result]