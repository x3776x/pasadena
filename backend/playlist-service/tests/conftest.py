import os
os.environ["SECRET_KEY"] = "key4testing"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
import pytest
from app.dependencies.dependencies import oauth2_scheme

# Base de datos de prueba SQLite en archivo local
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Crear motor y sesión de prueba
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Crea y destruye una base temporal para cada prueba."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Crea un cliente de prueba FastAPI usando la sesión temporal."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def mock_oauth(monkeypatch):
    """Mockea el esquema OAuth2 para que acepte cualquier token."""
    def fake_oauth2_scheme():
        return "fake-token"
    monkeypatch.setattr("app.dependencies.dependencies.oauth2_scheme", fake_oauth2_scheme)

