from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/pasadena_db")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["pasadena_db"]
songs_collection = mongo_db["songs"]

def save_audio(song_id: str, audio_bytes: bytes):
    """Guarda un archivo de audio en MongoDB."""
    songs_collection.insert_one({
        "_id": song_id,
        "audio_data": audio_bytes
    })

def delete_audio(song_id: str):
    """Elimina el archivo de audio de MongoDB."""
    songs_collection.delete_one({"_id": song_id})
