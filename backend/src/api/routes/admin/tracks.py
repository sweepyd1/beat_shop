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

# @router.post("/", status_code=201)



















    











    



    

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None, ge=0),
    genre_id: Optional[int] = Form(None),
    author_id: Optional[int] = Form(None),
    duration_seconds: Optional[int] = Form(None, ge=0),
    bpm: Optional[int] = Form(None),
    cover: Optional[UploadFile] = File(None),
    mp3_file: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    track_service: TrackService = Depends(get_track_service)   
):
    """Обновление трека (администратором)"""
    update_data = {}
    if title is not None: update_data['title'] = title
    if price is not None: update_data['price'] = price
    if genre_id is not None: update_data['genre_id'] = genre_id
    if author_id is not None: update_data['author_id'] = author_id
    if duration_seconds is not None: update_data['duration_seconds'] = duration_seconds
    if bpm is not None: update_data['bpm'] = bpm

    track = await track_service.update_track(track_id, update_data, cover, mp3_file)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    return track


@router.delete("/{track_id}", status_code=204)
async def delete_track(
    track_id: int,
    admin: User = Depends(get_current_admin),
    track_service: TrackService = Depends(get_track_service)   
):
    """Удаление трека (администратором)"""
    deleted = await track_service.delete_track(track_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Трек не найден")
    