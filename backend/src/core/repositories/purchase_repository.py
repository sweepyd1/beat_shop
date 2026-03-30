# core/repositories/purchase_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import LicenseType, Purchase, Track


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

    async def get_by_id(self, purchase_id: int) -> Purchase | None:
        stmt = select(Purchase).where(Purchase.id == purchase_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()