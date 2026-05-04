# src/core/repositories/user.py
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import func, select, or_
from database.models import Favorite, Interaction, Purchase, Subscription, Track, User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def get_by_login(self, login: str) -> User | None:
        """Поиск пользователя по логину или email"""
        result = await self.session.execute(
            select(User).where(
                or_(
                    User.login == login,
                    User.email == login
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def check_exists(self, login: str, email: str) -> bool:
        """Проверка, существует ли пользователь с таким логином или email"""
        result = await self.session.execute(
            select(User).where(
                or_(
                    User.login == login,
                    User.email == email
                )
            )
        )
        return result.first() is not None
    
    

    async def get_with_relations(self, user_id: int) -> Optional[User]:
        """Получить пользователя со всеми связанными данными (подписки, покупки, избранное)"""
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                # Загрузка подписок с авторами
                selectinload(User.subscriptions).selectinload(Subscription.author),
                # Загрузка покупок с треками, у которых загружены авторы и жанры
                selectinload(User.purchases)
                    .selectinload(Purchase.track)
                    .selectinload(Track.author),   # автор трека
                selectinload(User.purchases)
                    .selectinload(Purchase.track)
                    .selectinload(Track.genre),    # 👈 жанр трека (исправляет ошибку)
                # Загрузка избранного с треками, у которых загружены авторы и жанры
                selectinload(User.favorites)
                    .selectinload(Favorite.track)
                    .selectinload(Track.author),
                selectinload(User.favorites)
                    .selectinload(Favorite.track)
                    .selectinload(Track.genre),    # 👈 и здесь тоже
                # Загрузка интеракций (прослушивания для топ жанров)
                selectinload(User.interactions)
                    .selectinload(Interaction.track)
                    .selectinload(Track.genre),    # 👈 и для интеракций
            )
        )
        return result.scalar_one_or_none()

    async def get_purchases(self, user_id: int) -> List[Purchase]:
        result = await self.session.execute(
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .options(selectinload(Purchase.track).selectinload(Track.author))
            .order_by(Purchase.purchase_date.desc())
        )
        return result.scalars().all()

    async def get_favorites(self, user_id: int) -> List[Favorite]:
        result = await self.session.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(selectinload(Favorite.track).selectinload(Track.author))
            .order_by(Favorite.added_at.desc())
        )
        return result.scalars().all()

    async def get_subscriptions(self, user_id: int) -> List[Subscription]:
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .options(selectinload(Subscription.author))
            .order_by(Subscription.subscribed_at.desc())
        )
        return result.scalars().all()
    
    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(User))
        return result.scalar_one() or 0

    async def count_registered_since(self, since_date: datetime) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.registered_at >= since_date)
        )
        return result.scalar_one() or 0
    async def count_registered_on_date(self, target_date: date) -> int:
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        result = await self.session.execute(
            select(func.count())
            .where(User.registered_at >= start, User.registered_at < end)
        )
        return result.scalar_one() or 0

    async def get_top_buyers(self, limit: int = 10):
        """Возвращает список пользователей с суммой покупок и количеством покупок"""
        stmt = (
            select(
                User.id,
                User.full_name,
                User.login,
                func.sum(Purchase.amount).label('total_spent'),
                func.count(Purchase.id).label('purchases_count')
            )
            .join(Purchase, User.id == Purchase.user_id)
            .group_by(User.id)
            .order_by(func.sum(Purchase.amount).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()  # каждая строка: (id, full_name, login, total_spent, purchases_count)

    async def get_role_distribution(self):
        """Распределение пользователей по ролям"""
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        result = await self.session.execute(stmt)
        return [(role.value, count) for role, count in result]  # role.value т.к. role - Enum
