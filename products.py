from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from dbconnection import Base, engine
from models import SkinType

# Inicialización de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Modelo para el Producto (SQLAlchemy)
class Product(Base):
    __tablename__ = "products"

    # Definir los atributos de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Nombre del producto
    skin: Mapped[SkinType] = mapped_column(SQLAlchemyEnum(SkinType), nullable=True)  # Tipo de piel
    ingredients: Mapped[str] = mapped_column(String(255), nullable=True)  # Ingredientes del producto
    price: Mapped[float] = mapped_column(Float, nullable=True)  # Precio del producto

# Modelos Pydantic para validaciones y transferencias de datos
class ProductCreate(BaseModel):
    name: str
    skin: Optional[SkinType] = None
    ingredients: Optional[str] = None
    price: Optional[float] = None

    class Config:
        orm_mode = True  # Esto permite que SQLAlchemy se use directamente en los modelos Pydantic

class ProductWithId(ProductCreate):
    id: int

    class Config:
        orm_mode = True

class UpdatedProduct(BaseModel):
    name: Optional[str]
    skin: Optional[SkinType] = None
    ingredients: Optional[str]
    price: Optional[float]

    class Config:
        orm_mode = True
