from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
import uvicorn
from core.repositories.user import UserRepository
from core.services.auth import AuthService
from core.repositories.author import AuthorRepository
from core.services.author import AuthorService
from database.db_manager import db_manager
from database.models import User
from config import cfg, setup_environment
from api.routes import auth, tracks, genres, user, favorites, purchase, listen, author, recommendations
from api.routes.admin import authors as admin_authors, genre as admin_genres, tracks as admin_tracks, admin as admin_stats, users as admin_users
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Действия при старте
#     async with db_manager.get_session() as session:
#         repo = UserRepository(session)
#         author_repo = AuthorRepository(session)
#         author_service = AuthorService(repo=author_repo)
#         auth_service = AuthService(repo, author_repo)
        
#         # Проверяем, есть ли администратор
#         result = await session.execute(select(User).where(User.is_admin == True))
#         admin = result.scalar_one_or_none()
        
#         if not admin:
#             # Создаём администратора
#             hashed = auth_service.get_password_hash(cfg.admin.password)
#             admin = User(
#                 full_name="Administrator",
#                 login=cfg.admin.login,
#                 email=cfg.admin.email,
#                 password_hash=hashed,
#                 is_admin=True
#             )
#             session.add(admin)
#             await session.commit()
#             print(f"Admin user created: {cfg.admin.login}")
#         else:
#             print("Admin user already exists")
    
#     yield
#     # Действия при выключении (опционально)
#     pass
setup_environment()
storage_path = Path("storage")
covers_path = storage_path / "covers"
tracks_path = storage_path / "tracks"
covers_path.mkdir(parents=True, exist_ok=True)
tracks_path.mkdir(parents=True, exist_ok=True)
app = FastAPI(
    title=cfg.app.name,
    version=cfg.app.version,
    debug=cfg.app.debug,
    # lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

app.include_router(auth.router)
app.include_router(tracks.router)
app.include_router(genres.router)
app.include_router(user.router)
app.include_router(favorites.router)
app.include_router(purchase.router)
app.include_router(listen.router)
app.include_router(author.router)
app.include_router(recommendations.router)
# Админские роуты
app.include_router(admin_authors.router)
app.include_router(admin_genres.router)
app.include_router(admin_tracks.router)
app.include_router(admin_stats.router)
app.include_router(admin_users.router)

@app.get("/")
async def root():
    return {
        "message": "Music Store API",
        "version": cfg.app.version,
        "environment": cfg.app.env
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app=app)