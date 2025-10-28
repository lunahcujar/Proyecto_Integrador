# app_/tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from app_.api.models import User, Habito

@pytest.fixture
def override_get_db():
    async def _mock_get_db():
        db = AsyncMock()

        # ✅ Usuario simulado que sí existirá
        fake_user = User(id=1, nombre="Juan", correo="juan@hotmail.com")
        fake_habito = Habito(id=1, usuario_id=1, tipo_piel="grasa")

        # ✅ Función mock que imita db.execute()
        async def mock_execute(query):
            q = str(query).lower()

            # --- Buscar consultas de usuario ---
            if "user" in q or "usuario" in q:
                class MockResult:
                    def scalars(self_inner):
                        class Scalar:
                            def first(self_inner_2):
                                return fake_user
                        return Scalar()
                return MockResult()

            # --- Buscar consultas de hábito ---
            elif "habito" in q or "habit" in q:
                class MockResult:
                    def scalars(self_inner):
                        class Scalar:
                            def first(self_inner_2):
                                return fake_habito
                        return Scalar()
                return MockResult()

            # --- En otros casos ---
            return AsyncMock()

        db.execute.side_effect = mock_execute
        yield db

    return _mock_get_db
