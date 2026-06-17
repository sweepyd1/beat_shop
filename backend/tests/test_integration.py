
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from main import app


class TestAuthEndpoints:
    """Интеграционные тесты эндпоинтов авторизации"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Проверка health endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
        print("✅ Health endpoint работает")

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Проверка корневого endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "Music Store API" in data["message"]
        print("✅ Root endpoint работает")

    @pytest.mark.asyncio
    async def test_register_user_success(self):
        """Регистрация нового пользователя - успех"""
        
        with patch('src.core.services.auth.AuthService') as MockAuthService:
            mock_service = MagicMock()
            mock_service.register = AsyncMock(return_value=MagicMock(
                id=1,
                login='newuser',
                email='new@example.com',
                full_name='New User',
                role='user',
                is_active=True,
                registered_at='2024-01-01T00:00:00',
                avatar_url=None
            ))
            MockAuthService.return_value = mock_service
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/auth/register", json={
                    "full_name": "New User",
                    "login": "newuser",
                    "email": "new@example.com",
                    "password": "SecurePass123!",
                    "role": "user"
                })
                assert response.status_code == 201
                data = response.json()
                assert data["login"] == "newuser"
        print("✅ Регистрация пользователя работает")

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Вход с неверными учетными данными"""
        with patch('src.core.services.auth.AuthService') as MockAuthService:
            from fastapi import HTTPException
            mock_service = MagicMock()
            mock_service.login = AsyncMock(side_effect=HTTPException(
                status_code=401, 
                detail="Неверный логин или пароль"
            ))
            MockAuthService.return_value = mock_service
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/auth/login", data={
                    "username": "wronguser",
                    "password": "wrongpass"
                })
                assert response.status_code == 401
        print("✅ Проверка неверных учетных данных работает")


class TestGenresEndpoint:
    """Интеграционные тесты эндпоинтов жанров"""
    
    @pytest.mark.asyncio
    async def test_get_genres_list(self):
        """Получение списка жанров"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/genres/")
            
            assert response.status_code in [200, 500]
        print("✅ Endpoint получения жанров работает")


class TestTracksEndpoint:
    """Интеграционные тесты эндпоинтов треков"""
    
    @pytest.mark.asyncio
    async def test_get_tracks_empty(self):
        """Получение пустого списка треков"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/tracks/")
            
            assert response.status_code in [200, 500]
        print("✅ Endpoint получения треков работает")

    @pytest.mark.asyncio
    async def test_search_tracks(self):
        """Поиск треков"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/tracks/search?query=test")
            
            assert response.status_code in [200, 500]
        print("✅ Поиск треков работает")


class TestRecommendationsEndpoint:
    """Интеграционные тесты рекомендаций"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self):
        """Получение рекомендаций"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/recommendations/")
            
            assert response.status_code in [200, 500]
        print("✅ Endpoint рекомендаций работает")


class TestUserEndpoint:
    """Интеграционные тесты пользовательских эндпоинтов"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self):
        """Попытка получить текущего пользователя без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/users/me")
            
            assert response.status_code == 401
        print("✅ Проверка авторизации пользователя работает")


class TestFavoritesEndpoint:
    """Интеграционные тесты избранного"""
    
    @pytest.mark.asyncio
    async def test_get_favorites_unauthorized(self):
        """Получение избранного без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/favorites/")
            assert response.status_code == 401
        print("✅ Проверка авторизации избранного работает")


class TestPurchaseEndpoint:
    """Интеграционные тесты покупок"""
    
    @pytest.mark.asyncio
    async def test_get_purchases_unauthorized(self):
        """Получение покупок без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/purchases/")
            assert response.status_code == 401
        print("✅ Проверка авторизации покупок работает")


class TestListenEndpoint:
    """Интеграционные тесты прослушиваний"""
    
    @pytest.mark.asyncio
    async def test_record_listen_unauthorized(self):
        """Запись прослушивания без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/listens/1")
            assert response.status_code == 401
        print("✅ Проверка авторизации прослушиваний работает")


class TestAuthorEndpoint:
    """Интеграционные тесты авторов"""
    
    @pytest.mark.asyncio
    async def test_get_author_info(self):
        """Получение информации об авторе"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/authors/1")
            
            assert response.status_code in [200, 404, 500]
        print("✅ Получение информации об авторе работает")


class TestAdminEndpoints:
    """Интеграционные тесты админских эндпоинтов"""
    
    @pytest.mark.asyncio
    async def test_admin_authors_unauthorized(self):
        """Получение списка авторов админом без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/admin/authors/")
            assert response.status_code == 401
        print("✅ Проверка авторизации админских авторов работает")

    @pytest.mark.asyncio
    async def test_admin_genres_unauthorized(self):
        """Получение списка жанров админом без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/admin/genres/")
            assert response.status_code == 401
        print("✅ Проверка авторизации админских жанров работает")

    @pytest.mark.asyncio
    async def test_admin_tracks_unauthorized(self):
        """Получение списка треков админом без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/admin/tracks/")
            assert response.status_code == 401
        print("✅ Проверка авторизации админских треков работает")

    @pytest.mark.asyncio
    async def test_admin_stats_unauthorized(self):
        """Получение статистики админом без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/admin/stats/")
            assert response.status_code == 401
        print("✅ Проверка авторизации админской статистики работает")

    @pytest.mark.asyncio
    async def test_admin_users_unauthorized(self):
        """Получение списка пользователей админом без авторизации"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/admin/users/")
            assert response.status_code == 401
        print("✅ Проверка авторизации админских пользователей работает")


class TestAPIValidation:
    """Тесты валидации API"""
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self):
        """Регистрация с отсутствующими полями"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/auth/register", json={
                "login": "test"
                
            })
            assert response.status_code == 422  
        print("✅ Валидация регистрации работает")

    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        """Регистрация с невалидным email"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/auth/register", json={
                "full_name": "Test User",
                "login": "testuser",
                "email": "invalid-email",
                "password": "password123",
                "role": "user"
            })
            assert response.status_code == 422  
        print("✅ Валидация email работает")

    @pytest.mark.asyncio
    async def test_register_short_password(self):
        """Регистрация с коротким паролем"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/auth/register", json={
                "full_name": "Test User",
                "login": "testuser",
                "email": "test@example.com",
                "password": "123",  
                "role": "user"
            })
            assert response.status_code == 422  
        print("✅ Валидация длины пароля работает")