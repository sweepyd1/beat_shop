from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.author_stats import AuthorFullStatsResponse
from core.services.author import AuthorService
from core.services.stats import StatsService
from core.services.track import TrackService
from database.models import User, UserRole
from schemas.author import AuthorResponse, AuthorDetailResponse
from core.repositories.author import AuthorRepository
from api.dependencies import get_author_service, get_current_user, get_db_session, get_stats_service, get_track_service
from schemas.track import AuthorTrackResponse, TrackResponse


router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/", response_model=list[AuthorResponse])
async def get_authors(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    repo = AuthorRepository(session)
    authors = await repo.get_all(skip=skip, limit=limit)
    return authors

@router.get("/me", response_model=AuthorDetailResponse)
async def get_my_author_profile(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service),
    track_service: TrackService = Depends(get_track_service)  # добавить
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")
    
    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    
    stats = await stats_service.get_author_stats(author.id)
    total_earnings = await stats_service.get_total_earnings(author.id)
    tracks_count = await track_service.get_tracks_count(author.id)  # вместо len(author.tracks)

    return AuthorDetailResponse(
        id=author.id,
        user_id=author.user_id,
        full_name=author.full_name,
        photo_url=author.photo_url,
        bio=author.bio,
        followers_count=stats.followers_count,
        total_earnings=total_earnings,
        tracks_count=tracks_count,
        average_rating=stats.average_rating
    )
@router.get("/me/tracks", response_model=list[AuthorTrackResponse])
async def get_my_tracks(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    track_service: TrackService = Depends(get_track_service)
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")
    
    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    
    tracks = await track_service.get_author_tracks(author.id)
    return tracks

@router.get("/me/stats",)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")
    
    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    
    stats = await stats_service.get_author_stats(author.id)
    return stats

@router.get("/{author_id}", response_model=AuthorDetailResponse)
async def get_author(
    author_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    repo = AuthorRepository(session)
    author = await repo.get(author_id)
    if not author:
        raise HTTPException(404, "Автор не найден")
    # Подсчёт количества треков
    tracks_count = len(author.tracks) if author.tracks else 0
    response = AuthorDetailResponse.model_validate(author)
    response.tracks_count = tracks_count
    return response

@router.get("/me/full-stats", response_model=AuthorFullStatsResponse)
async def get_my_full_stats(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")
    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    return await stats_service.get_author_full_stats(author.id)