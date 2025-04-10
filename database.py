from sqlalchemy import Column, Float, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models import SkinType
from sqlalchemy import Enum as SQLAlchemyEnum


# Definir la clase base
class Base(DeclarativeBase):
    pass


# Definir el modelo Product con tus atributos
class Product(Base):
    __tablename__ = "products"

    # Definir los atributos de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Tamaño de cadena ajustado según necesidad
    skin: Mapped[SkinType] = mapped_column(SQLAlchemyEnum(SkinType), nullable=True)  # Usar el Enum SkinType
    ingredients: Mapped[str] = mapped_column(String(255), nullable=True)  # Limite ajustado para ingredientes
    price: Mapped[float] = mapped_column(Float, nullable=True)  # Precio en formato Float

