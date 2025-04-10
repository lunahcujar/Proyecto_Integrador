from typing import Optional
from sqlalchemy import Column, Float, String, Integer, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum

# Base de SQLAlchemy
class Base(DeclarativeBase):
    pass

# Enum para el tipo de piel
class SkinType(str, enum.Enum):
    oily = "Oily"
    dry = "Dry"
    combination = "Combination"
    sensitive = "Sensitive"
    normal = "Normal"

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    skin: Mapped[Optional[SkinType]] = mapped_column(Enum(SkinType), nullable=True)
    ingredients: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
