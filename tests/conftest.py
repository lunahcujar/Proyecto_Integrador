import pytest_asyncio
from httpx import AsyncClient
from app_.main import app

@pytest_asyncio.fixture
async def client():
    """Cliente HTTP asíncrono para pruebas."""
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac
