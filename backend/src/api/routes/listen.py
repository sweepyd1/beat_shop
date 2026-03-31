from fastapi import APIRouter, Depends, status
from schemas.listen import ListenResponse
from api.dependencies import get_current_user, get_listen_service
from core.services.listen import ListenService
from database.models import User

router = APIRouter(prefix="/listen", tags=["listen"])


@router.post("/{track_id}", response_model=ListenResponse, status_code=status.HTTP_200_OK)
async def log_listen(
    track_id: int,
    service: ListenService = Depends(get_listen_service),
    current_user: User = Depends(get_current_user),
    count_today_only: bool = True  
):
    """
    Записать прослушивание трека.
    
    Вызывается с фронта при воспроизведении трека.
    """
    result = await service.log_listen(
        user_id=current_user.id,
        track_id=track_id,
        count_today_only=count_today_only
    )
    return result