import uuid
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from sqlalchemy import text

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
                return result.all()
            else:
                return {"message": "Comando ejecutado exitosamente."}
        except Exception as e:
            await session.rollback()
            print(f"Error al ejecutar la consulta: {e}")
            raise
