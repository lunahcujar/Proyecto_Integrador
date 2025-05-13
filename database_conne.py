import asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from models import Base
from products import Product

# --- Origen (SQLite)
SQLITE_URL = "sqlite:///./productos_piel.db"
sqlite_engine = create_engine(SQLITE_URL)
SQLiteSession = sessionmaker(bind=sqlite_engine)

# --- Destino (PostgreSQL en Clever Cloud)
POSTGRES_URL = "postgresql+asyncpg://uocli0titobcsftfloev:ONxwy7h8aKuybHt7a5F05jNdwGVnzd@bxrra2fip4pfogffonc8-postgresql.services.clever-cloud.com:50013/bxrra2fip4pfogffonc8"
pg_engine = create_async_engine(POSTGRES_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)

async def migrate():
    # Crear tablas si no existen en PostgreSQL
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Leer desde SQLite
    sqlite_db = SQLiteSession()
    products = sqlite_db.query(Product).all()

    # Insertar en PostgreSQL
    async with AsyncSessionLocal() as async_session:
        async_session.add_all(products)
        await async_session.commit()

    print("✅ Migración completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(migrate())
