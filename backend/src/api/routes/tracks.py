import os
from pathlib import Path
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from core.services.purchase_service import PurchaseService
from core.repositories.track import TrackRepository
from core.services.auth import AuthService
from database.models import User
from schemas.track import TrackResponse, TrackCreate, TrackUpdate
from core.services.track import TrackService
from api.dependencies import get_auth_service, get_purchase_service, get_track_service
from api.dependencies import analyze_mp3
router = APIRouter(prefix="/tracks", tags=["tracks"])

@router.get("/me", response_model=List[TrackResponse])
async def get_my_tracks(
    request:Request,
    track_service: TrackService = Depends(get_track_service),
    auth_service: AuthService = Depends(get_auth_service),

):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await auth_service.get_user_from_token(access_token)
    print(user.role.name)
    if user.role.name != "author":
        raise HTTPException(status_code=403, detail="Только авторы могут просматривать свои треки")
    tracks = await track_service.get_tracks_by_user(user.id)
    return tracks
@router.get("/search", response_model=list[TrackResponse])
async def search_tracks(
    query: Optional[str] = Query(None, description="Поисковый запрос"),
    genre_ids: Optional[List[int]] = Query(None, description="ID жанров"),
    bpm_min: Optional[int] = Query(None, ge=0, description="Минимальный BPM"),
    bpm_max: Optional[int] = Query(None, ge=0, description="Максимальный BPM"),
    duration_min: Optional[int] = Query(None, ge=0, description="Минимальная длительность в секундах"),
    duration_max: Optional[int] = Query(None, ge=0, description="Максимальная длительность в секундах"),
    sort_by: str = Query("popular", pattern="^(popular|newest|price_asc|price_desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: TrackService = Depends(get_track_service)
):
    """Поиск треков с фильтрацией и сортировкой"""
    tracks = await service.search_tracks(
        query=query,
        genre_ids=genre_ids,
        bpm_min=bpm_min,
        bpm_max=bpm_max,
        duration_min=duration_min,
        duration_max=duration_max,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )
    return tracks
@router.get("/", response_model=list[TrackResponse])
async def get_tracks(
    skip: int = 0,
    limit: int = 100,
    service: TrackService = Depends(get_track_service)
):
    tracks = await service.repo.get_all(skip=skip, limit=limit)
    return tracks
@router.get("/popular", response_model=list[TrackResponse])
async def popular_tracks(
    limit: int = Query(10, ge=1, le=50),
    service: TrackService = Depends(get_track_service)
):
    """Возвращает популярные треки (по убыванию plays)."""
    tracks = await service.get_popular_tracks(limit)
    return tracks

@router.get("/new", response_model=list[TrackResponse])
async def new_tracks(
    limit: int = Query(10, ge=1, le=50),
    service: TrackService = Depends(get_track_service)
):
    """Возвращает новые треки (по убыванию added_date)."""
    tracks = await service.get_new_tracks(limit)
    return tracks

@router.get("/trends", response_model=list[TrackResponse])
async def get_trends(
    period: str = Query("week", pattern="^(day|week|month)$", description="Период для трендов"),
    limit: int = Query(10, ge=1, le=50),
    service: TrackService = Depends(get_track_service)
):
    """
    Возвращает трендовые треки за указанный период.
    Тренды рассчитываются на основе количества прослушиваний и продаж.
    """
    from datetime import datetime, timedelta, timezone
    
    # Определяем дату начала периода
    now = datetime.now(timezone.utc)
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    else:  # month
        start_date = now - timedelta(days=30)
    
    trends = await service.repo.get_trends(start_date=start_date, limit=limit)
    return trends


@router.post("/")
async def create_track(
    request: Request,
    title: str = Form(..., min_length=1, max_length=200),
    genre_id: int = Form(...),
    price: float = Form(..., ge=0),
    cover: UploadFile = File(...),
    mp3: UploadFile = File(...),
    auth_service: AuthService = Depends(get_auth_service),
    track_service: TrackService = Depends(get_track_service)
):
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await auth_service.get_user_from_token(access_token)
    """Создание нового трека (только для авторов)"""
    mp3_content = await mp3.read()
    mp3_filename = mp3.filename or "track.mp3"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(mp3_content)
        tmp_path = Path(tmp_file.name)
    try:
        duration, bpm = analyze_mp3(tmp_path)
    finally:
        # 🧹 Удаляем временный файл
        if tmp_path.exists():
            tmp_path.unlink()

    track = await track_service.create_track(
        user=user,
        title=title,
        genre_id=genre_id,
        price=price,
        cover=cover,
        mp3=mp3,
        bpm=bpm,
        duration=duration
    )
    


@router.get("/{track_id}/download")
async def download_track(
    request: Request,
    track_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    track_service: TrackService = Depends(get_track_service),
    purchase_service: PurchaseService = Depends(get_purchase_service)
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await auth_service.get_user_from_token(access_token)
    
    track = await track_service.get_track(track_id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
   
    purchases = await purchase_service.get_user_purchases(user.id)
    if not any(p.track_id == track_id for p in purchases):
        raise HTTPException(status_code=403, detail="Вы не приобрели этот трек")
    if not track.mp3_file_url:
        raise HTTPException(status_code=404, detail="Файл трека не найден")

    file_path = track.mp3_file_url.lstrip("/")  # убираем ведущий слеш
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл трека отсутствует на сервере")

    filename = f"{track.id}_{track.title.replace(' ', '_')}.mp3"
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

@router.get("/{track_id}/stream")
async def stream_track(
    track_id: int,
    service: TrackService = Depends(get_track_service)
):
    track = await service.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    
    file_path = track.mp3_file_url  
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg", filename=f"{track.title}.mp3")

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    track_data: TrackUpdate,
    service: TrackService = Depends(get_track_service)
):
    track = await service.update_track(track_id, track_data)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.delete("/{track_id}", status_code=204)
async def delete_track(
    track_id: int,
    service: TrackService = Depends(get_track_service)
):
    deleted = await service.delete_track(track_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Track not found")

@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    service: TrackService = Depends(get_track_service)
):
    track = await service.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track