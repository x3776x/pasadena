from pymongo import MongoClient

# Conexión a MongoDB dentro de Docker
client = MongoClient("mongodb://papu:Kavinsky@pasadena_mongo:27017/")
db = client['metadata_db']  # Nombre de tu base
songs_collection = db['songs']

# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text # Para consultas SQL crudas

# Tu URL modificada para ser asíncrona
DATABASE_URL_ASYNC = "postgresql+asyncpg://papu:CocteauTwins@postgres_metadata_db:5432/postgres_metadata_db"

# 1. Crear el Motor Asíncrono
engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=True, # Muestra el SQL generado en la consola
)

# 2. Definir la factoría de Sesiones Asíncronas
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False # Práctica recomendada para sesiones asíncronas
)