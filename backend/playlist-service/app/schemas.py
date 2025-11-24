from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Playlist schemas
class PlaylistBase(BaseModel):
    name: str
    is_public: bool = False


class PlaylistCreate(PlaylistBase):
    name: str
    is_public: bool
    playlist_cover: str | None = None


class PlaylistUpdate(BaseModel):
    name: str | None = None
    is_public: bool | None = None
    playlist_cover: str | None = None


class Playlist(PlaylistBase):
    id: int
    owner_id: int
    playlist_cover: str | None = None

    class Config:
        from_attributes = True


# === PLAYLIST LIKES ===

class PlaylistLike(BaseModel):
    user_id: int
    playlist_id: int
    created_at: datetime | None = None

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
