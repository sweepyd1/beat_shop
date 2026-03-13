from core.repositories.favorite import FavoriteRepository

class FavoriteService:
    def __init__(self, repo: FavoriteRepository):
        self.repo = repo

    async def get_user_favorites(self, user_id: int):
        favorites = await self.repo.get_user_favorites(user_id)
        return favorites

    async def add_favorite(self, user_id: int, track_id: int):
        # Проверяем, нет ли уже
        existing = await self.repo.get_by_user_and_track(user_id, track_id)
        if existing:
            return existing
        favorite = await self.repo.create(user_id=user_id, track_id=track_id)
        return favorite

    async def remove_favorite(self, user_id: int, track_id: int):
        favorite = await self.repo.get_by_user_and_track(user_id, track_id)
        if favorite:
            await self.repo.delete(favorite.id)
            return True
        return False