import os
os.environ["SECRET_KEY"] = "key4testing"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, get_metadata_db, Base, MetadataBase
from unittest.mock import patch
from app import models
from app.security import get_current_user


# ============================================
# BASE DE DATOS DE PRUEBA (SQLite)
# ============================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base.metadata.create_all(bind=engine)
MetadataBase.metadata.create_all(bind=engine)


@pytest.fixture
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def override_get_metadata_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_metadata_db] = override_get_metadata_db


# ============================================
# SESIÓN DB TEMPORAL POR PRUEBA
# ============================================
@pytest.fixture(scope="function")
def db_session():
    # Borra y recrea las tablas en cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    MetadataBase.metadata.drop_all(bind=engine)
    MetadataBase.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()




@pytest.fixture(autouse=True)
def override_current_user():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": 1, "role_id": 2}


# ============================================
# CLIENTE FASTAPI USANDO DB DE PRUEBA
# ============================================
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass


    def override_get_metadata_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_metadata_db] = override_get_metadata_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
