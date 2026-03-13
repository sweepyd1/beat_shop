from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Subscription, Author
from .base import BaseRepository

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session):
        super().__init__(Subscription, session)

    async def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """Получить все подписки пользователя с подгрузкой автора"""
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .options(selectinload(Subscription.author))
            .order_by(Subscription.subscribed_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_author(self, user_id: int, author_id: int) -> Optional[Subscription]:
        result = await self.session.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.author_id == author_id
            )
        )
        return result.scalar_one_or_none()