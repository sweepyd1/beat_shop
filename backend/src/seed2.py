import asyncio
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiohttp
import librosa
from mutagen.mp3 import MP3
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from config import cfg
from database.db_manager import db_manager
from database.models import (
    User, Author, Genre, Track, Favorite, Purchase, Contract,
    Interaction, Subscription, UserRole, InteractionType, LicenseType
)
from api.dependencies import get_auth_service  # для хеширования паролей

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы путей
BASE_DIR = Path(__file__).resolve().parent
DATA_MUSIC_DIR = BASE_DIR / "data" / "music"
DATA_COVERS_DIR = BASE_DIR / "data" / "covers"
STORAGE_TRACKS_DIR = BASE_DIR / "storage" / "tracks"
STORAGE_COVERS_DIR = BASE_DIR / "storage" / "covers"

# Убедимся, что папки для хранения существуют
STORAGE_TRACKS_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_COVERS_DIR.mkdir(parents=True, exist_ok=True)


# ------------------- Утилиты -------------------

def scan_directory(directory: Path, extensions: tuple) -> List[Path]:
    """Рекурсивно сканирует директорию и возвращает список файлов с заданными расширениями."""
    files = []
    try:
        for ext in extensions:
            files.extend(directory.rglob(f'*{ext}'))
        logger.info(f"Найдено {len(files)} файлов с расширениями {extensions} в {directory}")
        return files
    except Exception as e:
        logger.error(f"Ошибка при сканировании директории {directory}: {e}")
        return []


def get_audio_duration(file_path: Path) -> Optional[int]:
    """Возвращает длительность MP3-файла в секундах."""
    try:
        audio = MP3(file_path)
        return int(audio.info.length)
    except Exception as e:
        logger.warning(f"Не удалось получить длительность для {file_path.name}: {e}")
        return None


def get_audio_bpm(file_path: Path) -> Optional[int]:
    """Возвращает BPM аудиофайла, безопасно обрабатывая ошибки."""
    try:
        y, sr = librosa.load(file_path, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        # tempo может быть numpy-массивом, берём первый элемент
        if hasattr(tempo, 'item'):
            return int(tempo.item())
        return int(tempo)
    except Exception as e:
        logger.warning(f"Не удалось определить BPM для {file_path.name}: {e}")
        return None


async def download_random_image(save_path, width=500, height=500, keyword="music,album"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Можно добавить ключевые слова для тематического поиска
    url = f"https://placekitten.com/{width}/{height}"
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, mode='wb') as f:
                        await f.write(await response.read())
                    print(f"✅ Обложка сохранена (Unsplash): {save_path}")
                    return True
    except Exception as e:
        print(f"⚠️ Ошибка Unsplash: {e}")
    return False


def generate_track_title(base_name: str) -> str:
    """Генерирует читаемое название трека из имени файла или создаёт случайное."""
    name = base_name.stem
    # Убираем цифры и подчёркивания в начале
    name = name.lstrip('0123456789-_ ')
    if len(name) < 3:
        adjectives = ['Тихий', 'Быстрый', 'Летний', 'Зимний', 'Утренний', 'Вечерний', 'Космический', 'Глубокий', 'Яркий', 'Холодный']
        nouns = ['Миг', 'Ритм', 'Сон', 'Дождь', 'Вальс', 'Этюд', 'Полёт', 'Взгляд', 'Путь', 'Свет']
        return f"{random.choice(adjectives)} {random.choice(nouns)}"
    return name.replace('_', ' ').replace('-', ' ').title()


def get_relative_storage_path(absolute_path: Path, storage_root: Path) -> str:
    """Преобразует абсолютный путь в относительный URL для хранения статики."""
    rel_path = absolute_path.relative_to(BASE_DIR)
    return f"/{rel_path.as_posix()}"


# ------------------- Основные сидеры -------------------

async def create_or_get_genres(session: AsyncSession) -> List[Genre]:
    """Создаёт стандартные жанры и возвращает их список."""
    genre_names = [
        "Рок", "Поп", "Хип-хоп", "Электронная", "Джаз",
        "Классика", "R&B", "Кантри", "Блюз", "Метал"
    ]
    genres = []
    for name in genre_names:
        result = await session.execute(select(Genre).where(Genre.name == name))
        genre = result.scalar_one_or_none()
        if not genre:
            genre = Genre(name=name)
            session.add(genre)
            await session.flush()
            logger.info(f"✅ Создан жанр: {name}")
        else:
            logger.info(f"✅ Жанр уже существует: {name}")
        genres.append(genre)
    return genres


async def create_fake_authors(session: AsyncSession, auth_service) -> List[Author]:
    """Создаёт несколько вымышленных авторов (связанных с User)."""
    authors_data = [
        {"full_name": "Алексей 'Электроник' Волков", "login": "alex_volkov", "email": "alex@example.com", "bio": "Создаю электронную музыку с душой."},
        {"full_name": "Мария Громова", "login": "maria_gromova", "email": "maria@example.com", "bio": "Пишу о том, что чувствую."},
        {"full_name": "Дмитрий 'Бит' Соколов", "login": "dima_beat", "email": "dima@example.com", "bio": "Хип-хоп продюсер."},
        {"full_name": "Анна Ледяная", "login": "anna_ice", "email": "anna@example.com", "bio": "Эмбиент и чилл."},
    ]
    authors = []
    for data in authors_data:
        # Проверим, существует ли пользователь
        result = await session.execute(select(User).where(User.login == data["login"]))
        user = result.scalar_one_or_none()
        if not user:
            hashed_password = auth_service.get_password_hash("password123")
            user = User(
                full_name=data["full_name"],
                login=data["login"],
                email=data["email"],
                password_hash=hashed_password,
                role=UserRole.author,
                is_active=True
            )
            session.add(user)
            await session.flush()
            logger.info(f"👤 Создан пользователь-автор: {user.login}")

        # Проверим, существует ли профиль автора
        result = await session.execute(select(Author).where(Author.user_id == user.id))
        author = result.scalar_one_or_none()
        if not author:
            # Загрузим или скачаем фото автора (упрощённо – используем дефолтную обложку)
            photo_url = "/storage/covers/default_author.jpg"
            author = Author(
                user_id=user.id,
                full_name=data["full_name"],
                bio=data["bio"],
                photo_url=photo_url
            )
            session.add(author)
            await session.flush()
            logger.info(f"🎤 Создан профиль автора: {author.full_name}")
        authors.append(author)
    return authors


async def create_fake_users(session: AsyncSession, auth_service, count: int = 15) -> List[User]:
    """Создаёт обычных пользователей (покупателей)."""
    users = []
    for i in range(count):
        login = f"user{i+1}"
        result = await session.execute(select(User).where(User.login == login))
        if result.scalar_one_or_none():
            continue
        hashed_password = auth_service.get_password_hash("password123")
        user = User(
            full_name=f"Пользователь {i+1}",
            login=login,
            email=f"user{i+1}@example.com",
            password_hash=hashed_password,
            role=UserRole.user,
            is_active=True
        )
        session.add(user)
        users.append(user)
    await session.flush()
    logger.info(f"👥 Создано {len(users)} обычных пользователей")
    return users


async def process_music_files(session: AsyncSession, music_files: List[Path], authors: List[Author], genres: List[Genre]) -> List[Track]:
    """Обрабатывает MP3-файлы, копирует в storage и создаёт записи Track."""
    tracks = []
    for idx, mp3_path in enumerate(music_files):
        # Копируем файл в storage/tracks/ с уникальным именем
        dest_filename = f"{datetime.now().timestamp()}_{idx}_{mp3_path.name}"
        dest_path = STORAGE_TRACKS_DIR / dest_filename
        if not dest_path.exists():
            import shutil
            shutil.copy2(mp3_path, dest_path)

        # Получаем метаданные
        duration = get_audio_duration(mp3_path) or random.randint(120, 360)
        bpm = get_audio_bpm(mp3_path) or random.randint(60, 180)

        # Определяем обложку
        cover_url = "/storage/covers/default_cover.jpg"  # дефолт, позже можно заменить на скачанную
        # Попробуем найти локальную обложку в data/covers с похожим именем
        cover_candidates = list(DATA_COVERS_DIR.glob(f"{mp3_path.stem}.*"))
        if cover_candidates:
            cover_path = cover_candidates[0]
            dest_cover_name = f"cover_{idx}_{cover_path.name}"
            dest_cover_path = STORAGE_COVERS_DIR / dest_cover_name
            import shutil
            shutil.copy2(cover_path, dest_cover_path)
            cover_url = get_relative_storage_path(dest_cover_path, BASE_DIR)
        else:
            # Если обложки нет – скачаем случайную
            dest_cover_name = f"cover_{idx}.jpg"
            dest_cover_path = STORAGE_COVERS_DIR / dest_cover_name
            if await download_random_image(dest_cover_path):
                cover_url = get_relative_storage_path(dest_cover_path, BASE_DIR)

        # Генерируем название
        title = generate_track_title(mp3_path)

        # Случайно выбираем автора и жанр
        author = random.choice(authors)
        genre = random.choice(genres)

        # Цена от 50 до 500
        price = round(random.uniform(50.0, 500.0), 2)
        # Дата создания в прошлом (до 2 лет назад)
        created_date = datetime.now() - timedelta(days=random.randint(30, 730))

        track = Track(
            title=title,
            cover_url=cover_url,
            duration_seconds=duration,
            created_date=created_date,
            mp3_file_url=get_relative_storage_path(dest_path, BASE_DIR),
            price=price,
            plays=random.randint(0, 1000),  # начальное количество прослушиваний
            bpm=bpm,
            genre_id=genre.id,
            author_id=author.id
        )
        session.add(track)
        tracks.append(track)

        if (idx + 1) % 10 == 0:
            logger.info(f"🎵 Обработано {idx + 1} треков...")
            await session.flush()

    await session.flush()
    logger.info(f"🎶 Всего создано треков: {len(tracks)}")
    return tracks


async def generate_user_activity(session: AsyncSession, users: List[User], tracks: List[Track]):
    """Генерирует прослушивания, избранное и покупки для каждого пользователя."""
    logger.info("🔄 Генерация активности пользователей...")
    for user in users:
        # Случайное количество треков, с которыми взаимодействовал пользователь
        interacted_tracks = random.sample(tracks, k=min(len(tracks), random.randint(5, 25)))
        for track in interacted_tracks:
            # Прослушивание (1-5 раз)
            for _ in range(random.randint(1, 5)):
                interaction = Interaction(
                    user_id=user.id,
                    track_id=track.id,
                    interaction_type=InteractionType.listen,
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 90))
                )
                session.add(interaction)

            # Избранное (с вероятностью 30%)
            if random.random() < 0.3:
                # Проверим, нет ли уже в избранном
                result = await session.execute(
                    select(Favorite).where(Favorite.user_id == user.id, Favorite.track_id == track.id)
                )
                if not result.scalar_one_or_none():
                    favorite = Favorite(user_id=user.id, track_id=track.id)
                    session.add(favorite)

            # Покупка (с вероятностью 15%)
            if random.random() < 0.15:
                # Проверим, не куплен ли уже
                result = await session.execute(
                    select(Purchase).where(Purchase.user_id == user.id, Purchase.track_id == track.id)
                )
                if not result.scalar_one_or_none():
                    license_type = random.choice(list(LicenseType))
                    amount = track.price
                    if license_type == LicenseType.extended:
                        amount *= 2.0
                    elif license_type == LicenseType.exclusive:
                        amount *= 5.0
                    purchase = Purchase(
                        user_id=user.id,
                        track_id=track.id,
                        amount=round(amount, 2),
                        license_type=license_type,
                        status="completed",
                        purchase_date=datetime.now() - timedelta(days=random.randint(0, 60))
                    )
                    session.add(purchase)
                    await session.flush()
                    # Создаём контракт
                    contract_number = f"CONTRACT-{user.id}-{track.id}-{int(datetime.now().timestamp())}"
                    contract = Contract(
                        purchase_id=purchase.id,
                        contract_number=contract_number,
                        document_url=f"/contracts/{contract_number}.pdf"
                    )
                    session.add(contract)

        # Подписки на авторов (с вероятностью 20% для каждого автора треков, которые слушал)
        authors_of_interest = {track.author_id for track in interacted_tracks}
        for author_id in authors_of_interest:
            if random.random() < 0.2:
                result = await session.execute(
                    select(Subscription).where(Subscription.user_id == user.id, Subscription.author_id == author_id)
                )
                if not result.scalar_one_or_none():
                    sub = Subscription(user_id=user.id, author_id=author_id)
                    session.add(sub)

    await session.flush()
    logger.info("✅ Активность пользователей сгенерирована")


# ------------------- Главная функция -------------------

async def seed_all():
    """Основная функция для наполнения базы данных."""
    logger.info("🚀 Запуск массового наполнения БД...")

    # Сканируем локальные файлы
    music_files = scan_directory(DATA_MUSIC_DIR, ('.mp3',))
    if not music_files:
        logger.error("❌ Не найдено MP3-файлов в data/music. Добавьте файлы и повторите.")
        return

    cover_files = scan_directory(DATA_COVERS_DIR, ('.jpg', '.jpeg', '.png'))
    logger.info(f"Найдено локальных обложек: {len(cover_files)}")

    try:
        async with db_manager.get_session() as session:
            await session.execute(text("SELECT 1"))
            logger.info("✅ Соединение с базой данных установлено")
    except Exception as e:
        logger.error(f"❌ Не удалось подключиться к БД: {e}")
        logger.error("Проверьте, запущен ли PostgreSQL и правильность строки подключения в config.py")
        return
    auth_service = get_auth_service()

    # 1. Жанры
    genres = await create_or_get_genres(session)
    await session.commit()

    # 2. Авторы (с пользователями)
    authors = await create_fake_authors(session, auth_service)
    await session.commit()

    # 3. Обычные пользователи
    users = await create_fake_users(session, auth_service, count=15)
    await session.commit()

    # 4. Треки из MP3-файлов
    tracks = await process_music_files(session, music_files, authors, genres)
    await session.commit()

    # 5. Активность
    all_users = users + [await session.get(User, author.user_id) for author in authors]
    await generate_user_activity(session, all_users, tracks)
    await session.commit()

    logger.info("🎉 База данных успешно наполнена!")


if __name__ == "__main__":
    asyncio.run(seed_all())