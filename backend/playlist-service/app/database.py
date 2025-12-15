from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://papu:CocteauTwins@postgres_db:5432/pasadena_playlist_db")

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Metadata DB
SQLALCHEMY_METADATA_URL = os.getenv(
    "METADATA_DATABASE_URL",
    "postgresql://papu:CocteauTwins@postgres_metadata_db:5432/postgres_metadata_db"
)
metadata_engine = create_engine(SQLALCHEMY_METADATA_URL)
MetadataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=metadata_engine)
MetadataBase = declarative_base()

def get_metadata_db():
    db = MetadataSessionLocal()
    try:
        yield db
    finally:
        db.close()