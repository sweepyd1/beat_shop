from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import librosa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid
from core.services.track import TrackService
from schemas.admin_stats import (
    DailyUserPurchasesResponse, DailyUserRegistrationsResponse, MetricsResponse, DailySalesResponse, DailyUsersResponse, TopBuyerResponse, TopListenerResponse,
    TopTrackResponse, GenreSalesResponse, UserMetricsResponse, UserRoleDistributionResponse
)
from core.services.admin_stats import AdminStatsService
from api.dependencies import get_admin_stats_service, get_track_service
from api.dependencies import get_db_session, get_current_admin, analyze_mp3
from database.models import User, Track
from schemas.track import TrackResponse
import mutagen
import numpy as np
router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = Path("storage/tracks")
COVER_DIR = Path("storage/covers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
COVER_DIR.mkdir(parents=True, exist_ok=True)



@router.get("/tracks", response_model=list[TrackResponse])
async def get_all_tracks(
    admin: User = Depends(get_current_admin),
    track_service: TrackService = Depends(get_track_service)
):
    tracks = await track_service.search_tracks(limit=1000)
    return tracks

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

@router.post("/tracks")
async def create_track(
    title: str = Form(...),
    genre_id: int = Form(...),
    author_id: int = Form(...),
    price: float = Form(...),
    mp3_file: UploadFile = File(...),
    cover: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
):
    # ... проверки расширений ...
    if not mp3_file.filename.endswith('.mp3'):
        raise HTTPException(400, "Только MP3")
    if not cover.filename.lower().endswith(('.jpg','.jpeg','.png')):
        raise HTTPException(400, "Только изображения (jpg,png)")

    # Генерация имён
    mp3_filename = f"{uuid.uuid4().hex}.mp3"
    cover_filename = f"{uuid.uuid4().hex}{Path(cover.filename).suffix}"
    mp3_path = UPLOAD_DIR / mp3_filename
    cover_path = COVER_DIR / cover_filename

    # Сохраняем файлы
    try:
        with open(mp3_path, "wb") as f:
            shutil.copyfileobj(mp3_file.file, f)
        with open(cover_path, "wb") as f:
            shutil.copyfileobj(cover.file, f)
    except Exception as e:
        raise HTTPException(500, f"Ошибка сохранения: {str(e)}")

    # 🎯 Автоматически определяем длительность и BPM
    duration_seconds, bpm, created_date = analyze_mp3(mp3_path)

    # Если длительность не удалось определить – можно вернуть ошибку
    if duration_seconds == 0:
        # Удаляем уже сохранённые файлы, чтобы не мусорить
        mp3_path.unlink(missing_ok=True)
        cover_path.unlink(missing_ok=True)
        raise HTTPException(400, "Не удалось прочитать длительность трека (файл повреждён?)")

    # Создаём запись в БД
    track_data = {
        "title": title,
        "cover_url": f"/storage/covers/{cover_filename}",
        "duration_seconds": int(duration_seconds),  # округляем до секунд
        "created_date": datetime.utcnow(),
        "mp3_file_url": f"/storage/tracks/{mp3_filename}",
        "price": price,
        "plays": 0,
        "bpm": bpm,          # может быть None, если BPM не определился
        "genre_id": genre_id,
        "author_id": author_id,
    }
    track = Track(**track_data)
    session.add(track)
    await session.commit()
    await session.refresh(track)




@router.get("/stats/user-metrics", response_model=UserMetricsResponse)
async def get_user_metrics(
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_user_metrics()

@router.get("/stats/user-daily-registrations", response_model=list[DailyUserRegistrationsResponse])
async def get_daily_registrations(
    days: int = 30,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_daily_user_registrations(days)

@router.get("/stats/user-daily-purchases", response_model=list[DailyUserPurchasesResponse])
async def get_daily_purchases_activity(
    days: int = 30,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_daily_user_purchases(days)

@router.get("/stats/user-top-buyers", response_model=list[TopBuyerResponse])
async def get_top_buyers(
    limit: int = 10,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_top_buyers(limit)

@router.get("/stats/user-top-listeners", response_model=list[TopListenerResponse])
async def get_top_listeners(
    limit: int = 10,
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_top_listeners(limit)

@router.get("/stats/user-role-distribution", response_model=list[UserRoleDistributionResponse])
async def get_role_distribution(
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
    current_user: User = Depends(get_current_admin)
):
    return await stats_service.get_user_role_distribution()


@router.get("/tracks/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    admin: User = Depends(get_current_admin),
    track_service: TrackService = Depends(get_track_service)
):

    track = await track_service.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    return track