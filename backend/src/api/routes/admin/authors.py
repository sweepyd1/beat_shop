from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from schemas.author import AuthorCreate, AuthorUpdate, AuthorResponse
from core.services.author import AuthorService
from core.repositories.author import AuthorRepository
from api.dependencies import get_db_session, get_current_admin, get_file_service
from core.services.file_service import FileService

router = APIRouter(prefix="/admin/authors", tags=["admin authors"])

@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    full_name: str = Form(..., min_length=1, max_length=150),
    bio: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    """Создание автора (только для админа)"""
    repo = AuthorRepository(session)
    service = AuthorService(repo, file_service)  
    
    author_data = AuthorCreate(full_name=full_name, bio=bio)
    author = await service.create_author(author_data, photo)
    return author

@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    full_name: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    """Обновление автора"""
    repo = AuthorRepository(session)
    service = AuthorService(repo, file_service)
    
    update_data = {}
    if full_name is not None:
        update_data['full_name'] = full_name
    if bio is not None:
        update_data['bio'] = bio
    
    author_update = AuthorUpdate(**update_data)
    author = await service.update_author(author_id, author_update, photo)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return author

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service)
):
    """Удаление автора"""
    repo = AuthorRepository(session)
    service = AuthorService(repo, file_service)
    
    deleted = await service.delete_author(author_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Автор не найден")