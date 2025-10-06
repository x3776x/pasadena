
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import os
from  .database import db

router = APIRouter()

@router.get("/stream/{song_id}")
async def stream_song(song_id: str):
    # Busca la canción en MongoDB
    song = await db.songs.find_one({"song_id": song_id})
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    file_path = song["filepath"]

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # Streaming parcial con StreamingResponse
    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f

    return StreamingResponse(iterfile(), media_type="audio/mpeg")
