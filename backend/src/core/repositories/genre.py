from sqlalchemy import func, select
from database.models import Genre, Track
from .base import BaseRepository
from sqlalchemy.orm import selectinload
class GenreRepository(BaseRepository[Genre]):
    def __init__(self, session):
        super().__init__(Genre, session)
    async def create(self, name: str, image_url: str | None = None) -> Genre:
        genre = Genre(name=name, image_url=image_url)
        self.session.add(genre)
        await self.session.commit()
        await self.session.refresh(genre)
        return genre

    async def update(self, genre_id: int, name: str | None = None, image_url: str | None = None) -> Genre | None:
        genre = await self.get(genre_id)
        if not genre:
            return None
        if name is not None:
            genre.name = name
        if image_url is not None:
            genre.image_url = image_url
        await self.session.commit()
        await self.session.refresh(genre)
        return genre
    async def get_all_with_counts(self):
            result = await self.session.execute(
                select(Genre, func.count(Track.id).label("tracks_count"))
                .outerjoin(Track, Track.genre_id == Genre.id)
                .group_by(Genre.id)
            )
            
            return result.all()
    async def get_with_tracks(self, genre_id: int) -> Genre | None:
        """Получает жанр вместе с его треками (для проверки перед удалением)."""
        stmt = (
            select(Genre)
            .where(Genre.id == genre_id)
            .options(selectinload(Genre.tracks))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()