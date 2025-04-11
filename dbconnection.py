from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# URL de conexión de ejemplo (ajústala a tu configuración de base de datos)
DATABASE_URL = "sqlite+aiosqlite:///./products_piel.db"  # Para SQLite asíncrono

# Crear un motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear una sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Función para obtener la sesión de base de datos de manera asíncrona
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session  # Devuelve la sesión para que la use FastAPI

# Crear un motor síncrono si lo necesitas
def get_engine():
    return engine
