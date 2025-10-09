from pymongo import MongoClient, ASCENDING
import os

def get_db(uri=None, db_name="pasadena"):
    # Si no se pasa URI, tomar la de la variable de entorno o usar la de Docker con auth
    if not uri:
        uri = os.getenv("MONGO_URI", "mongodb://papu:Kavinsky@mongodb:27017/pasadena")
    client = MongoClient(uri)
    db = client[db_name]
    return db

def create_indexes(db):
    db.songs.create_index([("song_id", ASCENDING)], unique=True)
    db.songs.create_index([("artist", ASCENDING)])
    db.songs.create_index([("album", ASCENDING)])
    db.songs.create_index([("genre", ASCENDING)])
