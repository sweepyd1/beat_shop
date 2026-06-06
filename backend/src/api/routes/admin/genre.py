import os
from pathlib import Path
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import STORAGE_PATH  
from database.models import User
from schemas.genre import GenreCreate, GenreUpdate, GenreResponse
from core.repositories.genre import GenreRepository
from core.services.genre import GenreService  
from api.dependencies import get_db_session, get_current_admin

router = APIRouter(prefix="/admin/genres", tags=["admin genres"])

@router.post("/", response_model=GenreResponse, status_code=201)
async def create_genre(
    genre_data: GenreCreate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    return await service.create_genre(genre_data)

@router.put("/{genre_id}", response_model=GenreResponse)
async def update_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    genre = await service.update_genre(genre_id, genre_data)
    if not genre:
        raise HTTPException(404, "Жанр не найден")
    return genre

@router.delete("/{genre_id}", status_code=204)
async def delete_genre(
    genre_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    deleted = await service.delete_genre(genre_id)
    if not deleted:
        raise HTTPException(404, "Жанр не найден")

# GET /admin/genres/ – список всех жанров (для админки)
@router.get("/", response_model=list[GenreResponse])
async def get_all_genres_admin(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    return await service.repo.get_all()   # или service.get_all_genres_admin()

@router.post("/upload-image", response_model=dict)
async def upload_genre_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),   # проверяем, что администратор
):
    # 1. Проверяем тип файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только изображения"
        )
    
    # 2. Проверяем расширение
    ext = Path(file.filename).suffix.lower()
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат изображения. Разрешены: jpg, jpeg, png, gif, webp"
        )
    
    # 3. Генерируем уникальное имя
    filename = f"genre_{uuid4().hex}{ext}"
    
    # 4. Определяем папку для сохранения (в корневой storage)
    upload_dir = STORAGE_PATH / "genre_photos"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    
    # 5. Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 6. Возвращаем относительный URL (статическая папка смонтирована как /storage)
    image_url = f"/storage/genre_photos/{filename}"
    return {"image_url": image_url}