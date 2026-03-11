from fastapi import APIRouter, Depends


from core.services.genre import GenreService

from api.dependencies import get_genre_service

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/")
async def get_genres(service: GenreService = Depends(get_genre_service)):
    return await service.get_all_genres()