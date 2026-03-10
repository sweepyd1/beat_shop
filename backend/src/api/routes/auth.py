# src/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from core.services.auth import AuthService
from api.dependencies import get_auth_service, get_current_user
from database.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    user = await auth_service.register(user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Вход в систему.
    
    - **username**: логин или email
    - **password**: пароль
    """
    login_data = UserLogin(login=form_data.username, password=form_data.password)
    result = await auth_service.login(login_data)
    
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access токена"""
    return await auth_service.refresh_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Информация о текущем пользователе"""
    return current_user


@router.post("/logout")
async def logout():
    """
    Выход из системы.
    На клиенте просто удаляем токены.
    """
    return {"message": "Успешный выход"}