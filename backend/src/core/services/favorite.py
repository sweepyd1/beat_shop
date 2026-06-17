from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.favorite import FavoriteRepository
from core.repositories.track import TrackRepository
from fastapi import HTTPException, status

class FavoriteService:
    def __init__(self, repo: FavoriteRepository, track_repo: TrackRepository):    
        self.repo = repo
        self.track_repo = track_repo
      
    
    async def get_user_favorites(self, user_id: int):
        favorites = await self.repo.get_user_favorites(user_id)
        return favorites

    async def add_favorite(self, user_id: int, track_id: int):
        track = await self.track_repo.get(track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        exists = await self.repo.exists(user_id, track_id)
        if exists:
            raise HTTPException(status_code=400, detail="Track already in favorites")
        
        favorite = await self.repo.create(user_id=user_id, track_id=track_id)
        return favorite

    async def remove_favorite(self, user_id: int, track_id: int) -> bool:
        return await self.repo.delete_by_user_track(user_id, track_id)