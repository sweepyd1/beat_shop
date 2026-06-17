from typing import Optional
from datetime import datetime, date
from sqlalchemy import select, and_, func
from database.models import Interaction, InteractionType, Track
from .base import BaseRepository


class ListenRepository(BaseRepository[Interaction]):
    def __init__(self, session):
        super().__init__(Interaction, session)

    async def get_today_listen(
        self, 
        user_id: int, 
        track_id: int
    ) -> Optional[Interaction]:
        """Проверить, было ли уже прослушивание сегодня (вариант Б)"""
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        
        stmt = select(Interaction).where(
            Interaction.user_id == user_id,
            Interaction.track_id == track_id,
            Interaction.interaction_type == InteractionType.listen,
            Interaction.timestamp >= today_start,
            Interaction.timestamp <= today_end
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_listen(
        self, 
        user_id: int, 
        track_id: int, 
        timestamp: Optional[datetime] = None
    ) -> Interaction:
        """Создать запись о прослушивании"""
        interaction = Interaction(
            user_id=user_id,
            track_id=track_id,
            interaction_type=InteractionType.listen,
            timestamp=timestamp or datetime.utcnow()
        )
        self.session.add(interaction)
        await self.session.flush()  
        await self.session.commit()
        return interaction

    async def increment_track_plays(self, track_id: int) -> Optional[int]:
        """Увеличить счётчик plays у трека и вернуть новое значение"""
        stmt = select(Track).where(Track.id == track_id)
        result = await self.session.execute(stmt)
        track = result.scalar_one_or_none()
        
        if track:
            track.plays = (track.plays or 0) + 1
            await self.session.flush()
            await self.session.commit()
            return track.plays
        return None