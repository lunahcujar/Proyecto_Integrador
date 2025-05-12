from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# URL de conexión completa proporcionada por Clever
DATABASE_URL = "postgresql://udafrfxeywqopsnngsxy:qOpKiLpt06qQF3VFmbiSllPf7J7ZW6@byjnneiuugcgy4m2iqlh-postgresql.services.clever-cloud.com:50013/byjnneiuugcgy4m2iqlh"

# Crear el motor de conexión asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear la sesión
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context manager para obtener sesión
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

# Motor síncrono si es necesario (por si necesitas usarlo en algunas partes de tu código)
def get_engine():
    return engine
