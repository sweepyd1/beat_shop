from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from database.models import Track
from .base import BaseRepository

class TrackRepository(BaseRepository[Track]):
    def __init__(self, session):
        super().__init__(Track, session)

    async def get(self, id: int) -> Optional[Track]:
        """Получение трека с загрузкой связанных данных"""
        result = await self.session.execute(
            select(Track)
            .where(Track.id == id)
            .options(
                selectinload(Track.genre),   # 👈 загружаем жанр
                selectinload(Track.author)   # 👈 загружаем автора
            )
        )
        return result.scalar_one_or_none()
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Track]:
        result = await self.session.execute(
            select(Track)
            .options(
                selectinload(Track.genre),
                selectinload(Track.author)
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    async def get_popular(self, limit: int):
        """Возвращает популярные треки (по убыванию plays)."""
        result = await self.session.execute(
            select(Track)
            .options(selectinload(Track.author), selectinload(Track.genre))
            .order_by(Track.plays.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_new(self, limit: int):
        """Возвращает новые треки (по убыванию added_date)."""
        result = await self.session.execute(
            select(Track)
            .options(selectinload(Track.author), selectinload(Track.genre))
            .order_by(Track.added_date.desc())
            .limit(limit)
        )
        return result.scalars().all()
