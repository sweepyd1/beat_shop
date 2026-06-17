
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.services.auth import AuthService
from schemas.user import UserCreate, UserLogin
from database.models import UserRole


class TestAuthRegistration:
    """Тесты регистрации пользователей"""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self):
        """Успешная регистрация нового пользователя"""
        mock_repo = AsyncMock()
        mock_repo.check_exists.return_value = False
        mock_repo.create.return_value = AsyncMock(
            id=1, 
            login='testuser', 
            email='test@example.com', 
            password_hash='hashed_password',
            is_active=True,
            registered_at=None,
            role='user',
            avatar_url=None
        )
        
        mock_author_repo = AsyncMock()
        
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        user_data = UserCreate(
            full_name='Test User',
            login='testuser',
            email='test@example.com',
            password='securepass123',
            role='user'
        )
        
        result = await service.register(user_data)
        
        assert result.id == 1
        assert result.login == 'testuser'
        mock_repo.check_exists.assert_called_once_with('testuser', 'test@example.com')
        mock_repo.create.assert_called_once()
        mock_author_repo.create.assert_not_called()
        print("✅ Тест успешной регистрации пройден")

    @pytest.mark.asyncio
    async def test_register_duplicate_user(self):
        """Регистрация пользователя с существующим логином/email"""
        mock_repo = AsyncMock()
        mock_repo.check_exists.return_value = True
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        user_data = UserCreate(
            full_name='Test User',
            login='existing_user',
            email='existing@example.com',
            password='securepass123',
            role='user'
        )
        
        with pytest.raises(Exception) as exc_info:
            await service.register(user_data)
        
        assert exc_info.value.status_code == 400
        print("✅ Тест дубликата пользователя пройден")

    @pytest.mark.asyncio
    async def test_register_author_creates_profile(self):
        """Регистрация автора создает профиль автора"""
        mock_repo = AsyncMock()
        mock_repo.check_exists.return_value = False
        mock_repo.create.return_value = AsyncMock(
            id=2, 
            login='author1', 
            email='author@example.com', 
            password_hash='hashed',
            is_active=True,
            registered_at=None,
            role='author',
            avatar_url=None
        )
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        user_data = UserCreate(
            full_name='Author Name',
            login='author1',
            email='author@example.com',
            password='securepass123',
            role='author'
        )
        
        result = await service.register(user_data)
        
        assert result.id == 2
        mock_author_repo.create.assert_called_once()
        print("✅ Тест регистрации автора пройден")


class TestAuthLogin:
    """Тесты авторизации"""
    
    @pytest.mark.asyncio
    async def test_login_success(self):
        """Успешный вход пользователя"""
        mock_repo = AsyncMock()
        mock_user = AsyncMock(
            id=1,
            login='testuser',
            email='test@example.com',
            password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.2f2f2f2f2f2f',
            is_active=True,
            role='user',
            avatar_url=None
        )
        mock_repo.get_by_login.return_value = mock_user
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        
        with patch.object(service, 'verify_password', return_value=True):
            result = await service.login(UserLogin(login='testuser', password='password123'))
        
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'bearer'
        print("✅ Тест успешного входа пройден")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Вход с несуществующим пользователем"""
        mock_repo = AsyncMock()
        mock_repo.get_by_login.return_value = None
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        with pytest.raises(Exception) as exc_info:
            await service.login(UserLogin(login='nonexistent', password='password123'))
        
        assert exc_info.value.status_code == 401
        print("✅ Тест входа с несуществующим пользователем пройден")

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Вход с неправильным паролем"""
        mock_repo = AsyncMock()
        mock_user = AsyncMock(
            id=1,
            login='testuser',
            password_hash='hashed_password',
            is_active=True
        )
        mock_repo.get_by_login.return_value = mock_user
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        with patch.object(service, 'verify_password', return_value=False):
            with pytest.raises(Exception) as exc_info:
                await service.login(UserLogin(login='testuser', password='wrongpassword'))
        
        assert exc_info.value.status_code == 401
        print("✅ Тест входа с неправильным паролем пройден")

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """Вход заблокированного пользователя"""
        mock_repo = AsyncMock()
        mock_user = AsyncMock(
            id=1,
            login='testuser',
            password_hash='hashed_password',
            is_active=False
        )
        mock_repo.get_by_login.return_value = mock_user
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        with patch.object(service, 'verify_password', return_value=True):
            with pytest.raises(Exception) as exc_info:
                await service.login(UserLogin(login='testuser', password='password123'))
        
        assert exc_info.value.status_code == 403
        print("✅ Тест входа заблокированного пользователя пройден")


class TestTokenOperations:
    """Тесты работы с токенами"""
    
    def test_create_access_token(self):
        """Создание access токена"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        token = service.create_access_token(user_id=123)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
        print("✅ Тест создания access токена пройден")

    def test_create_refresh_token(self):
        """Создание refresh токена"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        token = service.create_refresh_token(user_id=123)
        
        assert token is not None
        assert isinstance(token, str)
        print("✅ Тест создания refresh токена пройден")

    @pytest.mark.asyncio
    async def test_verify_valid_token(self):
        """Проверка валидного токена"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        token = service.create_access_token(user_id=42)
        user_id = await service.verify_token(token, token_type="access")
        
        assert user_id == 42
        print("✅ Тест проверки валидного токена пройден")

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self):
        """Проверка невалидного токена"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        user_id = await service.verify_token("invalid_token_xyz", token_type="access")
        
        assert user_id is None
        print("✅ Тест проверки невалидного токена пройден")

    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self):
        """Проверка токена с неправильным типом"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        access_token = service.create_access_token(user_id=42)
        
        result = await service.verify_token(access_token, token_type="refresh")
        
        assert result is None
        print("✅ Тест проверки токена с неправильным типом пройден")


class TestPasswordHashing:
    """Тесты хеширования паролей"""
    
    def test_password_hashing(self):
        """Хеширование пароля"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        password = "my_secure_password123"
        hashed = service.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith('$')
        print("✅ Тест хеширования пароля пройден")

    def test_password_verification(self):
        """Проверка пароля"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        password = "my_secure_password123"
        hashed = service.get_password_hash(password)
        
        assert service.verify_password(password, hashed) is True
        assert service.verify_password("wrong_password", hashed) is False
        print("✅ Тест проверки пароля пройден")

    def test_long_password_truncation(self):
        """Обработка длинного пароля (ограничение bcrypt 72 байта)"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        
        long_password = "a" * 100
        hashed = service.get_password_hash(long_password)
        
        assert hashed is not None
        assert len(hashed) > 0
        print("✅ Тест обработки длинного пароля пройден")


class TestTokenRefresh:
    """Тесты обновления токенов"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Успешное обновление токена"""
        mock_repo = AsyncMock()
        mock_user = AsyncMock(
            id=99,
            is_active=True,
            login='testuser'
        )
        mock_repo.get.return_value = mock_user
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        refresh_token = service.create_refresh_token(user_id=99)
        
        result = await service.refresh_token(refresh_token)
        
        assert 'access_token' in result
        assert 'refresh_token' in result
        print("✅ Тест успешного обновления токена пройден")

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self):
        """Обновление с невалидным токеном"""
        mock_repo = AsyncMock()
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        with pytest.raises(Exception) as exc_info:
            await service.refresh_token("invalid_refresh_token")
        
        assert exc_info.value.status_code == 401
        print("✅ Тест обновления с невалидным токеном пройден")

    @pytest.mark.asyncio
    async def test_refresh_inactive_user(self):
        """Обновление токена заблокированным пользователем"""
        mock_repo = AsyncMock()
        mock_user = AsyncMock(
            id=99,
            is_active=False
        )
        mock_repo.get.return_value = mock_user
        
        mock_author_repo = AsyncMock()
        service = AuthService(repo=mock_repo, author_repo=mock_author_repo)
        
        refresh_token = service.create_refresh_token(user_id=99)
        
        with pytest.raises(Exception) as exc_info:
            await service.refresh_token(refresh_token)
        
        assert exc_info.value.status_code == 401
        print("✅ Тест обновления токена заблокированным пользователем пройден")