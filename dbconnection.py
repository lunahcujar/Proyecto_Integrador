# config/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

# URL de conexión completa proporcionada por Clever Cloud
DATABASE_URL = (
    "postgresql+asyncpg://udafrfxeywqopsnngsxy:qOpKiLpt06qQF3VFmbiSllPf7J7ZW6"
    "@byjnneiuugcgy4m2iqlh-postgresql.services.clever-cloud.com:50013/byjnneiuugcgy4m2iqlh"
)

# Crear el motor de conexión asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear la base declarativa
Base = declarative_base()

# Crear la sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context manager para obtener sesión asíncrona
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
