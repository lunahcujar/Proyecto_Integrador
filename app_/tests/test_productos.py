import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_obtener_productos_usuario(async_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/productos/usuario/1")
        if response.status_code == 404:
            assert "Tipo de piel" in response.json()["detail"] or "No hay hábitos" in response.json()["detail"]
        else:
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            if data:
                assert "product_name" in data[0]
