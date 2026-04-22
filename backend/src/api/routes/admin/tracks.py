from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from schemas.track import TrackResponse
from core.repositories.track import TrackRepository
from core.services.track import TrackService
from core.services.file_service import FileService
from api.dependencies import get_db_session, get_current_admin, get_file_service, get_track_service
from database.models import Track, User
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/admin/tracks", tags=["admin tracks"])

@router.post("/", status_code=201)
async def create_track(
    title: str = Form(..., min_length=1, max_length=200),
    price: float = Form(..., ge=0),
    genre_id: int = Form(...),
    author_id: int = Form(...),
    duration_seconds: Optional[int] = Form(None, ge=0),
    created_date: Optional[datetime] = Form(None),
    cover: Optional[UploadFile] = File(None),
    mp3_file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    track_service: TrackService = Depends(get_track_service)  # Используем зависимость TrackService
):
    """Создание трека с загрузкой файлов"""
    # Сохраняем файлы
    cover_url = None
    if cover:
        cover_url = await track_service.file_service.save_cover(cover)
    print(author_id)
    mp3_url = await track_service.file_service.save_track(mp3_file)
    
    # Создаём трек в БД через сервис
    track = await track_service.create_track(
        title=title,
        price=price,
        genre_id=genre_id,
        user=author_id,
        duration_seconds=duration_seconds,
        created_date=created_date,
        cover_url=cover_url,
        mp3_file_url=mp3_url
    )
    
    # Не нужно использовать session.merge, так как track был создан через сервис и уже сохранён
    return {"message": "Track created successfully"}

    

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None, ge=0),
    genre_id: Optional[int] = Form(None),
    author_id: Optional[int] = Form(None),
    duration_seconds: Optional[int] = Form(None, ge=0),
    created_date: Optional[datetime] = Form(None),
    cover: Optional[UploadFile] = File(None),
    mp3_file: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    """Обновление трека"""
    repo = TrackRepository(session)
    service = TrackService(repo, file_service)
    
    # Собираем данные для обновления
    update_data = {}
    if title is not None:
        update_data['title'] = title
    if price is not None:
        update_data['price'] = price
    if genre_id is not None:
        update_data['genre_id'] = genre_id
    if author_id is not None:
        update_data['author_id'] = author_id
    if duration_seconds is not None:
        update_data['duration_seconds'] = duration_seconds
    if created_date is not None:
        update_data['created_date'] = created_date
    
    track = await service.update_track(track_id, update_data, cover, mp3_file)
    if not track:
        raise HTTPException(404, "Трек не найден")
    return track

@router.delete("/{track_id}", status_code=204)
async def delete_track(
    track_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    repo = TrackRepository(session)
    service = TrackService(repo, file_service)
    deleted = await service.delete_track(track_id)
    if not deleted:
        raise HTTPException(404, "Трек не найден")