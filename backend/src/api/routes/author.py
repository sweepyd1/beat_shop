from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from schemas.author import AuthorResponse, AuthorDetailResponse
from core.repositories.author import AuthorRepository
from api.dependencies import get_current_user, get_db_session

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/", response_model=list[AuthorResponse])
async def get_authors(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    repo = AuthorRepository(session)
    authors = await repo.get_all(skip=skip, limit=limit)
    return authors

@router.get("/{author_id}", response_model=AuthorDetailResponse)
async def get_author(
    author_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    repo = AuthorRepository(session)
    author = await repo.get(author_id)
    if not author:
        raise HTTPException(404, "Автор не найден")
    # Подсчёт количества треков
    tracks_count = len(author.tracks) if author.tracks else 0
    response = AuthorDetailResponse.model_validate(author)
    response.tracks_count = tracks_count
    return response

@router.get("/me", response_model=AuthorDetailResponse)
async def get_my_author_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    if current_user.role != "author":
        raise HTTPException(403, "Пользователь не является автором")
    repo = AuthorRepository(session)
    author = await repo.get_by_user_id(current_user.id)
    if not author:
        raise HTTPException(404, "Профиль автора не найден")
    return author