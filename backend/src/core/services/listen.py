from fastapi import HTTPException, status
from core.repositories.listen import ListenRepository
from core.repositories.track import TrackRepository


class ListenService:
    def __init__(self, repo: ListenRepository, track_repo: TrackRepository):
        self.repo = repo
        self.track_repo = track_repo

    async def log_listen(self, user_id: int, track_id: int, count_today_only: bool = True) -> dict:
        """
        Записать прослушивание трека.
        
        Если count_today_only=True — засчитывается только одно прослушивание в день от пользователя.
        Если False — каждое воспроизведение считается отдельно (вариант А).
        """
        
        track = await self.track_repo.get(track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        counted = True
        
        if count_today_only:
            
            existing = await self.repo.get_today_listen(user_id, track_id)
            if existing:
                
                current_plays = track.plays or 0
                return {
                    "status": "ignored",
                    "message": "Already counted today",
                    "total_plays": current_plays,
                    "counted": False
                }

        
        await self.repo.create_listen(user_id, track_id)
        
        
        new_plays = await self.repo.increment_track_plays(track_id)
        if new_plays is None:
            raise HTTPException(status_code=500, detail="Failed to update track plays")

        

        return {
            "status": "ok",
            "message": "Listen counted",
            "total_plays": new_plays,
            "counted": True
        }