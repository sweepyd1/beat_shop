from sqlalchemy import select
from database.models import Author
from .base import BaseRepository

class AuthorRepository(BaseRepository[Author]):
    def __init__(self, session):
        super().__init__(Author, session)

    async def get_by_id(self, id: int) -> Author | None:
            """Получение автора по ID"""
            result = await self.session.execute(
                select(Author).where(Author.id == id)
            )
            return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Author | None:
            """Получение автора по ID пользователя"""
            result = await self.session.execute(
                select(Author).where(Author.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def create(
            self,
            user_id: int,
            full_name: str,
            photo_url: str | None = None,
            bio: str | None = None
        ) -> Author:
            """Создание профиля автора"""
            author = Author(
                user_id=user_id,
                full_name=full_name,
                photo_url=photo_url,
                bio=bio
            )
            self.session.add(author)
            await self.session.commit()
            await self.session.flush()
        
            await self.session.refresh(author)
            return author

    async def update(self, author_id: int, **kwargs) -> Author | None:
            """Обновление профиля автора"""
            author = await self.get_by_id(author_id)
            if not author:
                return None
            
            for key, value in kwargs.items():
                if hasattr(author, key) and value is not None:
                    setattr(author, key, value)
            
            await self.session.flush()
            await self.session.refresh(author)
            return author

    async def delete(self, author_id: int) -> bool:
            """Удаление профиля автора"""
            author = await self.get_by_id(author_id)
            if not author:
                return False
            
            await self.session.delete(author)
            await self.session.flush()
            return True
    
