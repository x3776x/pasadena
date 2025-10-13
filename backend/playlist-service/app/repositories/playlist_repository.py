from sqlalchemy.orm import Session
from app import models, schemas


def get_playlist_by_id(db: Session, playlist_id: int):
    return db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()


def get_playlists_by_owner(db: Session, owner_id: int):
    return db.query(models.Playlist).filter(models.Playlist.owner_id == owner_id).all()


def create_playlist(db: Session, owner_id: int, playlist: schemas.PlaylistCreate):
    db_playlist = models.Playlist(
        name=playlist.name,
        is_public=playlist.is_public,
        owner_id=owner_id
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


def update_playlist(db: Session, playlist_id: int, playlist_update: schemas.PlaylistUpdate):
    db_playlist = get_playlist_by_id(db, playlist_id)
    if not db_playlist:
        return None
    if playlist_update.name is not None:
        db_playlist.name = playlist_update.name
    if playlist_update.is_public is not None:
        db_playlist.is_public = playlist_update.is_public
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


def delete_playlist(db: Session, playlist_id: int):
    db_playlist = get_playlist_by_id(db, playlist_id)
    if not db_playlist:
        return False
    db.delete(db_playlist)
    db.commit()
    return True


def add_like(db: Session, user_id: int, playlist_id: int):
    existing = db.query(models.PlaylistLike).filter(
        models.PlaylistLike.user_id == user_id,
        models.PlaylistLike.playlist_id == playlist_id
    ).first()
    if existing:
        return existing
    like = models.PlaylistLike(user_id=user_id, playlist_id=playlist_id)
    db.add(like)
    db.commit()
    return like


def remove_like(db: Session, user_id: int, playlist_id: int):
    existing = db.query(models.PlaylistLike).filter(
        models.PlaylistLike.user_id == user_id,
        models.PlaylistLike.playlist_id == playlist_id
    ).first()
    if not existing:
        return False
    db.delete(existing)
    db.commit()
    return True


def is_liked(db: Session, user_id: int, playlist_id: int) -> bool:
    existing = db.query(models.PlaylistLike).filter(
        models.PlaylistLike.user_id == user_id,
        models.PlaylistLike.playlist_id == playlist_id
    ).first()
    return existing is not None

def get_active_playlists(db: Session):
    return db.query(models.Playlist).filter(models.Playlist.is_active == True).all()

def get_all_playlists(db: Session):
    return db.query(models.Playlist).all()
