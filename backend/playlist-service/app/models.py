from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base


class Playlist(Base):
    __tablename__ = "playlist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    playlist_cover = Column(LargeBinary(), nullable=True)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    likes = relationship("PlaylistLike", back_populates="playlist", cascade="all, delete-orphan")
    songs = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistLike(Base):
    __tablename__ = "playlist_likes"

    user_id = Column(Integer, primary_key=True, nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlist.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación inversa
    playlist = relationship("Playlist", back_populates="likes")


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    playlist_id = Column(Integer, ForeignKey("playlist.id", ondelete="CASCADE"), primary_key=True)
    song_id = Column(String(100), primary_key=True, nullable=False)
    position = Column(Integer, nullable=False)

    # Relación inversa
    playlist = relationship("Playlist", back_populates="songs")
