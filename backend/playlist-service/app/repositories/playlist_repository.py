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

# === MÉTODOS PARA MANEJAR LA TABLA playlist_likes ===


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

# === MÉTODOS PARA MANEJAR LA TABLA playlist_songs ===

def add_song_to_playlist(db: Session, playlist_id: int, song_id: int, position: int):
    """
    Agrega una canción a una playlist en una posición específica.
    Si ya existe, devuelve la entrada existente.
    """
    existing = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()

    if existing:
        return existing  # Ya existe

    playlist_song = models.PlaylistSong(
        playlist_id=playlist_id,
        song_id=song_id,
        position=position
    )
    db.add(playlist_song)
    db.commit()
    db.refresh(playlist_song)
    return playlist_song


def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int) -> bool:
    """
    Elimina una canción específica de una playlist.
    """
    playlist_song = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()
    if not playlist_song:
        return False

    db.delete(playlist_song)
    db.commit()
    return True


def get_songs_in_playlist(db: Session, playlist_id: int):
    """
    Devuelve todas las canciones de una playlist, ordenadas por posición.
    """
    return db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).order_by(models.PlaylistSong.position.asc()).all()


def update_song_position(db: Session, playlist_id: int, song_id: int, new_position: int):
    """
    Actualiza la posición de una canción dentro de la playlist.
    """
    playlist_song = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()

    if not playlist_song:
        return None

    playlist_song.position = new_position
    db.commit()
    db.refresh(playlist_song)
    return playlist_song


def clear_playlist(db: Session, playlist_id: int) -> int:
    """
    Elimina todas las canciones de una playlist. Devuelve cuántas eliminó.
    """
    deleted = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).delete()
    db.commit()
    return deleted


def is_song_in_playlist(db: Session, playlist_id: int, song_id: int) -> bool:
    """
    Verifica si una canción está en la playlist.
    """
    existing = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()
    return existing is not None
