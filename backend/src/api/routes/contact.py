from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.services.contact import ContactMessageService
from core.repositories.contact import ContactMessageRepository
from schemas.contact import ContactMessageCreate, ContactMessageResponse
from api.dependencies import get_current_admin, get_db_session
from core.services.auth import AuthService
from api.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

async def get_contact_service(db: AsyncSession = Depends(get_db_session)):
    repo = ContactMessageRepository(db)
    return ContactMessageService(repo)

@router.post("/", status_code=201)
async def send_contact_message(
    request: Request,
    data: ContactMessageCreate,
    auth_service: AuthService = Depends(get_auth_service),
    service: ContactMessageService = Depends(get_contact_service),
):
    """
    Публичный эндпоинт для отправки сообщения.
    Если пользователь авторизован, его ID будет привязан к сообщению.
    """
    user_id = None
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            user = await auth_service.get_user_from_token(access_token)
            if user:
                user_id = user.id
        except:
            pass  # не фатально, сообщение всё равно сохранится
    result = await service.send_message(data, user_id)
    return result

# Ниже – дополнительные админские эндпоинты (опционально)
@router.get("/admin/", response_model=list[ContactMessageResponse])
async def get_all_messages(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),  # ← получаем пользователя
    service: ContactMessageService = Depends(get_contact_service),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    messages = await service.get_messages(skip, limit, unread_only)
    return messages

@router.patch("/admin/{message_id}/read", status_code=200)
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    service: ContactMessageService = Depends(get_contact_service),
):
  
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    success = await service.mark_read(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "marked as read"}