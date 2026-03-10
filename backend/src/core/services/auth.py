# src/core/services/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from database.models import User
from config import cfg
from core.repositories.user import UserRepository
from schemas.user import UserCreate, UserLogin, TokenPayload


# Настраиваем CryptContext с правильными параметрами
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    bcrypt__rounds=cfg.security.bcrypt_rounds  # используем из конфига
)


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    # ---------- Хеширование паролей ----------
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля с автоматическим усечением"""
        # bcrypt имеет ограничение 72 байта, обрезаем если нужно
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля с автоматическим усечением"""
        # bcrypt имеет ограничение 72 байта, обрезаем если нужно
        if isinstance(password, str):
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)

    # ---------- JWT токены ----------
    def create_access_token(self, user_id: int) -> str:
        """Создание access токена"""
        expires_delta = timedelta(days=cfg.security.access_token_expire_minutes)
        expire = datetime.utcnow() + expires_delta
        
        payload = TokenPayload(
            sub=str(user_id),
            exp=int(expire.timestamp()),
            type="access"
        )
        
        return jwt.encode(
            payload.model_dump(),
            cfg.security.jwt_secret_key,
            algorithm=cfg.security.jwt_algorithm
        )

    def create_refresh_token(self, user_id: int) -> str:
        """Создание refresh токена"""
        expires_delta = timedelta(days=cfg.security.refresh_token_expire_days)
        expire = datetime.utcnow() + expires_delta
        
        payload = TokenPayload(
            sub=str(user_id),
            exp=int(expire.timestamp()),
            type="refresh"
        )
        
        return jwt.encode(
            payload.model_dump(),
            cfg.security.jwt_secret_key,
            algorithm=cfg.security.jwt_algorithm
        )

    async def verify_token(self, token: str, token_type: str = "access") -> Optional[int]:
        """Проверка токена и возврат user_id"""
        try:
            payload = jwt.decode(
                token,
                cfg.security.jwt_secret_key,
                algorithms=[cfg.security.jwt_algorithm]
            )
            
            # Проверяем тип токена
            if payload.get("type") != token_type:
                return None
            
            user_id = int(payload.get("sub"))
            return user_id
            
        except (JWTError, ValueError, TypeError):
            return None

    # ---------- Бизнес-логика ----------
    async def register(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""
        # Проверяем, не занят ли логин или email
        exists = await self.repo.check_exists(user_data.login, user_data.email)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином или email уже существует"
            )
        
        # Хешируем пароль и создаём пользователя
        hashed_password = self.get_password_hash(user_data.password)
        user = await self.repo.create(
            full_name=user_data.full_name,
            login=user_data.login,
            email=user_data.email,
            password_hash=hashed_password
        )
        
        return user

    async def login(self, login_data: UserLogin) -> dict:
        """Вход пользователя"""
        # Ищем пользователя по логину или email
        user = await self.repo.get_by_login(login_data.login)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Проверяем пароль
        if not self.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Проверяем активен ли пользователь
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь заблокирован"
            )
        
        # Создаём токены
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        """Обновление access токена по refresh токену"""
        user_id = await self.verify_token(refresh_token, token_type="refresh")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен"
            )
        
        # Проверяем, что пользователь существует
        user = await self.repo.get(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или заблокирован"
            )
        
        # Создаём новые токены
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }