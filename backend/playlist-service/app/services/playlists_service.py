from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.repositories import playlist_repository


class PlaylistService:
    def __init__(self, db: Session):
        self.db = db

    def create_playlist(self, owner_id: int, playlist_data: schemas.PlaylistCreate):
        if not playlist_data.name or len(playlist_data.name) < 1:
            raise ValueError("Playlist name required")
        return playlist_repository.create_playlist(self.db, owner_id, playlist_data)

    def update_playlist(self, playlist_id: int, playlist_update: schemas.PlaylistUpdate):
        pl = playlist_repository.update_playlist(self.db, playlist_id, playlist_update)
        if not pl:
            raise ValueError("Playlist not found")
        return pl

    def delete_playlist(self, playlist_id: int):
        success = playlist_repository.delete_playlist(self.db, playlist_id)
        if not success:
            raise ValueError("Playlist not found")
        return success

    def add_like(self, user_id: int, playlist_id: int):
        return playlist_repository.add_like(self.db, user_id, playlist_id)

    def remove_like(self, user_id: int, playlist_id: int):
        return playlist_repository.remove_like(self.db, user_id, playlist_id)
    
    def get_active_playlists(self):
        return playlist_repository.get_active_playlists(self.db)

    def get_all_playlists(self):
        return playlist_repository.get_all_playlists(self.db)



def get_playlist_service(db: Session = Depends(get_db)):
    return PlaylistService(db)
