from sqlalchemy.ext.asyncio import AsyncSession
from database import Product

async def create_product(db: AsyncSession, p: Product):
    db_product = Product(name=p.name, skin=p.skin, ingredients=p.ingredients, price=p.price)
    db.add(db_product)
    await db.commit()  # Confirmar la transacción asíncrona
    await db.refresh(db_product)  # Refrescar el objeto para obtener el ID generado
    return db_product

from sqlalchemy.future import select  # Usamos `select` de SQLAlchemy para consultas asíncronas
from sqlalchemy.ext.asyncio import AsyncSession

async def get_all_products(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all()  # Devuelve todos los productos de forma asíncrona

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_product_by_name(db: AsyncSession, product_name: str):
    result = await db.execute(select(Product).filter(Product.name == product_name))
    return result.scalars().first()  # Devuelve el primer producto que coincide con el nombre

from sqlalchemy.ext.asyncio import AsyncSession

async def update_product(db: AsyncSession, product_name: str, updated_data: dict):
    result = await db.execute(select(Product).filter(Product.name == product_name))
    db_product = result.scalars().first()

    if db_product:
        db_product.name = updated_data.get('name', db_product.name)
        db_product.skin = updated_data.get('skin', db_product.skin)
        db_product.ingredients = updated_data.get('ingredients', db_product.ingredients)
        db_product.price = updated_data.get('price', db_product.price)

        await db.commit()  # Confirmar la transacción asíncrona
        await db.refresh(db_product)  # Refrescar el producto actualizado
        return db_product
    return None

from sqlalchemy.ext.asyncio import AsyncSession

async def delete_product(db: AsyncSession, product_name: str):
    result = await db.execute(select(Product).filter(Product.name == product_name))
    db_product = result.scalars().first()

    if db_product:
        await db.delete(db_product)  # Eliminar el producto de forma asíncrona
        await db.commit()  # Confirmar la transacción
        return db_product
    return None
