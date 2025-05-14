import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from products import Product  # tu modelo SQLAlchemy
from models import Base

# URL de PostgreSQL (ajústala si la cambias)
POSTGRES_URL = "postgresql+asyncpg://uocli0titobcsftfloev:ONxwy7h8aKuybHt7a5F05jNdwGVnzd@bxrra2fip4pfogffonc8-postgresql.services.clever-cloud.com:50013/bxrra2fip4pfogffonc8"

# Crear engine y sesión
pg_engine = create_async_engine(POSTGRES_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)

async def migrate_from_csv(csv_path):
    # Crear tablas si no existen
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Leer el CSV con pandas
    df = pd.read_csv(csv_path)

    # Convertir filas del DataFrame a objetos Product
    products = [
        Product(
            id=row["id"],
            name=row["name"],
            skin=row["skin"],
            ingredients=row["ingredients"],
            price=row["price"]
        )
        for _, row in df.iterrows()
    ]

    # Insertar en PostgreSQL
    async with AsyncSessionLocal() as session:
        session.add_all(products)
        await session.commit()

    print("✅ Migración desde CSV completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(migrate_from_csv("productos.csv"))
