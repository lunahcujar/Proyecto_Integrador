from sqlalchemy.ext.asyncio import create_async_engine
from models import Base  # Asegúrate de usar el nombre correcto del archivo que contiene tus clases Base, User, etc.

DATABASE_URL = "postgresql+asyncpg://uocli0titobcsftfloev:ONxwy7h8aKuybHt7a5F05jNdwGVnzd@bxrra2fip4pfogffonc8-postgresql.services.clever-cloud.com:50013/bxrra2fip4pfogffonc8"


# Crear el motor de conexión asincrónica
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=2, max_overflow=0)

# Función asincrónica para crear las tablas
async def create_tables():
    async with engine.begin() as conn:
        # Crear las tablas en la base de datos
        await conn.run_sync(Base.metadata.create_all)
    # Asegúrate de liberar las conexiones
    await engine.dispose()

