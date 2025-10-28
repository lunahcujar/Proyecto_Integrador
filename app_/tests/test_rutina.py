# app_/tests/test_rutina.py
from fastapi.testclient import TestClient
from app_.main import app
from app_.core.dbconnection import get_db
import pytest

# --- Mock del cliente Supabase ---
class MockSupabaseClient:
    def table(self, name):
        self.table_name = name
        return self

    def select(self, *args, **kwargs):
        return self

    def eq(self, column, value):
        self.column = column
        self.value = value
        return self

    def execute(self):
        if self.value == "juan@hotmail.com":
            return type("MockResponse", (), {
                "data": [{"id": 1, "name": "Juan", "mail": "juan@hotmail.com"}],
                "error": None
            })()
        return type("MockResponse", (), {"data": [], "error": None})()

# --- Mock DB ---
@pytest.fixture
def override_get_db():
    async def _mock_get_db():
        class MockDB:
            async def add(self, *args, **kwargs):
                pass

            async def commit(self):
                pass

            async def execute(self, *args, **kwargs):
                query_str = str(args[0]).lower()

                class MockResult:
                    def scalars(self_inner):
                        class MockScalar:
                            def first(self_inner_2):
                                # ✅ Detectar tipo de consulta
                                if "from user" in query_str:
                                    class MockUser:
                                        def __init__(self):
                                            self.id = 1
                                            self.nombre = "Juan"
                                            self.correo = "juan@hotmail.com"
                                    return MockUser()
                                elif "from habito" in query_str:
                                    class MockHabito:
                                        def __init__(self):
                                            self.id = 1
                                            self.usuario_id = 1
                                            self.tipo_piel = "grasa"
                                    return MockHabito()
                                return None
                        return MockScalar()
                return MockResult()
        yield MockDB()
    return _mock_get_db

# --- Test principal ---
def test_rutina_usuario_existente(monkeypatch, override_get_db):
    import app_.core.supabase_config as supabase_module

    # ✅ Parchear el cliente Supabase
    monkeypatch.setattr(supabase_module, "supabase", MockSupabaseClient())

    # ✅ Sobrescribir dependencia DB
    app.dependency_overrides[get_db] = override_get_db

    # ✅ Cliente de prueba
    client = TestClient(app)
    response = client.get("/api/rutina?email=juan@hotmail.com")

    # --- Validar respuesta ---
    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()
    assert "rutina" in data or "mensaje" in data, f"Respuesta inesperada: {data}"
