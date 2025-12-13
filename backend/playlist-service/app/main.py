from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
from pathlib import Path

from app import schemas
from app.database import get_db
from app.security import get_current_user
from app.services.playlists_service import PlaylistService, get_playlist_service
from app.repositories.playlist_repository import get_playlist_by_id
from app import schemas as playlist_schemas
import os
import uuid

app = FastAPI(title="Playlist Service")

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

STATIC_PLAYLISTS_DIR = Path("/app/static")
STATIC_PLAYLISTS_DIR.mkdir(parents=True, exist_ok=True)

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


@app.post("/playlist/{playlist_id}/like", response_model=playlist_schemas.PlaylistLike)
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


@app.get("/playlist/public", response_model=list[playlist_schemas.Playlist])
def get_public_playlists(
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """Obtiene todas las playlists publicas."""
    return playlist_service.get_public_playlists()


@app.get("/playlist/{owner_id}/public", response_model=list[playlist_schemas.Playlist])
def get_public_playlists_by_owner(
    owner_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """Obtiene todas las playlists publicas."""
    return playlist_service.get_public_playlists_by_owner(owner_id)


@app.get("/playlist/{playlist_id}", response_model=playlist_schemas.Playlist)
def get_playlist_id_endpoint(
    playlist_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    return playlist_service.get_playlist_by_id(playlist_id)


@app.get("/playlist/{owner_id}/owner", response_model=list[playlist_schemas.Playlist])
def get_playlists_by_owner(
    owner_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    return playlist_service.get_playlists_by_owner(owner_id)


@app.get("/playlist/{owner_id}/active", response_model=list[playlist_schemas.Playlist])
def get_active_playlists_by_owner(
    owner_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """
    Obtiene todas las playlists activas (is_active = True) de un usuario,
    sin importar visibilidad (públicas y privadas).
    """
    return playlist_service.get_active_playlists_by_owner(owner_id)


@app.get("/playlist/{owner_id}/active/public", response_model=list[playlist_schemas.Playlist])
def get_active_public_playlists_by_owner(
    owner_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """
    Obtiene todas las playlists activas y públicas (is_active = True y public = True)
    de un usuario.
    """
    return playlist_service.get_active_public_playlists_by_owner(owner_id)


@app.get("/playlist/active/public", response_model=list[playlist_schemas.Playlist])
def get_active_public_playlists(
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """
    Obtiene todas las playlists activas y públicas de todos los usuarios.
    """
    return playlist_service.get_active_public_playlists()


@app.get("/playlist/{user_id}/liked-playlists", response_model=list[playlist_schemas.Playlist])
def get_playlists_liked_by_user(
    user_id: int,
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    """Obtiene todas las playlists, activas e inactivas."""
    return playlist_service.get_playlists_liked_by_user(user_id)



@app.post("/playlist/{playlist_id}/cover", response_model=playlist_schemas.Playlist)
async def upload_playlist_cover(
    playlist_id: int,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    # 1) Verificar permisos y existencia
    pl = get_playlist_by_id(playlist_service.db, playlist_id)
    if pl is None or pl.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # 2) Validar tipo de archivo
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # 3) Generar nombre único y ruta de guardado
    _, ext = os.path.splitext(file.filename)
    # si ext está vacío, puedes forzar .png por ejemplo:
    if not ext:
        ext = ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = STATIC_PLAYLISTS_DIR / filename

    # 4) Guardar archivo de forma segura
    try:
        content = await file.read()
        save_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # 5) (Opcional) Borrar cover anterior si existía
    try:
        old_cover = pl.playlist_cover
        if old_cover:
            old_path = STATIC_PLAYLISTS_DIR / old_cover
            # evita borrar si es igual al nuevo o si no existe
            if old_path.exists() and old_cover != filename:
                try:
                    old_path.unlink()
                except Exception:
                    # no crítico, solo un log en producción
                    pass
    except Exception:
        # no queremos que la limpieza bloquee la respuesta
        pass

    # 6) Actualizar en BD (usando tu servicio y schema de update)
    updated_playlist = playlist_service.update_playlist(
        playlist_id,
        playlist_schemas.PlaylistUpdate(playlist_cover=filename)
    )

    return updated_playlist


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

    if not playlist_service.song_exists(song.song_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

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


@app.delete("/playlist/songs/{song_id}")
def remove_song_references_from_playlists(
    song_id: str,
    current_user = Depends(get_current_user),
    playlist_service: PlaylistService = Depends(get_playlist_service)
):
    try:
        deleted_count = playlist_service.remove_song_references_from_playlists(song_id)
        return {"message": f"song references removed from {deleted_count} playlists"}
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
