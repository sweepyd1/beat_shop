from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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