from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Purchase, Track
from .base import BaseRepository

class PurchaseRepository(BaseRepository[Purchase]):
    def __init__(self, session):
        super().__init__(Purchase, session)

    async def get_user_purchases(self, user_id: int) -> List[Purchase]:
        result = await self.session.execute(
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .options(selectinload(Purchase.track).selectinload(Track.author))
            .order_by(Purchase.purchase_date.desc())
        )
        return result.scalars().all()