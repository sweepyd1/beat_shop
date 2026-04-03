from typing import List, Optional
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from database.models import Author, Genre, Purchase, Track
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
    async def search(
        self,
        query: Optional[str] = None,
        genre_ids: Optional[List[int]] = None,
        bpm_min: Optional[int] = None,
        bpm_max: Optional[int] = None,
        duration_min: Optional[int] = None,  # в секундах
        duration_max: Optional[int] = None,
        sort_by: str = "popular",  # popular, newest, price_asc, price_desc
        skip: int = 0,
        limit: int = 20
    ) -> List[Track]:
        stmt = select(Track).options(
            selectinload(Track.genre),
            selectinload(Track.author)
        )

        # Фильтр по поисковому запросу (по названию трека или имени автора)
        if query:
            stmt = stmt.join(Track.author).where(
                or_(
                    Track.title.ilike(f"%{query}%"),
                    Author.full_name.ilike(f"%{query}%")
                )
            )

        # Фильтр по жанрам
        if genre_ids:
            stmt = stmt.where(Track.genre_id.in_(genre_ids))

        # Фильтр по BPM
        if bpm_min is not None:
            stmt = stmt.where(Track.bpm >= bpm_min)
        if bpm_max is not None:
            stmt = stmt.where(Track.bpm <= bpm_max)

        # Фильтр по длительности (в секундах)
        if duration_min is not None:
            stmt = stmt.where(Track.duration_seconds >= duration_min)
        if duration_max is not None:
            stmt = stmt.where(Track.duration_seconds <= duration_max)

        # Сортировка
        if sort_by == "newest":
            stmt = stmt.order_by(Track.added_date.desc())
        elif sort_by == "price_asc":
            stmt = stmt.order_by(Track.price.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Track.price.desc())
        else:  # popular по умолчанию
            stmt = stmt.order_by(Track.plays.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    async def create(self, **kwargs) -> Track:
        track = Track(**kwargs)
        self.session.add(track)
        await self.session.commit()
        await self.session.flush()
        await self.session.refresh(track)
        return track
    
    async def get_by_author_id(self, author_id: int) -> List[Track]:
        """Получение всех треков автора по author_id"""
        stmt = select(Track).where(Track.author_id == author_id).options(
            selectinload(Track.genre),
            selectinload(Track.author)
        ).order_by(Track.added_date.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_sales_count(self, track_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Purchase).where(Purchase.track_id == track_id)
        )
        return result.scalar_one() or 0
    async def count_by_author(self, author_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Track).where(Track.author_id == author_id)
        )
        return result.scalar_one() or 0
    async def total_listens(self) -> int:
        result = await self.session.execute(select(func.sum(Track.plays)))
        return result.scalar_one() or 0

    async def top_tracks_by_revenue(self, limit: int = 10) -> list[tuple]:
        result = await self.session.execute(
            select(
                Track.id,
                Track.title,
                Author.full_name.label('author_name'),
                Genre.name.label('genre_name'),
                func.count(Purchase.id).label('sales_count'),
                func.coalesce(func.sum(Purchase.amount), 0).label('revenue'),  # ← ключевое изменение
                Track.cover_url
            )
            .outerjoin(Purchase, Purchase.track_id == Track.id)
            .join(Author, Author.id == Track.author_id)
            .join(Genre, Genre.id == Track.genre_id)
            .group_by(Track.id, Author.full_name, Genre.name)
            .order_by(func.coalesce(func.sum(Purchase.amount), 0).desc())
            .limit(limit)
        )
        return result.all()