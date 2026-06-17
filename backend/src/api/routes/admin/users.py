from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from passlib.hash import bcrypt
from sqlalchemy import select

from core.services.auth import AuthService
from schemas.favorite import FavoriteResponse
from schemas.purchase import PurchaseResponse
from schemas.subscription import SubscriptionResponse
from database.models import User, UserRole
from schemas.user import UserResponse, UserCreate
from api.dependencies import get_auth_service, get_db_session, get_current_admin, get_file_service
from core.services.file_service import FileService
from core.repositories.user import UserRepository

router = APIRouter(prefix="/admin/users", tags=["admin users"])

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    """Список всех пользователей"""
    repo = UserRepository(session)
    users = await repo.get_all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    """Получить одного пользователя"""
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    full_name: str = Form(...),
    login: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: UserRole = Form(UserRole.user),
    avatar: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Создание нового пользователя администратором"""
    repo = UserRepository(session)

    
    exists = await repo.check_exists(login, email)
    if exists:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином или email уже существует")

    
    avatar_url = None
    if avatar:
        avatar_url = await file_service.save_avatar(avatar)

    
    user_data = {
        "full_name": full_name,
        "login": login,
        "email": email,
        "password_hash": auth_service.get_password_hash(password),
        "role": role,
        "avatar_url": avatar_url,
        "is_active": True,
        "is_admin": (role == UserRole.admin)
    }
    user = await repo.create(**user_data)
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    role: Optional[UserRole] = Form(None),
    is_active: Optional[bool] = Form(None),
    password: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(get_file_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление данных пользователя"""
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if email is not None:
        update_data["email"] = email
    if role is not None:
        update_data["role"] = role
        update_data["is_admin"] = (role == UserRole.admin)
    if is_active is not None:
        update_data["is_active"] = is_active
    if password is not None and password.strip():
        update_data["password_hash"] = auth_service.get_password_hash(password)

    
    if avatar:
        if user.avatar_url:
            file_service.delete_file(user.avatar_url)
        update_data["avatar_url"] = await file_service.save_avatar(avatar)

    updated_user = await repo.update(user_id, **update_data)
    return updated_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление пользователя"""
    repo = UserRepository(session)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
class UserProfileResponse(UserResponse):
    purchases_count: int
    favorites_count: int
    subscriptions_count: int
    total_spent: float
    last_listen: Optional[datetime] = None
    top_genres: list[dict] = []   
    recent_purchases: list[PurchaseResponse] = []
    recent_favorites: list[FavoriteResponse] = []
    subscriptions: list[SubscriptionResponse] = []

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session)
):
    repo = UserRepository(session)
    user = await repo.get_with_relations(user_id)
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")

    
    purchases = user.purchases
    favorites = user.favorites
    subs = user.subscriptions

    total_spent = sum(p.amount for p in purchases)
    last_listen = None
    if user.interactions:
        listen_interactions = [i for i in user.interactions if i.interaction_type == 'listen']
        if listen_interactions:
            last_listen = max(i.timestamp for i in listen_interactions)

    
    genre_counter = {}
    for p in purchases:
        genre = p.track.genre.name if p.track.genre else 'Без жанра'
        genre_counter[genre] = genre_counter.get(genre, 0) + 1
    
    for i in user.interactions:
        if i.interaction_type == 'listen':
            genre = i.track.genre.name if i.track.genre else 'Без жанра'
            genre_counter[genre] = genre_counter.get(genre, 0) + 1

    top_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    top_genres = [{"genre_name": g, "count": c} for g, c in top_genres]

    
    recent_purchases = sorted(purchases, key=lambda x: x.purchase_date, reverse=True)[:5]
    recent_favorites = sorted(favorites, key=lambda x: x.added_at, reverse=True)[:5]

    return {
        **user.__dict__,
        "purchases_count": len(purchases),
        "favorites_count": len(favorites),
        "subscriptions_count": len(subs),
        "total_spent": total_spent,
        "last_listen": last_listen,
        "top_genres": top_genres,
        "recent_purchases": [PurchaseResponse.from_orm(p) for p in recent_purchases],
        "recent_favorites": [FavoriteResponse.from_orm(f) for f in recent_favorites],
        "subscriptions":[],
    }