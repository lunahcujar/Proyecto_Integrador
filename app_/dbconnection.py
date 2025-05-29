from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncio

# URL de conexión completa y correcta (debes usar el dialecto asyncpg para async)
DATABASE_URL = "postgresql://uwwaoyysz9b8uw8oryhz:lF9ljHVTelf8mU2ST8glvH3E7SaZUK@bmx3ykywpgi0a3ffcvnm-postgresql.services.clever-cloud.com:50013/bmx3ykywpgi0a3ffcvnm"

# Crear el motor de conexión asincrónica
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=2, max_overflow=0)

# Crear la base declarativa
Base = declarative_base()

# Crear la sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency que se inyecta con Depends() en FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session  # La sesión se cierra automáticamente al salir del contexto
