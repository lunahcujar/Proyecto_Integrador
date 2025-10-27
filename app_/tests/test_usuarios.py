import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app_.main import app
from app_.api.models import User
from app_.core.dbconnection import get_db  # <- Importa la función directamente

app.dependency_overrides[get_db] = _mock_get_db  # <- Usa la función como key


# --- Datos de prueba ---
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
        self.execute = AsyncMock()
        self.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)

# --- Fixture para FastAPI dependency override ---
@pytest.fixture
def override_get_db():
    async def _mock_get_db():
        db = MockDB()
        try:
            yield db
        finally:
            await db.close()
    app.dependency_overrides[get_db] = _mock_get_db
    return _mock_get_db


@pytest.mark.asyncio
async def test_registrar_usuario(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/usuarios", json=json_data)

    assert response.status_code == 200
    json_resp = response.json()
    assert "message" in json_resp
    assert "usuario" in json_resp["message"].lower()

    # Verificar que se llamaron add y commit
    db_instance = await anext(override_get_db())
    assert db_instance.add.called
    assert db_instance.commit.called
