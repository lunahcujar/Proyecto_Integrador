from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from app_.dbconnection import Base, engine
from app_.models import SkinType

# Inicialización de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Modelo para el Producto (SQLAlchemy)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column("image", String, nullable=False)  # ✅ aquí está el cambio
    skin_type = Column(String, nullable=False)


# Modelos Pydantic para validaciones y transferencias de datos
class ProductCreate(BaseModel):
    name: str
    url: Optional[str] = None
    type: Optional[str] = None
    ingredients: Optional[str] = None
    price: Optional[float] = None
    image :Optional[str] = None
    skin_type :Optional[str] = None

    class Config:
        orm_mode = True

class ProductWithId(ProductCreate):
    id: int

    class Config:
        orm_mode = True

class UpdatedProduct(BaseModel):
    name: Optional[str]
    url: Optional[str] = None
    type: Optional[str] = None
    ingredients: Optional[str]
    price: Optional[float]

    class Config:
        orm_mode = True
