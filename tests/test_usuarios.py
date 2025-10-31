import pytest
from httpx import AsyncClient, ASGITransport
from main import app

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.asyncio
async def test_registrar_usuario():
    """
    🧪 Prueba el registro de un nuevo usuario junto con su test de hábitos.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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

        # Enviamos solicitud de registro
        response = await ac.post("/api/usuarios", json=data)

        # ✅ Verificamos que devuelva un código esperado
        assert response.status_code in (200, 201), f"❌ Error al registrar usuario: {response.text}"

        # ✅ Validamos estructura de la respuesta
        result = response.json()
        assert isinstance(result, dict), "La respuesta debe ser un diccionario"
        assert "email" in result, "El campo 'email' no está en la respuesta"
        assert result["email"] == data["email"], "El email devuelto no coincide"


@pytest.mark.asyncio
async def test_obtener_usuario():
    """
    🧪 Prueba la obtención de un usuario registrado por email.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = "luna_test@example.com"

        # Solicitamos usuario por email
        response = await ac.get(f"/api/usuarios?email={email}")

        # ✅ Puede devolver 200 (existe) o 404 (no existe)
        assert response.status_code in (200, 404), f"❌ Error al consultar usuario: {response.text}"

        if response.status_code == 200:
            usuario = response.json()
            assert isinstance(usuario, dict), "La respuesta debe ser un diccionario"
            assert "email" in usuario, "Falta el campo 'email'"
            assert usuario["email"] == email, "El email no coincide con el esperado"
        else:
            data = response.json()
            assert "detail" in data, "La respuesta 404 debe tener un campo 'detail'"
            assert isinstance(data["detail"], str), "El campo 'detail' debe ser texto"
