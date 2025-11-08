import uuid
import grpc
from proto import metadata_pb2 as pb2
from proto import metadata_pb2_grpc as pb2_grpc

from models.mongo import save_audio, delete_audio
from models.song_model import Song
from utils import execute_db_query as postgres_db


class MetadataServiceServicer(pb2_grpc.MetadataServiceServicer):
    async def AddSong(self, request, context):
        """Guarda una canción (metadatos en Postgres, audio en Mongo)."""
        try:
            song_id = str(uuid.uuid4())
            song_table = Song.__table__  # ✅ Usamos la tabla del modelo

            # Guardar metadatos
            query = song_table.insert().values(
                song_id=song_id,
                title=request.title,
                artist=request.artist,
                album=request.album,
                year=request.year,
                genre=request.genre,
                duration=request.duration
            )
            await postgres_db(query)

            # Guardar archivo en Mongo
            save_audio(song_id, request.file_data)

            return pb2.SongResponse(
                song_id=song_id,
                title=request.title,
                artist=request.artist,
                album=request.album,
                year=request.year,
                genre=request.genre,
                duration=request.duration,
                album_cover=request.album_cover
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SongResponse()

    async def GetSongMetadata(self, request, context):
        """Obtiene los metadatos de Postgres."""
        song_table = Song.__table__  # ✅ Igual aquí
        query = song_table.select().where(song_table.c.song_id == request.song_id)
        song = await postgres_db.fetch_one(query)

        if not song:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Song not found")
            return pb2.SongResponse()

        return pb2.SongResponse(
            song_id=song["song_id"],
            title=song["title"],
            artist=song["artist"],
            album=song["album"],
            year=song["year"],
            genre=song["genre"],
            duration=song["duration"],
            album_cover=b""  # opcional
        )

    async def GetSongPath(self, request, context):
        """Retorna una ruta virtual o ID (Mongo)."""
        return pb2.SongPathResponse(path=f"/songs/{request.song_id}")

    async def DeleteSong(self, request, context):
        """Elimina la canción de ambos sistemas."""
        try:
            song_table = Song.__table__
            # Eliminar en Postgres
            query = song_table.delete().where(song_table.c.song_id == request.song_id)
            await postgres_db.execute(query)

            # Eliminar en Mongo
            delete_audio(request.song_id)

            return pb2.DeleteResponse(success=True, message="Deleted successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.DeleteResponse(success=False, message=str(e))
