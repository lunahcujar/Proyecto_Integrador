from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Obtener variables desde el entorno
DB_HOST = os.getenv("CLEVER_HOST")
DB_NAME = os.getenv("CLEVER_DATABASE")
DB_USER = os.getenv("CLEVER_USER")
DB_PASSWORD = os.getenv("CLEVER_PASSWORD")
DB_PORT = os.getenv("CLEVER_PORT")

# Formar la URL de conexión para PostgreSQL asíncrono
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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

# Motor síncrono si es necesario
def get_engine():
    return engine
