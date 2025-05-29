from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncio

# URL de conexión completa y correcta (debes usar el dialecto asyncpg para async)
DATABASE_URL = "postgresql+asyncpg://ux2fcjvg3newt9bt9rwp:UXZu0qLFkAUJL0ZlxZctddIxLwyMx9@bbmcq5stul9kujtseek7-postgresql.services.clever-cloud.com:50013/bbmcq5stul9kujtseek7"


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
