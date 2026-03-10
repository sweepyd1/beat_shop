
from sqlalchemy import (
    Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean, 
    UniqueConstraint, Index, func
)
from sqlalchemy.orm import  Mapped, mapped_column, relationship
import enum

from .db_manager import Base  


class InteractionType(enum.Enum):
    listen = "listen"
    favorite = "favorite"
    purchase = "purchase"

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    registered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(200))
    bio: Mapped[str | None] = mapped_column(Text)

    tracks = relationship("Track", back_populates="author", cascade="all, delete-orphan")

class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tracks = relationship("Track", back_populates="genre")

class Track(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(200))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    created_date: Mapped[DateTime | None] = mapped_column(DateTime)
    added_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    mp3_file_url: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Внешние ключи
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey('genres.id'), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'), nullable=False)

    # Связи
    genre = relationship("Genre", back_populates="tracks")
    author = relationship("Author", back_populates="tracks")
    favorites = relationship("Favorite", back_populates="track", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="track", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="track", cascade="all, delete-orphan")

    # Индекс для поиска
    __table_args__ = (
        Index('idx_track_title', 'title'),
    )

class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey('tracks.id'), nullable=False)
    added_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")
    track = relationship("Track", back_populates="favorites")

    # Уникальность пары пользователь-трек
    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', name='unique_user_track_favorite'),
    )

class Purchase(Base):
    __tablename__ = 'purchases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey('tracks.id'), nullable=False)
    purchase_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='completed')

    user = relationship("User", back_populates="purchases")
    track = relationship("Track", back_populates="purchases")
    contract = relationship("Contract", uselist=False, back_populates="purchase", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', name='unique_user_track_purchase'),
    )

class Contract(Base):
    __tablename__ = 'contracts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_id: Mapped[int] = mapped_column(Integer, ForeignKey('purchases.id'), unique=True, nullable=False)
    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    issued_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    document_url: Mapped[str | None] = mapped_column(String(200))

    purchase = relationship("Purchase", back_populates="contract")

class Interaction(Base):
    __tablename__ = 'interactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey('tracks.id'), nullable=False)
    interaction_type: Mapped[InteractionType] = mapped_column(Enum(InteractionType), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="interactions")
    track = relationship("Track", back_populates="interactions")

    __table_args__ = (
        Index('idx_interaction_user_type', 'user_id', 'interaction_type'),
        Index('idx_interaction_track', 'track_id'),
    )
