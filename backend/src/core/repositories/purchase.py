from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from database.models import Author, Genre, LicenseType, Purchase, Track
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
 
    async def get_daily_purchases(self, days: int = 30):
        """Количество покупок и сумма по дням за последние N дней"""
        start_date = datetime.utcnow().date() - timedelta(days=days-1)
        stmt = (
            select(
                func.date(Purchase.purchase_date).label('date'),
                func.count(Purchase.id).label('purchase_count'),
                func.sum(Purchase.amount).label('total_amount')
            )
            .where(func.date(Purchase.purchase_date) >= start_date)
            .group_by(func.date(Purchase.purchase_date))
            .order_by('date')
        )
        result = await self.session.execute(stmt)
        rows = {row.date: (row.purchase_count, row.total_amount or 0.0) for row in result}
        full = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            cnt, amt = rows.get(d, (0, 0.0))
            full.append((d, cnt, amt))
        return full

    async def get_monthly_earnings_last_n_months(self, author_id: int, months: int = 6) -> list[dict]:
        """Возвращает список {'month': 'YYYY-MM', 'amount': float} за последние N месяцев"""
        now = datetime.now()
        first_day_current = datetime(now.year, now.month, 1)
        start_date = first_day_current - timedelta(days=(months-1)*30)  # приблизительно
        stmt = (
            select(
                func.to_char(Purchase.purchase_date, 'YYYY-MM').label('month'),
                func.sum(Purchase.amount).label('amount')
            )
            .join(Track, Track.id == Purchase.track_id)
            .where(Track.author_id == author_id, Purchase.purchase_date >= start_date)
            .group_by('month')
            .order_by('month')
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [{'month': row.month, 'amount': float(row.amount)} for row in rows]

    async def get_sales_by_license_type(self, author_id: int) -> list[dict]:
        """Возвращает список с license_type, count, total_amount"""
        stmt = (
            select(
                Purchase.license_type,
                func.count(Purchase.id).label('count'),
                func.sum(Purchase.amount).label('total_amount')
            )
            .join(Track, Track.id == Purchase.track_id)
            .where(Track.author_id == author_id)
            .group_by(Purchase.license_type)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            {
                'license_type': row.license_type.value,  # если license_type это Enum
                'count': row.count,
                'total_amount': float(row.total_amount)
            }
            for row in rows
        ]

    async def get_top_tracks_by_sales(self, author_id: int, limit: int = 5) -> list[dict]:
        """Топ треков по количеству продаж и выручке"""
        stmt = (
            select(
                Track.id,
                Track.title,
                Track.cover_url,
                func.count(Purchase.id).label('sales_count'),
                func.sum(Purchase.amount).label('revenue')
            )
            .outerjoin(Purchase, Purchase.track_id == Track.id)
            .where(Track.author_id == author_id)
            .group_by(Track.id)
            .order_by(func.count(Purchase.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            {
                'track_id': row.id,
                'title': row.title,
                'cover_url': row.cover_url,
                'sales_count': row.sales_count or 0,
                'revenue': float(row.revenue or 0.0)
            }
            for row in rows
        ]

    async def get_last_7_days_sales_count(self, author_id: int) -> list[int]:
        """Количество продаж за последние 7 дней (массив из 7 чисел)"""
        now = datetime.now()
        days = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0)
            day_end = (now - timedelta(days=i-1)).replace(hour=0, minute=0, second=0) if i > 0 else now
            result = await self.session.execute(
                select(func.count(Purchase.id))
                .join(Track, Track.id == Purchase.track_id)
                .where(Track.author_id == author_id, Purchase.purchase_date >= day_start, Purchase.purchase_date < day_end)
            )
            days.append(result.scalar_one() or 0)
        return days
    
    async def create(self, user_id: int, track_id: int, amount: float, license_type: LicenseType, comment: str = None, status: str = "completed") -> Purchase:
        purchase = Purchase(
            user_id=user_id,
            track_id=track_id,
            amount=amount,
            license_type=license_type,
            comment=comment,
            status=status
        )
        self.session.add(purchase)
        await self.session.flush()
        return purchase

    async def get_user_purchase_for_track(self, user_id: int, track_id: int) -> Purchase | None:
        stmt = select(Purchase).where(
            Purchase.user_id == user_id,
            Purchase.track_id == track_id,
            Purchase.status == "completed"
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_exclusive_purchase_for_track(self, track_id: int) -> Purchase | None:
        """Возвращает первую завершённую покупку эксклюзивного трека (если есть)"""
        stmt = select(Purchase).join(Track).where(
            Track.id == track_id,
            Purchase.status == "completed"
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, purchase_id: int):
        stmt = (
            select(Purchase)
            .where(Purchase.id == purchase_id)
            .options(
                selectinload(Purchase.track).selectinload(Track.genre),
                selectinload(Purchase.track).selectinload(Track.author).selectinload(Author.user),
                selectinload(Purchase.user)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
