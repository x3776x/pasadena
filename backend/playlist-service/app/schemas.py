from enum import Enum
from pydantic import BaseModel, EmailStr, Field

# Playlist schemas
class PlaylistBase(BaseModel):
    name: str
    is_public: bool = False


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(BaseModel):
    name: str | None = None
    is_public: bool | None = None


class Playlist(PlaylistBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# === PLAYLIST SONGS ===

class PlaylistSongBase(BaseModel):
    song_id: str
    position: int

class PlaylistSongCreate(PlaylistSongBase):
    pass

class PlaylistSongUpdate(BaseModel):
    position: int

class PlaylistSong(PlaylistSongBase):
    playlist_id: int

    class Config:
        from_attributes = True
