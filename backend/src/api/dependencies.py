from typing import AsyncIterator
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from database.models import User
from core.repositories.user import UserRepository
from core.services.auth import AuthService
from core.repositories.track import TrackRepository
from core.services.track import TrackService
from core.services.file_service import FileService
from database.db_manager import db_manager
from fastapi import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with db_manager.get_session() as session:
        yield session

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_track_repository(session: AsyncSession = Depends(get_db_session)) -> TrackRepository:
    return TrackRepository(session)


# ---------- Сервисы ----------
def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)


def get_track_service(repo: TrackRepository = Depends(get_track_repository)) -> TrackService:
    return TrackService(repo=repo, file_service=get_file_service())


# ---------- Текущий пользователь (из JWT) ----------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Получение текущего аутентифицированного пользователя"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    user_id = await auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
    
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован"
        )
    
    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Опциональный пользователь (для страниц, где авторизация не обязательна)"""
    if not token:
        return None
    
    user_id = await auth_service.verify_token(token)
    if not user_id:
        return None
    
    user = await user_repo.get(user_id)
    if not user or not user.is_active:
        return None
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка, что текущий пользователь - администратор"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора."
        )
    return current_user



def get_file_service() -> FileService:
    return FileService()