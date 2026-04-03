from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid
from schemas.admin_stats import (
    MetricsResponse, DailySalesResponse, DailyUsersResponse,
    TopTrackResponse, GenreSalesResponse
)
from core.services.admin_stats import AdminStatsService
from api.dependencies import get_admin_stats_service
from api.dependencies import get_db_session, get_current_admin
from core.repositories.track import TrackRepository
from database.models import User, Track
from schemas.track import TrackResponse

router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = Path("storage/tracks")
COVER_DIR = Path("storage/covers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
COVER_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/stats/metrics", response_model=MetricsResponse)
async def get_stats_metrics(
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_metrics()

@router.get("/stats/sales-daily", response_model=list[DailySalesResponse])
async def get_daily_sales(
    days: int = 7,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_daily_sales(days)

@router.get("/stats/users-daily", response_model=list[DailyUsersResponse])
async def get_daily_users(
    days: int = 7,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_daily_users(days)

@router.get("/stats/top-tracks", response_model=list[TopTrackResponse])
async def get_top_tracks(
    limit: int = 10,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_top_tracks(limit)

@router.get("/stats/genres", response_model=list[GenreSalesResponse])
async def get_genre_sales(
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_genre_sales()
@router.post("/tracks", response_model=TrackResponse)
async def create_track(
    title: str = Form(...),
    genre_id: int = Form(...),
    author_id: int = Form(...),
    price: float = Form(...),
    bpm: Optional[int] = Form(None),
    duration_seconds: Optional[int] = Form(None),
    mp3_file: UploadFile = File(...),
    cover: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    # Проверка расширений
    if not mp3_file.filename.endswith('.mp3'):
        raise HTTPException(400, "Только MP3")
    if not cover.filename.lower().endswith(('.jpg','.jpeg','.png')):
        raise HTTPException(400, "Только изображения (jpg,png)")

    # Генерация имён файлов
    mp3_filename = f"{uuid.uuid4().hex}.mp3"
    cover_filename = f"{uuid.uuid4().hex}{Path(cover.filename).suffix}"

    mp3_path = UPLOAD_DIR / mp3_filename
    cover_path = COVER_DIR / cover_filename

    # Сохранение файлов
    try:
        with open(mp3_path, "wb") as f:
            shutil.copyfileobj(mp3_file.file, f)
        with open(cover_path, "wb") as f:
            shutil.copyfileobj(cover.file, f)
    except Exception as e:
        raise HTTPException(500, f"Ошибка сохранения: {str(e)}")

    # Создание записи в БД
    track_data = {
        "title": title,
        "cover_url": f"/storage/covers/{cover_filename}",
        "duration_seconds": duration_seconds,
        "created_date": datetime.utcnow(),
        "mp3_file_url": f"/storage/tracks/{mp3_filename}",
        "price": price,
        "plays": 0,
        "bpm": bpm,
        "genre_id": genre_id,
        "author_id": author_id,
    }
    track = Track(**track_data)
    session.add(track)
    await session.commit()
    await session.refresh(track)

    # Загрузка связей для ответа
    result = await session.get(Track, track.id, options=[selectinload(Track.author), selectinload(Track.genre)])
    return result

