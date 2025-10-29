import pytest
from httpx import AsyncClient
from app_.main import app
from app_.core.dbconnection import get_db

@pytest.mark.asyncio
async def test_registrar_usuario(async_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "name": "Luna Test",
            "email": "luna_test@example.com",
            "quiz": {
                "pregunta_1": "sí",
                "pregunta_2": "no",
                "pregunta_3": "1 vez por semana",
                "pregunta_4": "seca",
                "pregunta_5": "hidratar",
                "pregunta_6": "25"
            }
        }
        response = await ac.post("/api/usuarios", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "Usuario y hábitos registrados" in result["message"]

@pytest.mark.asyncio
async def test_obtener_usuario(async_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        email = "luna_test@example.com"
        response = await ac.get(f"/api/usuarios?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert data["correo"] == email
