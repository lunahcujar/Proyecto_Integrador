# app_/tests/test_usuarios.py
from fastapi.testclient import TestClient
from app_.main import app
from app_.core.dbconnection import get_db
from unittest.mock import AsyncMock

import pytest

json_data = {
    "name": "Prueba",
    "mail": "testuser@example.com",
    "quiz": {
        "pregunta_1": True,
        "pregunta_2": False,
        "pregunta_3": "1 vez/semana",
        "pregunta_4": "seca",
        "pregunta_5": "hidratar",
        "pregunta_6": "25"
    }
}

# --- Mock DB ---
class MockDB:
    def __init__(self):
        self.add = AsyncMock()
        self.commit = AsyncMock()
        self.flush = AsyncMock()
        self.close = AsyncMock()
        # Simula que no hay usuario existente
        self.execute = AsyncMock()
        self.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)

@pytest.fixture
def override_get_db():
    async def _mock_get_db():
        db = MockDB()
        try:
            yield db
        finally:
            await db.close()
    return _mock_get_db

def test_registrar_usuario(override_get_db):
    # Override de la DB
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    response = client.post("/api/usuarios", json=json_data)
    assert response.status_code == 200
    json_resp = response.json()
    assert "usuario" in json_resp["message"].lower()
