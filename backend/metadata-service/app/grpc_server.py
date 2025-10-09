import grpc
import app.proto.metadata_pb2 as pb2
import app.proto.metadata_pb2_grpc as pb2_grpc
from models import get_db
from utils import extract_metadata, generate_song_id
import os

class MetadataServiceServicer(pb2_grpc.MetadataServiceServicer):
    def __init__(self):
        self.db = get_db().songs

    def AddSong(self, request, context):
        song_id = generate_song_id()
        file_path = f"/data/music/{song_id}.mp3"
        with open(file_path, "wb") as f:
            f.write(request.file_data)
        metadata = extract_metadata(file_path)
        metadata["song_id"] = song_id
        metadata["file_path"] = file_path
        self.db.insert_one(metadata)
        return pb2.SongUploadResponse(status="success", song_id=song_id)

    def GetSongMetadata(self, request, context):
        song = self.db.find_one({"song_id": request.song_id})
        if not song:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Song not found")
            return pb2.SongMetadataResponse()
        return pb2.SongMetadataResponse(
            song_id=song["song_id"],
            title=song["title"],
            artist=song["artist"],
            album=song["album"],
            year=int(song["year"]),
            genre=song["genre"],
            duration=float(song["duration"]),
            album_cover=song["album_cover"]
        )
