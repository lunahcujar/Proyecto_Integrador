from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# URL de conexión de ejemplo (cámbiala a tu configuración de base de dato
DATABASE_URL = "sqlite+aiosqlite:///./products_piel.db"


# Crear un motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear una sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Función para obtener la sesión de base de datos
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

# Crear un motor síncrono si lo necesitas
def get_engine():
    return engine
