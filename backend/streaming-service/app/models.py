from pydantic import BaseModel

class Song(BaseModel):
    song_id: str
    title: str
    duration: int  # en segundos
    filepath: str
    album_id: str
    genre_id: str
    track_number: int
