from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .song_model import Song, Album, Genre, Base # importa tus modelos aquí