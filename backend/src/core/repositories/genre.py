from sqlalchemy import func, select
from database.models import Genre, Track
from .base import BaseRepository

class GenreRepository(BaseRepository[Genre]):
    def __init__(self, session):
        super().__init__(Genre, session)

    async def get_all_with_counts(self):
            result = await self.session.execute(
                select(Genre, func.count(Track.id).label("tracks_count"))
                .outerjoin(Track, Track.genre_id == Genre.id)
                .group_by(Genre.id)
            )
            
            return result.all()