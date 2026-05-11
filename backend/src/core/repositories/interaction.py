from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Tuple
from database.models import Interaction, InteractionType, Track, User

class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_top_listeners(self, limit: int = 10) -> List[Tuple[User, int]]:
        """Возвращает список (пользователь, количество прослушиваний) топ слушателей"""
        stmt = (
            select(User, func.count(Interaction.id).label('listen_count'))
            .join(Interaction, User.id == Interaction.user_id)
            .where(Interaction.interaction_type == InteractionType.listen)
            .group_by(User.id)
            .order_by(func.count(Interaction.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [(user, count) for user, count in result]

    async def get_listen_count_by_user(self, user_id: int) -> int:
        """Количество прослушиваний конкретного пользователя"""
        stmt = select(func.count(Interaction.id)).where(
            Interaction.user_id == user_id,
            Interaction.interaction_type == InteractionType.listen
        )
        return await self.session.scalar(stmt) or 0

    async def get_active_users_count_since(self, days: int = 30) -> int:
        """Количество уникальных пользователей, совершивших покупку или прослушивание за последние N дней"""
        since_date = datetime.utcnow() - timedelta(days=days)
        # Используем UNION через подзапрос
        from sqlalchemy import union
        from database.models import Purchase

        purchase_subq = select(Purchase.user_id).where(Purchase.purchase_date >= since_date)
        listen_subq = select(Interaction.user_id).where(
            Interaction.interaction_type == InteractionType.listen,
            Interaction.timestamp >= since_date
        )
        union_stmt = union(purchase_subq, listen_subq).subquery()
        stmt = select(func.count(func.distinct(union_stmt.c.user_id)))
        return await self.session.scalar(stmt) or 0
    
    async def count_plays_by_author(self, author_id: int) -> int:
        """Количество прослушиваний всех треков автора"""
        subq = select(Track.id).where(Track.author_id == author_id).subquery()
        stmt = (
            select(func.count())
            .where(
                Interaction.track_id.in_(subq),
                Interaction.interaction_type == InteractionType.listen
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_favorites_by_author(self, author_id: int) -> int:
        """Количество лайков всех треков автора"""
        subq = select(Track.id).where(Track.author_id == author_id).subquery()
        stmt = (
            select(func.count())
            .where(
                Interaction.track_id.in_(subq),
                Interaction.interaction_type == InteractionType.favorite
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_last_7_days_plays(self, author_id: int) -> list[int]:
        """Прослушивания за последние 7 дней (массив из 7 чисел)"""
        start_date = datetime.now() - timedelta(days=6)
        subq = select(Track.id).where(Track.author_id == author_id).subquery()
        stmt = (
            select(func.date(Interaction.timestamp), func.count())
            .where(
                Interaction.track_id.in_(subq),
                Interaction.interaction_type == InteractionType.listen,
                Interaction.timestamp >= start_date
            )
            .group_by(func.date(Interaction.timestamp))
            .order_by(func.date(Interaction.timestamp))
        )
        result = await self.session.execute(stmt)
        rows = {row[0]: row[1] for row in result.all()}
        today = datetime.now().date()
        return [rows.get(today - timedelta(days=i), 0) for i in range(6, -1, -1)]