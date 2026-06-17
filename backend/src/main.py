from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from api.routes.contact import router as contact_router

# @asynccontextmanager







        



        















    



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
    
)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        new_error = dict(error)
        err_type = error.get("type", "")
        msg = error.get("msg", "")
        ctx = error.get("ctx", {})

        
        if err_type == "missing":
            new_error["msg"] = "Обязательное поле"
        elif err_type == "string_too_short":
            min_len = ctx.get("min_length", "?")
            new_error["msg"] = f"Минимальная длина: {min_len} симв."
        elif err_type == "string_too_long":
            max_len = ctx.get("max_length", "?")
            new_error["msg"] = f"Максимальная длина: {max_len} симв."
        elif err_type == "value_error":
            if "email" in msg.lower():
                new_error["msg"] = "Некорректный формат email"
            else:
                new_error["msg"] = "Некорректное значение"
        

        errors.append(new_error)

    return JSONResponse(status_code=422, content={"detail": errors})
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

app.include_router(admin_authors.router)
app.include_router(admin_genres.router)
app.include_router(admin_tracks.router)
app.include_router(admin_stats.router)
app.include_router(admin_users.router)
app.include_router(contact_router)

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