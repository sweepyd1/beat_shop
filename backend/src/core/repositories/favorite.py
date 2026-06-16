from typing import List, Optional
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload
from database.models import Favorite, Track
from .base import BaseRepository


class FavoriteRepository(BaseRepository[Favorite]):
    def __init__(self, session):
        super().__init__(Favorite, session)

    async def get_user_favorites(self, user_id: int) -> List[Favorite]:
        """Получить все избранные треки пользователя с подгрузкой трека и автора"""
        result = await self.session.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Favorite.track).selectinload(Track.author),
                selectinload(Favorite.track).selectinload(Track.genre)
            )
            .order_by(Favorite.added_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_track(self, user_id: int, track_id: int) -> Optional[Favorite]:
        result = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.track_id == track_id
            )
        )
        return result.scalar_one_or_none()
    # async def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100):
    #     stmt = select(Favorite).where(Favorite.user_id == user_id).offset(skip).limit(limit)
    #     result = await self.session.execute(stmt)
    #     return result.scalars().all()

    async def exists(self, user_id: int, track_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_by_user_track(self, user_id: int, track_id: int) -> bool:
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id
        ).returning(Favorite.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none() is not None
    async def count_favorites_by_author(self, author_id: int) -> int:
        stmt = (
            select(func.count(Favorite.id))
            .join(Track, Favorite.track_id == Track.id)
            .where(Track.author_id == author_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0