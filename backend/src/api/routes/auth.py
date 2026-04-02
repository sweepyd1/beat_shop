from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import UserCreate, UserResponse
from core.services.auth import AuthService
from api.dependencies import get_auth_service
from database.models import User
from typing import Any

router = APIRouter(prefix="/auth", tags=["auth"])

# Конфигурация кук (в реальном проекте вынесите в .env)
ACCESS_TOKEN_EXPIRE = 360000  # 1 час
REFRESH_TOKEN_EXPIRE = 86400 * 7  # 7 дней
COOKIE_SECURE = False  # В production установите True (для HTTPS)
COOKIE_SAMESITE = "lax"

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Установка httpOnly кук с токенами"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE,
    )

def clear_auth_cookies(response: Response):
    """Удаление кук (выход)"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя и автоматический вход"""
    user = await auth_service.register(user_data)
    # Генерируем токены и устанавливаем куки
    tokens = await auth_service.create_tokens(user.id)  # добавим этот метод в AuthService
    set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход в систему, установка кук"""
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    tokens = await auth_service.create_tokens(user.id)
    set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return {"message": "Успешный вход", "user": user}  # вернём пользователя для фронта


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access токена по refresh токену из куки"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    new_tokens = await auth_service.refresh_token(refresh_token)
    set_auth_cookies(response, new_tokens["access_token"], new_tokens["refresh_token"])
    return {"message": "Токен обновлен"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    # 1. Пробуем access_token
    user = await auth_service.get_user_from_token(access_token) if access_token else None
    if user:
        return user

    # 2. Access не подошёл (истёк/невалиден) – пробуем обновить по refresh
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No valid tokens")

    try:
        new_tokens = await auth_service.refresh_token(refresh_token)
        # Обновляем куки
        set_auth_cookies(response, new_tokens["access_token"], new_tokens["refresh_token"])
        # Теперь получаем пользователя из нового access_token
        user = await auth_service.get_user_from_token(new_tokens["access_token"])
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except Exception:
        # Рефреш невалиден или истёк
        clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Session expired, please login again")

@router.post("/logout")
async def logout(response: Response):
    """Выход - очищаем куки"""
    clear_auth_cookies(response)
    return {"message": "Вы вышли из системы"}