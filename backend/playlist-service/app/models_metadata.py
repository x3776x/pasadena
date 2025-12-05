from sqlalchemy import Column, String
from .database import MetadataBase 

class Song(MetadataBase):
    __tablename__ = "song"
    song_id = Column(String(100), primary_key=True)
