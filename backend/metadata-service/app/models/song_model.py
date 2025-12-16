from sqlalchemy import Column, Integer, String, Date, LargeBinary, ForeignKey, Double, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Column, Integer, String


class Genre(Base):
    __tablename__ = "genre"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    songs = relationship("Song", back_populates="genre")


class Album(Base):
    __tablename__ = "album"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    release_date = Column(Date)
    cover = Column(LargeBinary)  # <- aquí se almacenan los bytes de la imagen
    artist_id = Column(Integer, ForeignKey("artist.id", ondelete="SET NULL"))
    songs = relationship("Song", back_populates="album")


class Song(Base):
    __tablename__ = "song"
    __table_args__ = {'extend_existing': True}

    song_id = Column(String(100), primary_key=True)
    title = Column(String(100), nullable=False)
    duration = Column(Double)

    album_id = Column(Integer, ForeignKey("album.id", ondelete="SET NULL"))
    genre_id = Column(Integer, ForeignKey("genre.id", ondelete="SET NULL"))
    artist_id = Column(Integer, ForeignKey("artist.id", ondelete="SET NULL"))


    album = relationship("Album", back_populates="songs")
    genre = relationship("Genre", back_populates="songs")



class Artist(Base):
    __tablename__ = "artist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class UserStatistics(Base):
    __tablename__ = "user_statistics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String, nullable=False)
    song_id = Column(String(100), ForeignKey("song.song_id", ondelete="CASCADE"), nullable=False)

    play_count = Column(Integer, default=1)
    total_time = Column(Float, default=0)
    last_play = Column(DateTime, default=datetime.datetime.utcnow)

    # Relación opcional (sirve para joins)
