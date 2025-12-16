import pytest
from app.metadata_service import MetadataServiceServicer

class FakeContext:
    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


@pytest.fixture
def service():
    """Instancia del servicio gRPC"""
    return MetadataServiceServicer()


@pytest.fixture
def fake_context():
    """Contexto falso de gRPC"""
    return FakeContext()
