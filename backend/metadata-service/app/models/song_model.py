from sqlalchemy import Column, Integer, String, Date, LargeBinary, ForeignKey, Double
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.ext.declarative import declarative_base



class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    songs = relationship("Song", back_populates="genre")


class Album(Base):
    __tablename__ = "album"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    release_date = Column(Date)
    cover = Column(LargeBinary)  # <- aquí se almacenan los bytes de la imagen
    artist_id = Column(Integer, ForeignKey("artist.id", ondelete="SET NULL"))
    songs = relationship("Song", back_populates="album")


class Song(Base):
    __tablename__ = "song"

    song_id = Column(String(100), primary_key=True)
    title = Column(String(100), nullable=False)
    duration = Column(Double)

    album_id = Column(Integer, ForeignKey("album.id", ondelete="SET NULL"))
    genre_id = Column(Integer, ForeignKey("genre.id", ondelete="SET NULL"))
    artist_id = Column(Integer, ForeignKey("artist.id", ondelete="SET NULL"))


    album = relationship("Album", back_populates="songs")
    genre = relationship("Genre", back_populates="songs")



from sqlalchemy import Column, Integer, String
from database import Base

class Artist(Base):
    __tablename__ = "artist"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
