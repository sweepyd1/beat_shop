from typing import AsyncIterator
from fastapi import Depends, HTTPException, Request
import librosa
import numpy as np
import mutagen
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from core.repositories.interaction import InteractionRepository
from core.services.admin_stats import AdminStatsService
from core.repositories.subscription import SubscriptionRepository
from core.services.stats import StatsService
from core.repositories.listen import ListenRepository
from core.services.listen import ListenService
from core.repositories.purchase import PurchaseRepository
from core.services.contract_service import ContractService
from core.services.purchase import PurchaseService
from core.repositories.author import AuthorRepository
from core.services.author import AuthorService
from core.repositories.genre import GenreRepository
from core.services.genre import GenreService
from database.models import User
from core.repositories.user import UserRepository
from core.repositories.favorite import FavoriteRepository
from core.services.auth import AuthService
from core.repositories.track import TrackRepository
from core.services.track import TrackService
from core.services.file_service import FileService
from core.services.favorite import FavoriteService
from database.db_manager import db_manager
from fastapi import status
from pathlib import Path

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with db_manager.get_session() as session:
        yield session

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)

def get_genre_repository(session: AsyncSession = Depends(get_db_session)) -> GenreRepository:
    return GenreRepository(session)

def get_track_repository(session: AsyncSession = Depends(get_db_session)) -> TrackRepository:
    return TrackRepository(session)

def get_favorite_repository(session: AsyncSession = Depends(get_db_session)) -> FavoriteRepository:
    return FavoriteRepository(session)

def get_author_repository(session: AsyncSession = Depends(get_db_session)) -> AuthorRepository:
    return AuthorRepository(session)
def get_purchase_repository(session: AsyncSession = Depends(get_db_session)) -> PurchaseRepository:
    return PurchaseRepository(session)
async def get_interaction_repository(session: AsyncSession = Depends(get_db_session)) -> InteractionRepository:
    return InteractionRepository(session)

# ---------- Сервисы ----------
def get_auth_service(repo: UserRepository = Depends(get_user_repository),  author_repo: AuthorRepository = Depends(get_author_repository),) -> AuthService:
    return AuthService(repo, author_repo)
def get_file_service() -> FileService:
    return FileService()

async def get_author_service(
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
) -> AuthorService:
    repo = AuthorRepository(session)
    return AuthorService(repo, file_service)



def get_favorite_service(
    repo: FavoriteRepository = Depends(get_favorite_repository),
    track_repo: TrackRepository = Depends(get_track_repository)
) -> FavoriteService:
    return FavoriteService(repo, track_repo)
def get_contract_service(session: AsyncSession = Depends(get_db_session), file_service: FileService = Depends(get_file_service)) -> ContractService:
    return ContractService(session, file_service)

def get_purchase_service(
    session: AsyncSession = Depends(get_db_session),
    contract_service: ContractService = Depends(get_contract_service)
) -> PurchaseService:
    return PurchaseService(session, contract_service)

def get_genre_service(repo: GenreRepository = Depends(get_genre_repository)) -> GenreService:
    return GenreService(repo)
async def get_track_service(
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service),
    author_service: AuthorService = Depends(get_author_service),
    genre_service: GenreService = Depends(get_genre_service)
) -> TrackService:
    track_repo = TrackRepository(session)
    return TrackService(track_repo, author_service, genre_service, file_service)
async def get_listen_service(
    session:AsyncSession = Depends(get_db_session)
) -> ListenService:
    """Зависимость для получения ListenService"""
    return ListenService(
        repo=ListenRepository(session),
        track_repo=TrackRepository(session)
    )
def get_subscription_repository(session: AsyncSession = Depends(get_db_session)) -> SubscriptionRepository:
    return SubscriptionRepository(session)

# Сервис статистики
# dependencies.py
def get_stats_service(
    purchase_repo: PurchaseRepository = Depends(get_purchase_repository),
    subscription_repo: SubscriptionRepository = Depends(get_subscription_repository),
    track_repo: TrackRepository = Depends(get_track_repository),              # добавить
    interaction_repo: InteractionRepository = Depends(get_interaction_repository)  # добавить
) -> StatsService:
    return StatsService(purchase_repo, subscription_repo, track_repo, interaction_repo)
async def get_admin_stats_service(
    user_repo: UserRepository = Depends(get_user_repository),
    purchase_repo: PurchaseRepository = Depends(get_purchase_repository),
    track_repo: TrackRepository = Depends(get_track_repository),
    interaction_repo: InteractionRepository = Depends(get_interaction_repository),
) -> AdminStatsService:
    return AdminStatsService(user_repo, purchase_repo, track_repo, interaction_repo)
# ---------- Текущий пользователь (из JWT) ----------
async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository)
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    user_id = await auth_service.verify_token(access_token)
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
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора."
        )
    return current_user

def analyze_mp3(file_path: Path) -> tuple[float, int]:
    """
    Возвращает (duration_seconds: float, bpm: int)
    """
    # 1. Длительность через mutagen (мгновенно, без декодирования)
    try:
        audio_info = mutagen.File(file_path)
        if audio_info and hasattr(audio_info.info, 'length'):
            duration = audio_info.info.length
        else:
            duration = 0.0
    except Exception:
        duration = 0.0

    # 2. BPM через librosa (загружаем только первые 30 секунд для скорости)
    try:
        # Загружаем аудио (librosa сконвертирует в моно, sr=22050)
        # Можно ограничить по времени: duration=30 (если трек длинный)
        y, sr = librosa.load(file_path, sr=22050, duration=30)
        if len(y) > 0:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0] if isinstance(tempo, (list, tuple, np.ndarray)) else tempo)
            bpm = int(round(bpm))
        else:
            bpm = None
    except Exception as e:
        
        print(f"BPM analysis failed: {e}")
        bpm = None

    # Если длительность не получилась через mutagen – пробуем через librosa
    if duration == 0.0:
        try:
            duration = librosa.get_duration(filename=str(file_path))
        except:
            duration = 0.0

    return duration, bpm
