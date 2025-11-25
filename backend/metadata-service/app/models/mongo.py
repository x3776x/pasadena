from pymongo import MongoClient
import gridfs
import os

# -----------------------------------------------------------
# URI con usuario y contraseña para autenticación
# -----------------------------------------------------------
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://papu:Kavinsky@mongodb:27017/pasada_db?authSource=admin"
)

# -----------------------------------------------------------
# Conexión a MongoDB y GridFS
# -----------------------------------------------------------
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["pasada_db"]
fs = gridfs.GridFS(mongo_db)

# -----------------------------------------------------------
# Función para guardar audio en GridFS
# -----------------------------------------------------------
def save_audio(song_id: str, audio_bytes: bytes):
    """Guarda un archivo de audio en MongoDB usando GridFS.
       Si el archivo ya existe, lo reemplaza."""

    # 1. Eliminar cualquier archivo existente con el mismo song_id
    existing = fs.find({"filename": song_id})
    for file in existing:
        fs.delete(file._id)

    # 2. Guardar el archivo nuevo en GridFS
    fs.put(audio_bytes, filename=song_id)
    print(f"✅ Audio guardado correctamente con filename={song_id}")


# -----------------------------------------------------------
# Función para eliminar audio en GridFS
# -----------------------------------------------------------
def delete_audio(song_id: str):
    """Elimina un archivo de GridFS por filename."""
    existing = fs.find({"filename": song_id})
    for file in existing:
        fs.delete(file._id)
    print(f"🗑️ Audio eliminado con filename={song_id}")
