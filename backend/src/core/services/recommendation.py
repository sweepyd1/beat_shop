from typing import List, Optional
from sqlalchemy import select, func, desc, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.track import TrackRepository
from core.repositories.purchase import PurchaseRepository
from core.repositories.interaction import InteractionRepository
from database.models import Track, Purchase, Interaction, InteractionType, User, Genre, Author

class RecommendationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.track_repo = TrackRepository(session)
        self.purchase_repo = PurchaseRepository(session)
        self.interaction_repo = InteractionRepository(session)

    async def get_personal_recommendation(
        self,
        user_id: int,
        limit: int = 1,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Track]:
        # 1. Любимые жанры (из покупок и прослушиваний)
        genre_query = (
            select(Track.genre_id, func.count(Track.id).label('cnt'))
            .join(Purchase, Purchase.track_id == Track.id)
            .where(Purchase.user_id == user_id)
            .group_by(Track.genre_id)
            .union_all(
                select(Track.genre_id, func.count(Track.id))
                .join(Interaction, Interaction.track_id == Track.id)
                .where(Interaction.user_id == user_id, Interaction.interaction_type == InteractionType.listen)
                .group_by(Track.genre_id)
            )
        ).subquery()
        stmt_genre = (
            select(genre_query.c.genre_id, func.sum(genre_query.c.cnt).label('total'))
            .group_by(genre_query.c.genre_id)
            .order_by(desc('total'))
            .limit(5)
        )
        fav_genres = await self.session.execute(stmt_genre)
        fav_genre_ids = [row[0] for row in fav_genres if row[0] is not None]

        # 2. Любимые авторы
        author_query = (
            select(Track.author_id, func.count(Track.id))
            .join(Purchase, Purchase.track_id == Track.id)
            .where(Purchase.user_id == user_id)
            .group_by(Track.author_id)
            .union_all(
                select(Track.author_id, func.count(Track.id))
                .join(Interaction, Interaction.track_id == Track.id)
                .where(Interaction.user_id == user_id, Interaction.interaction_type == InteractionType.listen)
                .group_by(Track.author_id)
            )
        ).subquery()
        stmt_author = (
            select(author_query.c.author_id, func.sum(author_query.c.cnt).label('total'))
            .group_by(author_query.c.author_id)
            .order_by(desc('total'))
            .limit(5)
        )
        fav_authors = await self.session.execute(stmt_author)
        fav_author_ids = [row[0] for row in fav_authors if row[0] is not None]

        # 3. Исключаем уже купленные/прослушанные треки
        purchased = await self.session.execute(select(Purchase.track_id).where(Purchase.user_id == user_id))
        listened = await self.session.execute(
            select(Interaction.track_id).where(
                Interaction.user_id == user_id,
                Interaction.interaction_type == InteractionType.listen
            )
        )
        exclude_owned = {row[0] for row in purchased} | {row[0] for row in listened}
        if exclude_ids:
            exclude_owned.update(exclude_ids)

        conditions = []
        if fav_genre_ids:
            conditions.append(Track.genre_id.in_(fav_genre_ids))
        if fav_author_ids:
            conditions.append(Track.author_id.in_(fav_author_ids))

        if not conditions:
            return await self.get_popular_tracks(limit, exclude_ids)

        # Получаем только ID подходящих треков (без подгрузки отношений)
        query_ids = select(Track.id).where(or_(*conditions))
        if exclude_owned:
            query_ids = query_ids.where(Track.id.not_in(list(exclude_owned)))
        query_ids = query_ids.order_by(func.random()).limit(limit)
        result_ids = await self.session.execute(query_ids)
        track_ids = result_ids.scalars().all()

        # Если ничего не нашли, пробуем без исключений
        if not track_ids:
            query_ids = select(Track.id).where(or_(*conditions)).order_by(func.random()).limit(limit)
            result_ids = await self.session.execute(query_ids)
            track_ids = result_ids.scalars().all()

        if not track_ids:
            return []

        # Загружаем полные объекты треков с подгрузкой отношений
        query = select(Track).where(Track.id.in_(track_ids)).options(
            selectinload(Track.genre),
            selectinload(Track.author)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_popular_tracks(self, limit: int = 1, exclude_ids: Optional[List[int]] = None) -> List[Track]:
        # Получаем ID популярных треков (топ-20 по прослушиваниям, затем случайный выбор)
        subq = select(Track.id).order_by(desc(Track.plays)).limit(20).subquery()
        query_ids = select(subq.c.id).order_by(func.random()).limit(limit)
        if exclude_ids:
            query_ids = query_ids.where(subq.c.id.not_in(exclude_ids))
        result_ids = await self.session.execute(query_ids)
        track_ids = result_ids.scalars().all()

        if not track_ids:
            return []

        query = select(Track).where(Track.id.in_(track_ids)).options(
            selectinload(Track.genre),
            selectinload(Track.author)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_track_by_id(self, track_id: int) -> Optional[Track]:
        query = select(Track).where(Track.id == track_id).options(
            selectinload(Track.genre),
            selectinload(Track.author)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()