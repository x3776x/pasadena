import grpc
from stubs import metadata_pb2 as pb2
from stubs import metadata_pb2_grpc as pb2_grpc

def upload_song(file_path):
    """Sube una canción y devuelve el song_id."""
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.MetadataServiceStub(channel)

    with open(file_path, "rb") as f:
        file_data = f.read()

    request = pb2.AddSongRequest(file_data=file_data)
    response = stub.AddSong(request)

    print(f"✅ Canción subida. ID: {response.song_id}")
    return response.song_id


def get_song_metadata(song_id):
    """Obtiene los metadatos de una canción."""
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.MetadataServiceStub(channel)

    request = pb2.SongRequest(song_id=song_id)
    try:
        response = stub.GetSongMetadata(request)
        print("\n📄 Metadatos de la canción:")
        print(f"  ID: {response.song_id}")
        print(f"  Título: {response.title}")
        print(f"  Artista: {response.artist}")
        print(f"  Álbum: {response.album}")
        print(f"  Año: {response.year}")
        print(f"  Género: {response.genre}")
        print(f"  Duración: {response.duration} seg")
        # Album cover es bytes, opcional de mostrar
        if response.album_cover:
            print(f"  Portada: {len(response.album_cover)} bytes")
    except grpc.RpcError as e:
        print(f"❌ Error al obtener metadatos: {e.details()}")


if __name__ == "__main__":
    song_path = "mi_cancion.mp3"
    song_id = upload_song(song_path)
    if song_id:
        get_song_metadata(song_id)
