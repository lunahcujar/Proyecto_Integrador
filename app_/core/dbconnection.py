from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import ssl

# URL de conexión (SQLite en local)
DATABASE_URL = "postgresql+asyncpg://postgres:Mi1familia234@db.lajsdmootdbzlnlyfeum.supabase.co:5432/postgres"


# Crear el motor de conexión asincrónica
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)
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
        yield session  # Se cierra automáticamente al salir del contexto
