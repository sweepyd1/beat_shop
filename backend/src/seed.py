import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import select

from config import cfg
from database.db_manager import db_manager
from database.models import Genre, Author, Track, User, UserRole
from api.dependencies import get_auth_service


async def seed_mass():
    async with db_manager.get_session() as session:
        print("🚀 Начинаем массовое заполнение данными...")

        
        user = await session.execute(
            select(User).where(User.login == "default_author")
        )
        user = user.scalar_one_or_none()
        if not user:
            
            user = User(
                full_name="Default Author",
                login="default_author",
                email="default@author.com",
                password_hash="defaultpass",
                role=UserRole.author,
                is_active=True
            )
            session.add(user)
            await session.flush()
            print(f"✅ Создан пользователь default_author с ID={user.id}")
        else:
            print(f"✅ Пользователь default_author уже существует с ID={user.id}")

        
        author = await session.get(Author, 1)  
        if not author:
            
            author_by_user = await session.execute(
                select(Author).where(Author.user_id == user.id)
            )
            author_by_user = author_by_user.scalar_one_or_none()
            if author_by_user:
                author = author_by_user
                print(f"✅ Найден автор с user_id={user.id}, id={author.id}")
            else:
                author = Author(
                    user_id=user.id,
                    full_name="Default Author",
                    bio="Automatically generated author for mass seeding.",
                    photo_url="/storage/covers/default_cover.jpg"
                )
                session.add(author)
                await session.flush()
                print(f"✅ Создан автор с ID={author.id} (Default Author)")
        else:
            
            
            if author.user_id is None:
                author.user_id = user.id
                session.add(author)
                await session.flush()
                print(f"✅ Обновлён user_id автора с ID=1 на {user.id}")
            print("✅ Автор с ID=1 уже существует")

        
        genre_names = [
            "Рок", "Поп", "Хип-хоп", "Электронная", "Джаз",
            "Классика", "R&B", "Кантри", "Блюз", "Метал"
        ]

        existing_genres = await session.execute(select(Genre))
        existing_genres = existing_genres.scalars().all()
        existing_names = {g.name for g in existing_genres}

        genres_to_add = []
        for name in genre_names:
            if name not in existing_names:
                genre = Genre(name=name)
                session.add(genre)
                genres_to_add.append(genre)

        if genres_to_add:
            await session.flush()
            print(f"✅ Добавлено {len(genres_to_add)} новых жанров")
        else:
            print("✅ Все 10 жанров уже присутствуют")

        
        all_genres = await session.execute(select(Genre))
        all_genres = all_genres.scalars().all()
        genre_ids = [g.id for g in all_genres]

        
        tracks_created = 0
        track_titles = [
            "Лунная соната", "В лесу", "Дорога домой", "Осенний дождь",
            "Быстрый ритм", "Медленный вальс", "Электрический сон",
            "Городской шум", "Тишина", "Восход", "Закат", "Ноктюрн",
            "Рок-н-ролл", "Симфония", "Концерт", "Этюд", "Прелюдия",
            "Фантазия", "Каприс", "Баллада", "Рэп баттл", "Бит",
            "Лоу-фай", "Чилл", "Амбиент", "Транс", "Хаус", "Техно"
        ]

        for i in range(100):
            title = random.choice(track_titles)
            if i >= len(track_titles):
                title = f"{title} {i+1}"

            duration = random.randint(120, 360)
            created_date = datetime.now() - timedelta(days=random.randint(0, 1000))
            price = round(random.uniform(50.0, 500.0), 2)
            genre_id = random.choice(genre_ids)

            track = Track(
                title=title,
                cover_url="/storage/covers/default_cover.jpg",
                duration_seconds=duration,
                created_date=created_date,
                mp3_file_url="/storage/tracks/default.mp3",
                price=price,
                genre_id=genre_id,
                author_id=author.id  
            )
            session.add(track)
            tracks_created += 1

            if tracks_created % 20 == 0:
                print(f"⏳ Создано {tracks_created} треков...")
                await session.flush()

        await session.commit()
        print(f"🎉 Успешно создано {tracks_created} треков!")


if __name__ == "__main__":
    asyncio.run(seed_mass())