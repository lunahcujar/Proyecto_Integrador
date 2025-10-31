import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_obtener_habitos_usuario(async_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # suponiendo que el usuario 1 ya existe
        response = await ac.get("/api/habitos/usuario/1")
        if response.status_code == 404:
            assert "No hay hábitos" in response.json()["detail"]
        else:
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert "lavarse_cara" in data[0]
