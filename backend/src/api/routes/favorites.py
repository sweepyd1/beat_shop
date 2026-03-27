from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from core.services.favorite import FavoriteService
from schemas.favorite import FavoriteResponse
from api.dependencies import get_current_user, get_favorite_service
from database.models import User

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Получить список избранных треков текущего пользователя"""
    
    favorites = await service.get_user_favorites(current_user.id)
    return favorites

@router.post("/{track_id}", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    track_id: int,
    service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    print(current_user)
    """Добавить трек в избранное"""

    await service.add_favorite(current_user.id, track_id)
    return {"message": "Track added to favorites"}

@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    track_id: int,
    service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Удалить трек из избранного"""
    deleted = await service.remove_favorite(current_user.id, track_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return