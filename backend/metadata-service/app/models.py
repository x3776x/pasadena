from pydantic import BaseModel
from typing import Optional

class Song(BaseModel):
    title: str
    artist: str
    album: str
    year: int
    genre: str
    streaming_url: Optional[str] = None
