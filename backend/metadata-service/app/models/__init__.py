from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .song_model import Song, Base # importa tus modelos aquí