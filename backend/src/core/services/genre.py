from typing import Optional
from database.models import Genre
from core.repositories.genre import GenreRepository
from schemas.genre import GenreCreate, GenreUpdate
from fastapi import HTTPException, status

class GenreService:
    def __init__(self, repo: GenreRepository):
        self.repo = repo

    async def create_genre(self, genre_data: GenreCreate):
        # Проверка на дубликат (опционально)
        return await self.repo.create(genre_data.name, genre_data.image_url)

    async def update_genre(self, genre_id: int, genre_data: GenreUpdate):
            genre = await self.repo.get(genre_id)
            if not genre:
                return None
            return await self.repo.update(genre_id, genre_data.name, genre_data.image_url)

    async def delete_genre(self, genre_id: int):
        genre = await self.repo.get(genre_id)
        if not genre:
            return False
        if genre.tracks:
            raise HTTPException(status_code=400, detail="Нельзя удалить жанр, к которому привязаны треки")
        return await self.repo.delete(genre_id)
    
    async def get_all_genres(self):
        genres_with_counts = await self.repo.get_all_with_counts()
        result = []
        for genre, count in genres_with_counts:
            result.append({
                "id": genre.id,
                "name": genre.name,
                "image_url": genre.image_url,      # добавить
                "tracks_count": count
            })
        return result

    async def get_genre(self, genre_id: int) -> Optional[Genre]:
        return await self.repo.get(genre_id)

    # Новый метод для админки (возвращает все жанры без counts, но с image_url)
    async def get_all_genres_admin(self):
        return await self.repo.get_all()   # если в BaseRepository есть get_all