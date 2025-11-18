from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles

from app import schemas
from app.database import get_db
from app.security import get_current_user
from app.services.playlists_service import PlaylistService, get_playlist_service
from app.repositories.playlist_repository import get_playlist_by_id
from app import schemas as playlist_schemas

app = FastAPI(title="Playlist Service")


# --- API Endpoints ---
@app.post("/playlist", response_model=playlist_schemas.Playlist)
def create_playlist(
    playlist: playlist_schemas.PlaylistCreate,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    try:
        return playlist_service.create_playlist(current_user["user_id"], playlist)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/playlist/{playlist_id}", response_model=playlist_schemas.Playlist)
def update_playlist(
    playlist_id: int,
    playlist_update: playlist_schemas.PlaylistUpdate,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    # Access control: ensure current_user owns the playlist
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    try:
        return playlist_service.update_playlist(playlist_id, playlist_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete("/playlist/{playlist_id}")
def delete_playlist(
    playlist_id: int,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    try:
        pl.is_active = False
        playlist_service.db.commit()
        return {"message": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/playlist/{playlist_id}/like")
def like_playlist(
    playlist_id: int,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    return playlist_service.add_like(current_user["user_id"], playlist_id)


@app.post("/playlist/{playlist_id}/unlike")
def unlike_playlist(
    playlist_id: int,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    success = playlist_service.remove_like(current_user["user_id"], playlist_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    return {"message": "unliked"}


@app.get("/playlist/active", response_model=list[playlist_schemas.Playlist])
def get_active_playlists(
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """Obtiene todas las playlists activas."""
    return playlist_service.get_active_playlists()


@app.get("/playlist/all", response_model=list[playlist_schemas.Playlist])
def get_all_playlists(
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """Obtiene todas las playlists, activas e inactivas."""
    return playlist_service.get_all_playlists()


# === PLAYLIST SONGS ===

@app.post("/playlist/{playlist_id}/songs")
def add_song_to_playlist(
    playlist_id: int,
    song: playlist_schemas.PlaylistSongCreate,  # schema con song_id y position
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    try:
        return playlist_service.add_song_to_playlist(playlist_id, song.song_id, song.position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/playlist/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(
    playlist_id: int,
    song_id: str,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    try:
        playlist_service.remove_song_from_playlist(playlist_id, song_id)
        return {"message": "song removed"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/playlist/{playlist_id}/songs", response_model=list[playlist_schemas.PlaylistSong])
def get_songs_in_playlist(
    playlist_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """
    Devuelve todas las canciones de una playlist ordenadas por posición.
    """
    return playlist_service.get_songs_in_playlist(playlist_id)


@app.put("/playlist/{playlist_id}/songs/{song_id}")
def update_song_position(
    playlist_id: int,
    song_id: str,
    update_data: playlist_schemas.PlaylistSongUpdate,  # schema con new_position
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    try:
        return playlist_service.update_song_position(playlist_id, song_id, update_data.position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete("/playlist/{playlist_id}/songs")
def clear_playlist(
    playlist_id: int,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """
    Elimina todas las canciones de una playlist.
    """
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    result = playlist_service.clear_playlist(playlist_id)
    return {"message": f"{result['deleted']} songs deleted"}
