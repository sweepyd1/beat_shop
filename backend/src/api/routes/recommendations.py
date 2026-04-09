from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
import os
from typing import List, Optional

from core.services.recommendation import RecommendationService
from api.dependencies import get_db_session, get_current_user_optional
from database.models import User
from schemas.track import TrackResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/personal", response_model=List[TrackResponse])
async def personal_recommendations(
    limit: int = 1,
    exclude: str = "",   # список ID через запятую, например "5,12,23"
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Персональная рекомендация. Если пользователь не авторизован – популярные треки."""
    service = RecommendationService(session)
    exclude_ids = [int(x.strip()) for x in exclude.split(",") if x.strip().isdigit()] if exclude else None
    if current_user:
        tracks = await service.get_personal_recommendation(current_user.id, limit, exclude_ids)
    else:
        tracks = await service.get_popular_tracks(limit, exclude_ids)
    return tracks

@router.get("/popular", response_model=List[TrackResponse])
async def popular(
    limit: int = 1,
    exclude: str = "",
    session: AsyncSession = Depends(get_db_session)
):
    service = RecommendationService(session)
    exclude_ids = [int(x.strip()) for x in exclude.split(",") if x.strip().isdigit()] if exclude else None
    tracks = await service.get_popular_tracks(limit, exclude_ids)
    return tracks

@router.get("/track/{track_id}", response_model=TrackResponse)
async def get_track_info(
    track_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    service = RecommendationService(session)
    track = await service.get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.get("/stream/{track_id}")
async def stream_track(
    track_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Возвращает MP3 файл для прослушивания"""
    service = RecommendationService(session)
    track = await service.get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Извлекаем имя файла из URL
    mp3_file_url = track.mp3_file_url
    if mp3_file_url.startswith('/storage/tracks/'):
        filename = mp3_file_url.replace('/storage/tracks/', '')
    else:
        filename = mp3_file_url.split('/')[-1]

    file_path = os.path.join("storage", "tracks", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Accept-Ranges": "bytes"}
    )