import grpc
from stubs import metadata_pb2 as pb2
from stubs import metadata_pb2_grpc as pb2_grpc

def send_song(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    request = pb2.AddSongRequest(file_data=file_data)
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = pb2_grpc.MetadataServiceStub(channel)
        response = stub.AddSong(request)
        print("Song uploaded with ID:", response.song_id)

if __name__ == "__main__":
    send_song("hola.mp3")