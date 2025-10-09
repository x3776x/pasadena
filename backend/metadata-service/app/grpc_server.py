import grpc
from proto import metadata_pb2 as pb2
from proto import metadata_pb2_grpc as pb2_grpc
from models import get_db
from utils import extract_metadata, generate_song_id
import os

class MetadataServiceServicer(pb2_grpc.MetadataServiceServicer):
    def __init__(self):
        self.db = get_db().songs  # Colección de canciones en MongoDB

    def AddSong(self, request, context):
        """Sube una canción y devuelve sus metadatos en SongResponse."""
        try:
            song_id = generate_song_id()
            os.makedirs("/data/music", exist_ok=True)
            file_path = f"/data/music/{song_id}.mp3"

            # Guardar archivo
            with open(file_path, "wb") as f:
                f.write(request.file_data)

            # Extraer metadatos
            metadata = extract_metadata(file_path)

            # Valores por defecto si no hay metadatos
            if not metadata or not isinstance(metadata, dict):
                metadata = {
                    "title": "no data",
                    "artist": "no data",
                    "album": "no data",
                    "year": 0,
                    "genre": "no data",
                    "duration": 0.0,
                    "album_cover": b""
                }

            # Crear documento MongoDB
            song_document = {
                "song_id": song_id,
                "file_path": file_path,
                "title": metadata.get("title", "no data"),
                "artist": metadata.get("artist", "no data"),
                "album": metadata.get("album", "no data"),
                "year": str(metadata.get("year", 0)),  # string según proto
                "genre": metadata.get("genre", "no data"),
                "duration": float(metadata.get("duration", 0)),
                "album_cover": metadata.get("album_cover", b"")
            }

            self.db.insert_one(song_document)

            # Retornar respuesta
            return pb2.SongResponse(
                song_id=song_id,
                title=song_document["title"],
                artist=song_document["artist"],
                album=song_document["album"],
                year=song_document["year"],
                genre=song_document["genre"],
                duration=song_document["duration"],
                album_cover=song_document["album_cover"]
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            # Retornar SongResponse vacío en caso de error
            return pb2.SongResponse(
                song_id="",
                title="",
                artist="",
                album="",
                year="0",
                genre="",
                duration=0.0,
                album_cover=b""
            )

    def GetSongMetadata(self, request, context):
        """Obtiene los metadatos de una canción existente usando SongResponse."""
        try:
            song = self.db.find_one({"song_id": request.song_id})
            if not song:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Song not found")
                return pb2.SongResponse(
                    song_id="",
                    title="",
                    artist="",
                    album="",
                    year="0",
                    genre="",
                    duration=0.0,
                    album_cover=b""
                )

            return pb2.SongResponse(
                song_id=song.get("song_id", ""),
                title=song.get("title", ""),
                artist=song.get("artist", ""),
                album=song.get("album", ""),
                year=str(song.get("year", "0")),
                genre=song.get("genre", ""),
                duration=float(song.get("duration", 0)),
                album_cover=song.get("album_cover", b"")
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SongResponse(
                song_id="",
                title="",
                artist="",
                album="",
                year="0",
                genre="",
                duration=0.0,
                album_cover=b""
            )
