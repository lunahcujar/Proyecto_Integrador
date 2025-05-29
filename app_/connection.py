import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app_.products import Product  # Importación relativa
from app_.models import Base       # Importación relativa

# URL de PostgreSQL (ajústala si la cambias)
POSTGRES_URL = "postgresql+asyncpg://uwwaoyysz9b8uw8oryhz:lF9ljHVTelf8mU2ST8glvH3E7SaZUK@bmx3ykywpgi0a3ffcvnm-postgresql.services.clever-cloud.com:50013/bmx3ykywpgi0a3ffcvnm"

# Crear engine y sesión
pg_engine = create_async_engine(POSTGRES_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)

def clean_price(price_str):
    """Limpia el campo de precio quitando símbolos y convirtiendo a float."""
    if isinstance(price_str, str):
        return float(price_str.replace("£", "").replace("$", "").strip())
    return float(price_str)

async def migrate_from_csv(csv_path):
    # Crear tablas si no existen
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Leer el CSV con pandas
    df = pd.read_csv(csv_path)

    # Convertir filas del DataFrame a objetos Product con nombres que coincidan con el modelo
    products = [
        Product(
            name=row["product_name"],
            url=row["product_url"],
            type=row["product_type"],
            ingredients=row["clean_ingreds"],
            price=clean_price(row["price"])  # ✅ Aquí se limpia el precio
        )
        for _, row in df.iterrows()
    ]

    # Insertar en PostgreSQL
    async with AsyncSessionLocal() as session:
        session.add_all(products)
        await session.commit()

    print("✅ Migración desde CSV completada exitosamente.")

if __name__ == "__main__":
    import os
    import asyncio

    # Ruta absoluta al archivo CSV basada en la ubicación actual de este script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "skincare_products_clean.csv")

    # Ejecutar la migración
    asyncio.run(migrate_from_csv(csv_path))
