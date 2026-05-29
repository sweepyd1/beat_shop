from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from schemas.genre import GenreCreate, GenreUpdate, GenreResponse
from core.repositories.genre import GenreRepository
from core.services.genre import GenreService  
from api.dependencies import get_db_session, get_current_admin, get_file_service
from core.services.file_service import FileService

router = APIRouter(prefix="/admin/genres", tags=["admin genres"])

@router.post("/", response_model=GenreResponse, status_code=201)
async def create_genre(
    name: str,
    photo: UploadFile | None = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    
    photo_url = None
    if photo:
        photo_url = await file_service.save_genre_photo(photo)
    
    genre_data = GenreCreate(name=name, photo_url=photo_url)
    return await service.create_genre(genre_data)

@router.put("/{genre_id}", response_model=GenreResponse)
async def update_genre(
    genre_id: int,
    name: str | None = None,
    photo: UploadFile | None = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    repo = GenreRepository(session)
    service = GenreService(repo)
    
    update_data = {}
    if name is not None:
        update_data['name'] = name
    
    if photo:
        photo_url = await file_service.save_genre_photo(photo)
        update_data['photo_url'] = photo_url
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    
    genre = await service.update_genre(genre_id, GenreUpdate(**update_data))
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