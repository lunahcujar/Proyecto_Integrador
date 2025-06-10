from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

from app_.dbconnection import Base, engine

# Inicialización de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Enumeración para tipos de piel
class SkinType(str, Enum):
    seca = "seca"
    grasa = "grasa"
    sensible = "sensible"
    mixta = "mixta"
    normal = "normal"

# Modelo SQLAlchemy de Usuario
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    type_skin = Column(SqlEnum(SkinType), nullable=True)  # CORREGIDO
    preferences = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String, nullable=True)

    habits = relationship("Habit", back_populates="user")

# Modelo SQLAlchemy de Hábito
class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    frequency = Column(String(25), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits")

# ----------------------
# Modelos Pydantic
# ----------------------

class UserCreate(BaseModel):
    name: str
    mail: str
    type_skin: Optional[SkinType]  # Puedes usar SkinType aquí también
    preferences: Optional[bool] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

class UpdatedUser(BaseModel):
    name: str
    mail: str
    type_skin: Optional[SkinType]
    preferences: bool = False

    class Config:
        orm_mode = True

class UserWithId(UpdatedUser):
    id: int

    class Config:
        orm_mode = True


class UsuarioOut(BaseModel):
    id: int
    email: str = Field(alias="mail")  # El campo real en la base es 'mail'
    name: str
    type_skin: SkinType | None
    preferences: bool
    date: datetime
    image_url: str | None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


# Modelos de hábito
from pydantic import BaseModel


class FrecuenciaEnum(str, Enum):
    nunca = "nunca"
    una_vez = "1_vez"
    dos_veces = "2_veces"
    diario = "diario"
    si = "si"
    no = "no"


    pass


class HabitCreate(BaseModel):
    name: str
    frequency: str
    user_id: int
class HabitCreate(BaseModel):
    name: str
    frequency: str
    user_id: int


class HabitResponse(BaseModel):
    id: int
    name: str
    frequency: str
    user_id: int

    class Config:
        orm_mode = True


class UpdatedHabit(BaseModel):
    name: Optional[str]
    frequency: Optional[str]
    user_id: Optional[int]

    class Config:
        orm_mode = True

class HabitWithId(BaseModel):
    id: int
    name: str
    frequency: str
    user_id: int

    class Config:
        orm_mode = True

