import uuid
from sqlalchemy import text
import base64
from PIL import Image
import io
from database import AsyncSessionFactory

def generate_song_id():
    return str(uuid.uuid4())

async def execute_db_query(query):
    async with AsyncSessionFactory() as session:
        try:
            if isinstance(query, str):
                result = await session.execute(text(query))
            else:
                result = await session.execute(query)

            await session.commit()

            if result.returns_rows:
                rows = result.mappings().all()

                # SIEMPRE devolver lista (vacía si no hay nada)
                return rows

            elif hasattr(result, "inserted_primary_key") and result.inserted_primary_key:
                return result.inserted_primary_key[0]

            else:
                return {"message": "Comando ejecutado exitosamente."}

        except Exception as e:
            await session.rollback()
            print(f"Error al ejecutar la consulta: {e}")
            raise



def safe_int(v, default=0):
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        try:
            return int(str(v))
        except Exception:
            return default

def safe_str(v, default=""):
    return "" if v is None else str(v)

def safe_float(v, default=0.0):
    if v is None:
        return default
    try:
        return float(v)
    except Exception:
        return default

def safe_bytes_from_db(v):
    if v is None:
        return b""
    # if stored as bytes already
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    # if stored as base64 string
    if isinstance(v, str):
        try:
            return base64.b64decode(v)
        except Exception:
            return v.encode(errors="ignore")
    return b""


def resize_image(image_bytes: bytes, max_size: int = 300) -> bytes:
    """
    Redimensiona la imagen a un máximo de `max_size` píxeles en ancho o alto,
    manteniendo la proporción.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img.thumbnail((max_size, max_size))  # ajusta manteniendo proporción
        output = io.BytesIO()
        img.save(output, format="JPEG")  # o PNG según tu necesidad
        return output.getvalue()
