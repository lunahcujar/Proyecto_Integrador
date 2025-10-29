from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict
from enum import Enum

from app_.core.dbconnection import Base, engine

# ----------------------
# Inicialización de la BD
# ----------------------
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# ----------------------
# Modelos SQLAlchemy
# ----------------------
class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    habitos = relationship("Habito", back_populates="usuario")
    rutinas = relationship("Rutina", back_populates="usuario")


class Habito(Base):
    __tablename__ = "habitos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    lavarse_cara = Column(String(50))
    protector_solar = Column(String(50))
    exfoliacion = Column(String(50))
    tipo_piel = Column(String(50))
    objetivo = Column(String(100))
    edad = Column(Integer)

    usuario = relationship("User", back_populates="habitos")



class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(150), nullable=False)
    product_url = Column(String(255), nullable=True)
    product_type = Column(String(100), nullable=False)
    clean_ingreds = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    skin_type = Column(String(100), nullable=True)

    rutinas = relationship("RutinaProducto", back_populates="producto")

    def __repr__(self):
        return f"<Producto(id={self.id}, name={self.product_name}, type={self.product_type}, price={self.price})>"

# ----------------------
class HabitoCreate(BaseModel):
    nombre: str
    correo: str
    respuestas: Dict[str, str]


class UserUpdate(BaseModel):
    edad: Optional[int] = None
    foto_url: Optional[str] = None

# ----------------------
# Pydantic model
# ----------------------
class HabitoCreate(BaseModel):
    nombre: str
    correo: str
    edad: Optional[int]
    respuestas: Dict[str, str]


class Rutina(Base):
    __tablename__ = "rutinas"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    habito_id = Column(Integer, ForeignKey("habitos.id"))
    usuario = relationship("User", back_populates="rutinas")
    productos = relationship("RutinaProducto", back_populates="rutina")

class RutinaProducto(Base):
    __tablename__ = "rutina_productos"
    id = Column(Integer, primary_key=True)
    rutina_id = Column(Integer, ForeignKey("rutinas.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))

    rutina = relationship("Rutina", back_populates="productos")
    producto = relationship("Producto", back_populates="rutinas")