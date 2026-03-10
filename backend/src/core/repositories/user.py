# src/core/repositories/user.py

from sqlalchemy import select, or_
from database.models import User
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