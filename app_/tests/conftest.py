import pytest
from app_.core.dbconnection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def async_session():
    """Simula una sesión de BD para pruebas."""
    async def override_get_db():
        async with AsyncSession() as session:
            yield session
    return override_get_db
