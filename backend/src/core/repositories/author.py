from database.models import Author
from .base import BaseRepository

class AuthorRepository(BaseRepository[Author]):
    def __init__(self, session):
        super().__init__(Author, session)