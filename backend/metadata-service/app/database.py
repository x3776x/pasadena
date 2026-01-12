from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Tu URL modificada para ser asíncrona
DATABASE_URL_ASYNC = "postgresql+asyncpg://papu:CocteauTwins@postgres_metadata_db:5432/postgres_metadata_db"

# Crear el motor asíncrono
engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=True,  # Muestra el SQL generado en la consola
)

# Definir la factoría de sesiones asíncronas
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Práctica recomendada para sesiones asíncronas
)

# Declaración única de Base
Base = declarative_base()

# Aquí va tu MongoDB (sin afectar la base de datos SQLAlchemy)
from pymongo import MongoClient

client = MongoClient("mongodb://papu:Kavinsky@pasadena_mongo:27017/")
db = client['metadata_db']
songs_collection = db['songs']
