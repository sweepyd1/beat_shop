# core/repositories/purchase_repository.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from database.models import Author, LicenseType, Purchase, Track
from sqlalchemy.orm import selectinload

class PurchaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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

async def get_sales_by_license_type(self, author_id: int) -> list[dict]:
    stmt = (
        select(
            Purchase.license_type,
            func.count(Purchase.id).label('count'),
            func.sum(Purchase.amount).label('total_amount')
        )
        .join(Track, Track.id == Purchase.track_id)
        .where(Track.author_id == author_id, Purchase.status == 'completed')
        .group_by(Purchase.license_type)
    )
    result = await self.session.execute(stmt)
    return [{'license_type': row[0].value, 'count': row[1], 'total_amount': float(row[2])} for row in result.all()]

async def get_top_tracks_by_sales(self, author_id: int, limit: int = 5) -> list[dict]:
    stmt = (
        select(
            Track.id, Track.title, Track.cover_url,
            func.count(Purchase.id).label('sales_count'),
            func.sum(Purchase.amount).label('revenue')
        )
        .outerjoin(Purchase, Purchase.track_id == Track.id)
        .where(Track.author_id == author_id, Purchase.status == 'completed')
        .group_by(Track.id)
        .order_by(func.count(Purchase.id).desc())
        .limit(limit)
    )
    result = await self.session.execute(stmt)
    rows = result.all()
    return [
        {
            'track_id': row[0], 'title': row[1], 'cover_url': row[2],
            'sales_count': row[3] or 0, 'revenue': float(row[4] or 0)
        }
        for row in rows
    ]

async def get_monthly_earnings_last_n_months(self, author_id: int, months: int = 6) -> list[dict]:
    start_date = datetime.now() - timedelta(days=months*30)
    stmt = (
        select(
            func.date_format(Purchase.purchase_date, '%Y-%m').label('month'),
            func.sum(Purchase.amount).label('amount')
        )
        .join(Track, Track.id == Purchase.track_id)
        .where(Track.author_id == author_id, Purchase.purchase_date >= start_date, Purchase.status == 'completed')
        .group_by('month')
        .order_by('month')
    )
    result = await self.session.execute(stmt)
    return [{'month': row[0], 'amount': float(row[1])} for row in result.all()]