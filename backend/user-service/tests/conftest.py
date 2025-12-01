import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Override for host environment (pytest runs outside Docker)
os.environ["MONGO_INITDB_ROOT_USERNAME"] = os.getenv("MONGO_INITDB_ROOT_USERNAME", "papu")
os.environ["MONGO_INITDB_ROOT_PASSWORD"] = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "Kavinsky")
os.environ["MONGO_USER_DB"] = os.getenv("MONGO_USER_DB", "pasadena_user_db")
os.environ["MONGO_USER_HOST"] = "localhost"
os.environ["MONGO_PORT"] = "27018"

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

