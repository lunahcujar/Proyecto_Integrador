from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from dbconnection import Base, engine


# Inicialización de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Enum para los tipos de piel
class SkinType(str, Enum):
    seca = "seca"
    grasa = "grasa"
    sensible = "sensible"
    mixta = "mixta"
    normal = "normal"
    acneica = "acneica"
    madura = "madura"
    todo_tipo = "todo_tipo"

# Modelo para el Producto
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
    name: Optional[str]  # Estos campos son opcionales para la actualización
    skin: Optional[SkinType] = None
    ingredients: Optional[str]
    price: Optional[float]

    class Config:
        orm_mode = True

class ProductWithId(UpdatedProduct):
    id: int

    class Config:
        orm_mode = True

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL,
    stock INTEGER
);