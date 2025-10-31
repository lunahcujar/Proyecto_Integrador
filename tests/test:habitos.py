import pytest
from httpx import AsyncClient, ASGITransport
from main import app

pytestmark = pytest.mark.asyncio(loop_scope="session")

@pytest.mark.asyncio
async def test_obtener_habitos_usuario():
    """
    Prueba el endpoint que obtiene los hábitos de un usuario por su ID.
    Espera 200 si hay hábitos o 404 si no existen.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        usuario_id = 1  # Cambia si es necesario
        response = await ac.get(f"/api/habitos/usuario/{usuario_id}")

        # Puede devolver 200 (si existen hábitos) o 404 (si no hay)
        assert response.status_code in (200, 404), f"Código inesperado: {response.status_code}"

        if response.status_code == 404:
            data = response.json()
            assert "detail" in data, "Debe incluir un mensaje de detalle en el 404"
            assert "No hay hábitos" in data["detail"], f"Detalle inesperado: {data['detail']}"
        else:
            data = response.json()
            assert isinstance(data, list), "La respuesta debe ser una lista"
            if data:  # Si hay hábitos
                habit = data[0]
                # Verifica que tenga las claves esperadas
                required_keys = {"lavarse_cara", "usar_bloqueador", "exfoliacion", "tipo_piel"}
                missing = required_keys - habit.keys()
                assert not missing, f"Faltan campos en la respuesta: {missing}"
