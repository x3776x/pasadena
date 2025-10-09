from pymongo import MongoClient, ASCENDING

def get_db(uri="mongodb://mongo:27017/", db_name="pasadena"):
    client = MongoClient(uri)
    db = client[db_name]
    return db

def create_indexes(db):
    db.songs.create_index([("song_id", ASCENDING)], unique=True)
    db.songs.create_index([("artist", ASCENDING)])
    db.songs.create_index([("album", ASCENDING)])
    db.songs.create_index([("genre", ASCENDING)])
