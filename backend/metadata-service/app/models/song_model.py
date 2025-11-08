# app/models/song_model.py

from sqlalchemy import Column, String, Float, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Song(Base):
    __tablename__ = "song"

    song_id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    artist = Column(String, nullable=True)
    album = Column(String, nullable=True)
    year = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    duration = Column(Float, nullable=True)

