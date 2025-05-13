from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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

# Dependency que se inyecta con Depends()
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
