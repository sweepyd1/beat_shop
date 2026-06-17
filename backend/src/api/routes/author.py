from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.services.auth import AuthService
from schemas.author_stats import AuthorFullStatsResponse
from core.services.author import AuthorService
from core.services.stats import StatsService
from core.services.track import TrackService
from database.models import User, UserRole
from schemas.author import AuthorResponse, AuthorDetailResponse, AuthorUpdate
from core.repositories.author import AuthorRepository
from api.dependencies import (
    get_auth_service,
    get_author_service,
    get_current_user,
    get_db_session,
    get_stats_service,
    get_track_service,
)
from schemas.track import AuthorTrackResponse, TrackResponse
from typing import List
from sqlalchemy.orm import selectinload  


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[AuthorResponse])
async def get_authors(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_db_session)
):
    repo = AuthorRepository(session)
    authors = await repo.get_all(skip=skip, limit=limit)
    return authors


@router.get("/me", response_model=AuthorDetailResponse)
async def get_my_author_profile(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service),
    track_service: TrackService = Depends(get_track_service),  
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")

    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")

    stats = await stats_service.get_author_stats(author.id)
    total_earnings = await stats_service.get_total_earnings(author.id)
    tracks_count = await track_service.get_tracks_count(
        author.id
    )  

    return AuthorDetailResponse(
        id=author.id,
        user_id=author.user_id,
        full_name=author.full_name,
        photo_url=author.photo_url,
        bio=author.bio,
        followers_count=stats.followers_count,
        total_earnings=total_earnings,
        tracks_count=tracks_count,
        average_rating=stats.average_rating,
    )
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Purchase, Track, Author, UserRole

@router.get("/me/track-purchases")
async def get_my_track_purchases(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
    author_service: AuthorService = Depends(get_author_service),
):
    """Получение списка покупок треков текущего автора, сгруппированных по трекам"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await auth_service.get_user_from_token(access_token)
    if user.role != UserRole.author:
        raise HTTPException(status_code=403, detail="Только авторы могут просматривать продажи")
    
    author = await author_service.get_author_by_user_id(user.id)
    if not author:
        raise HTTPException(status_code=404, detail="Профиль автора не найден")
    
    # Получаем все покупки треков этого автора
    result = await session.execute(
        select(Purchase)
        .join(Track, Track.id == Purchase.track_id)
        .where(Track.author_id == author.id)
        .options(
            selectinload(Purchase.track),
            selectinload(Purchase.user),
            selectinload(Purchase.contract)
        )
        .order_by(Purchase.purchase_date.desc())
    )
    purchases = result.scalars().all()
    
    # Группируем по трекам
    grouped = {}
    for p in purchases:
        if p.track_id not in grouped:
            grouped[p.track_id] = {
                "track_id": p.track_id,
                "track_title": p.track.title,
                "cover_url": p.track.cover_url,
                "purchases": []
            }
        grouped[p.track_id]["purchases"].append({
            "id": p.id,
            "buyer_name": p.user.full_name,
            "purchase_date": p.purchase_date.isoformat() if p.purchase_date else None,
            "amount": p.amount,
            "license_type": p.license_type.value if p.license_type else None,
            "has_contract": p.contract is not None and p.contract.document_url is not None,
            "contract_number": p.contract.contract_number if p.contract else None
        })
    
    return list(grouped.values())

@router.get("/me/tracks", response_model=list[AuthorTrackResponse])
async def get_my_tracks(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    track_service: TrackService = Depends(get_track_service),
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")

    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")

    tracks = await track_service.get_author_tracks(author.id)
    return tracks


@router.get(
    "/me/stats",
)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service),
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")

    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")

    stats = await stats_service.get_author_stats(author.id)
    return stats


class AuthorPublicResponse(AuthorDetailResponse):
    tracks: List[AuthorTrackResponse] = []


@router.get("/{author_id}", response_model=AuthorPublicResponse)
async def get_author_public(
    author_id: int,
    session: AsyncSession = Depends(get_db_session),
    stats_service: StatsService = Depends(get_stats_service),
    track_service: TrackService = Depends(get_track_service),
):
    """Публичная страница автора - доступна всем пользователям"""
    repo = AuthorRepository(session)
    author = await repo.get(author_id)
    if not author:
        raise HTTPException(404, "Автор не найден")

    
    stats = await stats_service.get_author_stats(author.id)
    total_earnings = await stats_service.get_total_earnings(author.id)
    tracks_count = await track_service.get_tracks_count(author.id)

    
    tracks = await track_service.get_author_tracks(author.id)
    user = await session.get(User, author.user_id)
    photo_url = user.avatar_url if user else None
    
    response = AuthorPublicResponse(
        id=author.id,
        user_id=author.user_id,
        full_name=author.full_name,
        photo_url=photo_url,
        bio=author.bio,
        followers_count=stats.followers_count,
        total_earnings=total_earnings,
        tracks_count=tracks_count,
        average_rating=stats.average_rating,
        tracks=tracks,
    )
    return response


@router.get("/me/full-stats", response_model=AuthorFullStatsResponse)
async def get_my_full_stats(
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
    stats_service: StatsService = Depends(get_stats_service),
):
    if current_user.role.value != "author":
        raise HTTPException(403, "Пользователь не является автором")
    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    return await stats_service.get_author_full_stats(author.id)


@router.patch("/me", response_model=AuthorDetailResponse)
async def update_my_profile(
    update_data: AuthorUpdate,
    current_user: User = Depends(get_current_user),
    author_service: AuthorService = Depends(get_author_service),
):
    if current_user.role != UserRole.author:
        raise HTTPException(403, "Только автор может редактировать профиль")

    author = await author_service.get_author_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")

    updated = await author_service.update_author(
        author.id, update_data, photo_file=None
    )
    if not updated:
        raise HTTPException(500, "Не удалось обновить профиль")

    
    return updated
