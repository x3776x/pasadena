from pymongo import MongoClient

# Conexión a MongoDB dentro de Docker
client = MongoClient("mongodb://papu:Kavinsky@pasadena_mongo:27017/")
db = client['metadata_db']  # Nombre de tu base
songs_collection = db['songs']


