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



class PlaylistLike(Base):
    __tablename__ = "playlist_likes"

    user_id = Column(Integer, nullable=False, primary_key=True)
    playlist_id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())