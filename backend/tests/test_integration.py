# test_integration.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app  # Убедитесь, что app = FastAPI() экспортируется из main.py

@pytest.mark.asyncio
async def test_register_and_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Регистрация
        reg_resp = await client.post("/auth/register", json={
            "full_name": "John Doe", "login": "johndoe",
            "email": "john@example.com", "password": "Test1234!", "role": "user"
        })
        assert reg_resp.status_code == 201
        assert reg_resp.json()["login"] == "johndoe"

        # Вход
        login_resp = await client.post("/auth/login", data={
            "username": "johndoe", "password": "Test1234!"
        })
        assert login_resp.status_code == 200
        
        # Проверка профиля
        me_resp = await client.get("/users/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["login"] == "johndoe"
    print("✅ Интеграционный тест авторизации пройден.")

@pytest.mark.asyncio
async def test_create_track_and_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Регистрируем автора
        await client.post("/auth/register", json={
            "full_name": "Author", "login": "author1",
            "email": "author@example.com", "password": "pass", "role": "author"
        })
        
        # Загрузка трека (имитация multipart)
        files = {
            "mp3": ("test.mp3", b"fake-mp3-content", "audio/mpeg"),
            "cover": ("cover.jpg", b"fake-image", "image/jpeg")
        }
        create_resp = await client.post("/tracks/", data={
            "title": "Test Track", "genre_id": "1", "price": "199.00", "bpm": "140"
        }, files=files)
        assert create_resp.status_code == 201
        track_id = create_resp.json()["id"]
        
        # Поиск
        search_resp = await client.get(f"/tracks/search?query=Test")
        assert search_resp.status_code == 200
        tracks = search_resp.json()
        assert any(t["id"] == track_id for t in tracks)
    print("✅ Интеграционный тест треков пройден.")