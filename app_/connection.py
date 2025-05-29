import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app_.products import Product  # Asegúrate de que este modelo esté bien importado
from app_.models import Base       # Contiene declarative_base()
from app_.dbconnection import engine, AsyncSessionLocal  # Reutilizamos el engine y la sesión

def clean_price(price_str):
    """Limpia el campo de precio quitando símbolos y convirtiendo a float."""
    if isinstance(price_str, str):
        return float(price_str.replace("£", "").replace("$", "").strip())
    return float(price_str)

async def migrate_from_csv(csv_path):
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Leer el CSV
    df = pd.read_csv(csv_path)

    # Crear instancias del modelo Product
    products = [
        Product(
            name=row["product_name"],
            url=row["product_url"],
            type=row["product_type"],
            ingredients=row["clean_ingreds"],
            price=clean_price(row["price"])
        )
        for _, row in df.iterrows()
    ]

    # Insertar en la base de datos
    async with AsyncSessionLocal() as session:
        session.add_all(products)
        await session.commit()

    print("✅ Migración completada exitosamente.")

if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "skincare_products_clean.csv")

    asyncio.run(migrate_from_csv(csv_path))
