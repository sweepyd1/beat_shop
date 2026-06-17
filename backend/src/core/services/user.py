from core.repositories.user import UserRepository
from core.repositories.subscription import SubscriptionRepository
from core.services.file_service import FileService
from typing import Optional
from database.models import User

class UserService:
    def __init__(self, repo: UserRepository, file_service: FileService):
        self.repo = repo
        self.file_service = file_service

    async def get_profile(self, user_id: int) -> Optional[User]:
        """Получить данные профиля с подписками, покупками, избранным"""
        return await self.repo.get_with_relations(user_id)

    async def update_profile(self, user_id: int, update_data: dict, avatar_file=None) -> Optional[User]:
        user = await self.repo.get(user_id)
        if not user:
            return None

        if avatar_file:
            if user.avatar_url:
                self.file_service.delete_file(user.avatar_url)
            update_data['avatar_url'] = await self.file_service.save_avatar(avatar_file)

        
        updated_user = await self.repo.update(user_id, **update_data)
        return updated_user

    async def get_purchases(self, user_id: int):
        
        pass

    