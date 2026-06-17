import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a'}

class FileService:
    def __init__(self, storage_path: Path = Path("storage")):
        self.storage_path = storage_path
        self.covers_path = storage_path / "covers"
        self.tracks_path = storage_path / "tracks"
        self.avatars_path = storage_path / "avatars"
        
        
        self.covers_path.mkdir(parents=True, exist_ok=True)
        self.tracks_path.mkdir(parents=True, exist_ok=True)

    async def save_cover(self, file: UploadFile) -> str:
        """Сохраняет обложку и возвращает относительный путь"""
        return await self._save_file(file, self.covers_path, ALLOWED_IMAGE_EXTENSIONS)

    async def save_track(self, file: UploadFile) -> str:
        """Сохраняет трек и возвращает относительный путь"""
        return await self._save_file(file, self.tracks_path, ALLOWED_AUDIO_EXTENSIONS)
    async def save_avatar(self, file: UploadFile) -> str:
        """Сохраняет аватар пользователя и возвращает относительный путь"""
        return await self._save_file(file, self.avatars_path, ALLOWED_IMAGE_EXTENSIONS)

    async def _save_file(self, file: UploadFile, target_dir: Path, allowed_extensions: set) -> str:
        
        ext = Path(file.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Недопустимый формат файла. Разрешены: {allowed_extensions}")
        
        
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = target_dir / unique_name
        
        
        try:
            async with aiofiles.open(file_path, 'wb') as buffer:
                content = await file.read()
                await buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")
        
        
        relative_path = f"/storage/{target_dir.name}/{unique_name}"
        return relative_path

    def delete_file(self, file_url: str):
        """Удаляет файл по URL (если нужно)"""
        if not file_url.startswith("/storage/"):
            return
        
        relative = file_url.replace("/storage/", "")
        file_path = self.storage_path / relative
        if file_path.exists():
            file_path.unlink()