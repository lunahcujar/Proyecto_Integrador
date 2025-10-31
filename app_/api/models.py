import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, Dict

from app_.core.dbconnection import Base

# ----------------------
# Modelos SQLAlchemy
# ----------------------

class User(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)

    habitos = relationship("Habito", back_populates="usuario")
    rutinas = relationship("Rutina", back_populates="usuario")


class Habito(Base):
    __tablename__ = "habitos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"))
    lavarse_cara = Column(String(50))
    protector_solar = Column(String(50))
    exfoliacion = Column(String(50))
    tipo_piel = Column(String(50))
    objetivo = Column(String(100))
    edad = Column(String(10))

    usuario = relationship("User", back_populates="habitos")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(150), nullable=False)
    product_url = Column(String(255), nullable=True)
    product_type = Column(String(100), nullable=False)
    clean_ingreds = Column(String(500), nullable=True)
    price = Column(String(50))
    image_url = Column(String(255), nullable=True)
    skin_type = Column(String(100), nullable=True)

    rutinas = relationship("RutinaProducto", back_populates="producto")

    def __repr__(self):
        return f"<Producto(id={self.id}, name={self.product_name}, type={self.product_type}, price={self.price})>"


class Rutina(Base):
    __tablename__ = "rutinas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    habito_id = Column(UUID(as_uuid=True), ForeignKey("habitos.id"))

    usuario = relationship("User", back_populates="rutinas")
    productos = relationship("RutinaProducto", back_populates="rutina")


class RutinaProducto(Base):
    __tablename__ = "rutina_productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rutina_id = Column(UUID(as_uuid=True), ForeignKey("rutinas.id"))
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"))

    rutina = relationship("Rutina", back_populates="productos")
    producto = relationship("Producto", back_populates="rutinas")


# ----------------------
# Modelos Pydantic
# ----------------------

class HabitoCreate(BaseModel):
    nombre: str
    correo: str
    edad: Optional[int]
    respuestas: Dict[str, str]


class UserUpdate(BaseModel):
    edad: Optional[int] = None
    foto_url: Optional[str] = None
