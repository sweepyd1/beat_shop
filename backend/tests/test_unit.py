# test_unit.py
import pytest
from unittest.mock import AsyncMock
from src.core.services.auth import AuthService
from src.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_register_new_user():
    mock_user_repo = AsyncMock()
    mock_user_repo.get_by_login.return_value = None
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = AsyncMock(
        id=1, login='test', email='test@test.com', password='hashed_password'
    )
    
    mock_author_repo = AsyncMock()
    mock_file_service = AsyncMock()
    
    service = AuthService(
        user_repo=mock_user_repo,
        author_repo=mock_author_repo,
        subscription_repo=AsyncMock(),
        file_service=mock_file_service
    )
    
    user_data = UserCreate(
        full_name='Test User',
        login='test',
        email='test@test.com',
        password='securepass123',
        role='user'
    )
    
    result = await service.register(user_data)
    
    assert result.id == 1
    assert result.login == 'test'
    # Проверка, что пароль был захэширован
    assert result.password != 'securepass123'
    mock_user_repo.create.assert_called_once()
    mock_author_repo.create.assert_not_called()
    print("✅ Unit-тест регистрации пройден.")