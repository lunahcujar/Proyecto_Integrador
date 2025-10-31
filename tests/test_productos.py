import pytest
from httpx import AsyncClient, ASGITransport
from main import app

pytestmark = pytest.mark.asyncio(loop_scope="session")

@pytest.mark.asyncio
async def test_obtener_productos_usuario():
    """
    Prueba el endpoint que obtiene los productos recomendados según el usuario.
    Puede devolver 200 si hay productos o 404 si no hay hábitos o tipo de piel definido.
    """

    # 🧩 Configuración del cliente de pruebas
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        usuario_id = 1  # Cambia si es necesario según tu BD

        # 🔹 Petición GET al endpoint
        response = await ac.get(f"/api/productos/usuario/{usuario_id}")

        # 🔹 Verifica código de estado válido
        assert response.status_code in (200, 404), f"Status inesperado: {response.status_code}"

        # 🔹 Si hay productos, validar estructura
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "La respuesta debe ser una lista"

            if data:  # Si hay al menos un producto
                producto = data[0]
                required_keys = {"product_name", "product_type", "clean_ingreds", "product_url", "image_url"}
                missing = required_keys - producto.keys()
                assert not missing, f"Faltan campos en la respuesta: {missing}"

        # 🔹 Si no hay productos, validar mensaje de error
        elif response.status_code == 404:
            data = response.json()
            assert "detail" in data, "La respuesta 404 debe contener un campo 'detail'"
            assert isinstance(data["detail"], str), "El campo 'detail' debe ser texto"
