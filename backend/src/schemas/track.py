from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from database.models import InteractionType
from enum import Enum


# ---------- Genre Schemas ----------
class GenreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Название жанра")


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Название жанра")


class GenreResponse(GenreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Author Schemas ----------
class AuthorBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150, description="ФИО автора")
    photo_url: Optional[str] = Field(None, description="Ссылка на фото автора")
    bio: Optional[str] = Field(None, description="Биография автора")


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    photo_url: Optional[str] = None
    bio: Optional[str] = None


class AuthorResponse(AuthorBase):
    id: int
    tracks_count: Optional[int] = Field(None, description="Количество треков автора")

    model_config = ConfigDict(from_attributes=True)


class AuthorDetailResponse(AuthorBase):
    id: int
    tracks: list["TrackShortResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# ---------- Track Schemas ----------
class TrackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название трека")
    cover_url: Optional[str] = Field(None, description="Ссылка на обложку")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Длительность в секундах")
    created_date: Optional[datetime] = Field(None, description="Дата создания произведения")
    mp3_file_url: str = Field(..., description="Путь к mp3 файлу")
    price: float = Field(..., ge=0, description="Цена трека")
    genre_id: int = Field(..., gt=0, description="ID жанра")
    author_id: int = Field(..., gt=0, description="ID автора")


class TrackCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    genre_id: int
    price: float = Field(..., ge=0)
    bpm: Optional[int] = Field(None, ge=0)
    
class AuthorShortResponse(BaseModel):
    id: int
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class GenreShortResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class TrackResponse(BaseModel):
    id: int
    title: str
    cover_url: Optional[str]
    duration_seconds: Optional[int]
    created_date: Optional[datetime]
    added_date: datetime
    mp3_file_url: str
    sales: int = 0   
    price: float
    plays: int
    bpm: Optional[int]
    genre: GenreShortResponse   # вместо genre_id
    author: AuthorShortResponse # вместо author_id

    model_config = ConfigDict(from_attributes=True)


class TrackUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    cover_url: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    created_date: Optional[datetime] = None
    mp3_file_url: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    genre_id: Optional[int] = Field(None, gt=0)
    author_id: Optional[int] = Field(None, gt=0)




class TrackShortResponse(BaseModel):
    """Краткая информация о треке (для списков)"""
    id: int
    title: str
    cover_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    price: float
    author_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrackWithInteractionResponse(TrackShortResponse):
    """Трек с информацией о взаимодействии пользователя"""
    is_favorite: bool = False
    is_purchased: bool = False
    interaction_count: Optional[int] = None


# ---------- Favorite Schemas ----------
class FavoriteBase(BaseModel):
    user_id: int
    track_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    added_at: datetime
    track: Optional[TrackShortResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Purchase Schemas ----------
class PurchaseBase(BaseModel):
    user_id: int
    track_id: int
    amount: float
    status: str = "completed"


class PurchaseCreate(PurchaseBase):
    pass


class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    purchase_date: datetime
    amount: float
    status: str
    track: Optional[TrackShortResponse] = None
    contract: Optional["ContractResponse"] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Contract Schemas ----------
class ContractBase(BaseModel):
    purchase_id: int
    contract_number: str
    document_url: Optional[str] = None


class ContractCreate(ContractBase):
    pass


class ContractResponse(BaseModel):
    id: int
    purchase_id: int
    contract_number: str
    issued_at: datetime
    document_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Interaction Schemas ----------

# Для совместимости с Pydantic v2 определим Enum строк
class InteractionTypeEnum(str, Enum):
    listen = "listen"
    favorite = "favorite"
    purchase = "purchase"


class InteractionBase(BaseModel):
    user_id: int
    track_id: int
    interaction_type: InteractionTypeEnum


class InteractionCreate(InteractionBase):
    pass


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    track_id: int
    interaction_type: InteractionTypeEnum
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Search/Filter Schemas ----------
class TrackFilterParams(BaseModel):
    query: Optional[str] = Field(None, description="Поисковый запрос")
    genre_id: Optional[int] = Field(None, description="Фильтр по жанру")
    author_id: Optional[int] = Field(None, description="Фильтр по автору")
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    sort_by: Optional[str] = Field(None, pattern="^(title|price|created_date|added_date|popularity)$")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# ---------- Recommendation Schemas ----------
class RecommendationResponse(BaseModel):
    track_id: int
    score: Optional[float] = None
    reason: Optional[str] = None  
class AuthorTrackResponse(BaseModel):
    """Упрощённая схема для списка треков автора (дашборд)"""
    id: int
    title: str
    cover_url: Optional[str] = None
    price: float
    plays: int = 0
    sales: int = 0   # количество продаж


AuthorDetailResponse.model_rebuild()
TrackResponse.model_rebuild()
TrackShortResponse.model_rebuild()
PurchaseResponse.model_rebuild()