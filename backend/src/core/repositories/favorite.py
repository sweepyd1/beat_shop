from typing import List, Optional
from sqlalchemy import select
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
                selectinload(Favorite.track).selectinload(Track.author)
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