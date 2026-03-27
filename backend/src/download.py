import json
import os
import requests
import time
from pathlib import Path

# Конфигурация
JSON_PATH = "jamendo_tracks_1000.json"
STORAGE_DIR = Path("storage")
COVERS_DIR = STORAGE_DIR / "covers"
TRACKS_DIR = STORAGE_DIR / "tracks"
OUTPUT_JSON = "tracks_metadata_for_db.json"

# Создаём папки
COVERS_DIR.mkdir(parents=True, exist_ok=True)
TRACKS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, dest_path, timeout=30, retries=2):
    """Скачивает файл по URL с повторными попытками"""
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                print(f"  HTTP {response.status_code} при скачивании {url}")
        except Exception as e:
            print(f"  Ошибка при скачивании (попытка {attempt+1}): {e}")
        time.sleep(1)
    return False

def sanitize_filename(name):
    """Убирает недопустимые символы для имени файла"""
    return "".join(c for c in name if c.isalnum() or c in ' ._-').strip()

def main():
    # Читаем JSON
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        tracks = json.load(f)
    
    print(f"Загружено {len(tracks)} треков из {JSON_PATH}")
    
    tracks_for_db = []
    
    for idx, track in enumerate(tracks, 1):
        track_id = track.get('id')
        if not track_id:
            continue
        
        artist = track.get('artist_name', 'Unknown')
        title = track.get('name', 'Unknown')
        
        # Имена файлов
        safe_artist = sanitize_filename(artist)
        safe_title = sanitize_filename(title)
        mp3_filename = f"{track_id}_{safe_artist}_{safe_title}.mp3"
        cover_filename = f"{track_id}.jpg"
        
        mp3_path = TRACKS_DIR / mp3_filename
        cover_path = COVERS_DIR / cover_filename
        
        # Скачиваем обложку, если нет
        cover_url = track.get('album_image') or track.get('image')
        if cover_url and not cover_path.exists():
            print(f"[{idx}/{len(tracks)}] Скачиваю обложку {cover_filename}...")
            if download_file(cover_url, cover_path):
                print(f"  Обложка сохранена: {cover_path}")
            else:
                print(f"  Не удалось скачать обложку для трека {track_id}")
                # используем дефолтную обложку
                cover_path = COVERS_DIR / "default_cover.jpg"
        else:
            print(f"[{idx}/{len(tracks)}] Обложка уже есть: {cover_path}")
        
        # Скачиваем MP3, если нет
        audio_url = track.get('audiodownload') or track.get('audio')
        if audio_url and not mp3_path.exists():
            print(f"  Скачиваю MP3 {mp3_filename}...")
            if download_file(audio_url, mp3_path):
                print(f"  MP3 сохранён: {mp3_path}")
            else:
                print(f"  Не удалось скачать MP3 для трека {track_id}")
                continue  # пропускаем трек без аудио
        else:
            print(f"[{idx}/{len(tracks)}] MP3 уже есть: {mp3_path}")
        
        # Формируем запись для БД
        db_record = {
            "source_id": int(track_id),
            "title": title,
            "cover_url": f"/storage/covers/{cover_filename}",
            "duration_seconds": track.get('duration', 0),
            "created_date": track.get('releasedate'),
            "mp3_file_url": f"/storage/tracks/{mp3_filename}",
            "price": None,                     # установите позже
            "plays": track.get('listens', 0),
            "bpm": None,
            "genre_id": None,                  # нужно будет сопоставить
            "author_id": None,                 # нужно будет сопоставить
            "artist_name": artist,
            "artist_id": track.get('artist_id'),
            "album_name": track.get('album_name'),
            "original_url": track.get('shareurl'),
        }
        tracks_for_db.append(db_record)
        
        time.sleep(0.3)   # пауза между треками
    
    # Сохраняем метаданные для БД
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(tracks_for_db, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Готово! Скачано/проверено {len(tracks_for_db)} треков.")
    print(f"📄 Метаданные для БД сохранены в {OUTPUT_JSON}")
    print(f"🖼️ Обложки в {COVERS_DIR}")
    print(f"🎵 Аудио в {TRACKS_DIR}")

if __name__ == "__main__":
    main()