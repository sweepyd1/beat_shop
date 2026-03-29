from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from core.services.author import AuthorService
from core.services.genre import GenreService
from database.models import Track, User
from core.repositories.track import TrackRepository
from core.services.file_service import FileService

class TrackService:
    def __init__(
        self,
        track_repo: TrackRepository,
        author_service: AuthorService,
        genre_service: GenreService,
        file_service: FileService
    ):
        self.repo = track_repo
        self.author_service = author_service
        self.genre_service = genre_service
        self.file_service = file_service

    async def create_track(
        self,
        user: User,
        title: str,
        genre_id: int,
        price: float,
        cover: UploadFile,
        mp3: UploadFile,
        bpm: Optional[int] = None
    ) -> Track:
        # 1. Проверяем, что пользователь является автором
        author = await self.author_service.get_author_by_user_id(user.id)
        if not author:
            raise HTTPException(status_code=403, detail="Только авторы могут загружать треки")

        # 2. Проверяем существование жанра
        genre = await self.genre_service.get_genre(genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Жанр не найден")

        # 3. Сохраняем файлы
        try:
            cover_url = await self.file_service.save_cover(cover)
            mp3_url = await self.file_service.save_track(mp3)
        except HTTPException as e:
            raise e

        # 4. Создаём трек
        track = await self.repo.create(
            title=title,
            genre_id=genre_id,
            author_id=author.id,
            price=price,
            bpm=bpm,
            cover_url=cover_url,
            mp3_file_url=mp3_url,
            plays=0
        )
        return track

    def _make_naive(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Убирает часовой пояс из datetime, если он есть."""
        if dt and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    async def update_track(self, track_id: int, update_data: dict, cover_file=None, mp3_file=None):

        if "created_date" in update_data:
            update_data["created_date"] = self._make_naive(update_data["created_date"])

        track = await self.repo.get(track_id)
        if not track:
            return None
        
      
        if cover_file:
            if track.cover_url:
                self.file_service.delete_file(track.cover_url)
            update_data['cover_url'] = await self.file_service.save_cover(cover_file)
        
        # Обработка нового mp3
        if mp3_file:
            if track.mp3_file_url:
                self.file_service.delete_file(track.mp3_file_url)
            update_data['mp3_file_url'] = await self.file_service.save_track(mp3_file)
        
        return await self.repo.update(track_id, **update_data)

    async def delete_track(self, track_id: int):
        track = await self.repo.get(track_id)
        if not track:
            return False
        
        # Удаляем связанные файлы
        if track.cover_url:
            self.file_service.delete_file(track.cover_url)
        if track.mp3_file_url:
            self.file_service.delete_file(track.mp3_file_url)
        
        # Также нужно удалить зависимости (избранное, покупки, взаимодействия) – каскадно в БД
        return await self.repo.delete(track_id)
    
    async def get_track(self, track_id: int):
        return await self.repo.get(id=track_id)
    
    async def get_popular_tracks(self, limit: int):
        """Бизнес-логика для популярных треков (может включать кэширование и т.п.)."""
        tracks = await self.repo.get_popular(limit)
        return tracks

    async def get_new_tracks(self, limit: int):
        """Бизнес-логика для новых треков."""
        tracks = await self.repo.get_new(limit)
        return tracks
    async def search_tracks(
        self,
        query: Optional[str] = None,
        genre_ids: Optional[List[int]] = None,
        bpm_min: Optional[int] = None,
        bpm_max: Optional[int] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None,
        sort_by: str = "popular",
        skip: int = 0,
        limit: int = 20
    ):
        return await self.repo.search(
            query=query,
            genre_ids=genre_ids,
            bpm_min=bpm_min,
            bpm_max=bpm_max,
            duration_min=duration_min,
            duration_max=duration_max,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )
    async def get_tracks_by_user(self, user_id: int) -> List[Track]:
        """Получение треков текущего автора по user_id"""
        # Получаем автора по user_id
        author = await self.author_service.get_author_by_user_id(user_id)
        if not author:
            return []
        
        # Получаем треки автора с подгрузкой жанра
        tracks = await self.repo.get_by_author_id(author.id)
        return tracks
