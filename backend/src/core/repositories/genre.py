from database.models import Genre
from .base import BaseRepository

class GenreRepository(BaseRepository[Genre]):
    def __init__(self, session):
        super().__init__(Genre, session)