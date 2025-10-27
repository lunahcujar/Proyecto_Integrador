from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float
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
    edad = Column(Integer, nullable=True)
    foto_url = Column(String(255), nullable=True)

    # Relación con hábitos
    habitos = relationship("Habit", back_populates="usuario", cascade="all, delete-orphan")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    pregunta = Column(String(255), nullable=False)
    respuesta = Column(String(255), nullable=False)

    # Relación inversa hacia el usuario
    usuario = relationship("User", back_populates="habitos")
# ----------------------
# Esquemas Pydantic
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

    def __repr__(self):
        return f"<Producto(id={self.id}, name={self.product_name}, type={self.product_type}, price={self.price})>"

