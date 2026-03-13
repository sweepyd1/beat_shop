from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from api.dependencies import get_db_session, get_auth_service
from core.services.auth import AuthService
from core.services.user import UserService
from core.services.purchase import PurchaseService
from core.services.favorite import FavoriteService
from core.services.subscription import SubscriptionService
from core.repositories.user import UserRepository
from core.repositories.purchase import PurchaseRepository
from core.repositories.favorite import FavoriteRepository
from core.repositories.subscription import SubscriptionRepository
from core.services.file_service import FileService
from schemas.user import UserResponse
from schemas.purchase import PurchaseResponse
from schemas.favorite import FavoriteResponse
from schemas.subscription import SubscriptionResponse
from database.models import User

router = APIRouter(prefix="/users", tags=["users"])

# Зависимости для получения сервисов
async def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    repo = UserRepository(session)
    file_service = FileService()
    return UserService(repo, file_service)

async def get_purchase_service(session: AsyncSession = Depends(get_db_session)) -> PurchaseService:
    repo = PurchaseRepository(session)
    return PurchaseService(repo)

async def get_favorite_service(session: AsyncSession = Depends(get_db_session)) -> FavoriteService:
    repo = FavoriteRepository(session)
    return FavoriteService(repo)

async def get_subscription_service(session: AsyncSession = Depends(get_db_session)) -> SubscriptionService:
    repo = SubscriptionRepository(session)
    return SubscriptionService(repo)

# Получение текущего пользователя из куки через AuthService
async def get_current_user_from_cookie(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await auth_service.get_user_from_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user_from_cookie),
    service: UserService = Depends(get_user_service)
):
    # Получаем профиль со связанными данными (подписки и т.д.)
    user = await service.get_profile(current_user.id)
    return user

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user_from_cookie),
    service: UserService = Depends(get_user_service)
):
    update_data = {}
    if full_name is not None:
        update_data['full_name'] = full_name
    if email is not None:
        update_data['email'] = email
    updated = await service.update_profile(current_user.id, update_data, avatar)
    if not updated:
        raise HTTPException(404, "User not found")
    return updated

@router.get("/me/purchases", response_model=list[PurchaseResponse])
async def get_my_purchases(
    current_user: User = Depends(get_current_user_from_cookie),
    service: PurchaseService = Depends(get_purchase_service)
):
    purchases = await service.get_user_purchases(current_user.id)
    return purchases

@router.get("/me/favorites", response_model=list[FavoriteResponse])
async def get_my_favorites(
    current_user: User = Depends(get_current_user_from_cookie),
    service: FavoriteService = Depends(get_favorite_service)
):
    favorites = await service.get_user_favorites(current_user.id)
    return favorites

@router.get("/me/subscriptions", response_model=list[SubscriptionResponse])
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user_from_cookie),
    service: SubscriptionService = Depends(get_subscription_service)
):
    subscriptions = await service.get_user_subscriptions(current_user.id)
    return subscriptions

@router.post("/me/subscriptions/{author_id}")
async def subscribe_to_author(
    author_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    service: SubscriptionService = Depends(get_subscription_service)
):
    await service.subscribe(current_user.id, author_id)
    return {"message": "Subscribed"}

@router.delete("/me/subscriptions/{author_id}")
async def unsubscribe_from_author(
    author_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    service: SubscriptionService = Depends(get_subscription_service)
):
    success = await service.unsubscribe(current_user.id, author_id)
    if not success:
        raise HTTPException(404, "Subscription not found")
    return {"message": "Unsubscribed"}