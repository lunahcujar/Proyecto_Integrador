# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import ForeignKey
from pydantic import BaseModel
from typing import Optional
from enum import Enum

# Importar desde la configuración de la base de datos
from dbconnection import Base,engine

# Inicialización de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Definir el modelo User en SQLAlchemy
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    type_skin = Column(String, nullable=True)
    preferences = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)

    habits = relationship("Habit", back_populates="user")

# Modelos Pydantic para validaciones y transferencias de datos

class UserCreate(BaseModel):
    name: str
    mail: str
    type_skin: Optional[str] = None
    preferences: Optional[bool] = None

    class Config:
        orm_mode = True  # Esto permite que SQLAlchemy se use directamente en los modelos Pydantic

class UserWithId(UserCreate):
    id: int

    class Config:
        orm_mode = True

class UpdatedUser(BaseModel):
    name: str
    mail: str
    type_skin: Optional[str] = None
    preferences: bool = False

    class Config:
        orm_mode = True

class UserWithId(UpdatedUser):
    id: int

    class Config:
        orm_mode = True


# Para los hábitos
class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    frequency = Column(String(25), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits")

class HabitWithId(BaseModel):
    id: int
    name: str
    frequency: str
    user_id: int

    class Config:
        orm_mode = True

# Representación del Hábito para crear o actualizar (sin ID)
class UpdatedHabit(BaseModel):
    name: Optional[str]  # Estos campos son opcionales para la actualización
    frequency: Optional[str]
    user_id: Optional[int]

    class Config:
        orm_mode = True



class SkinType(str,Enum):
    seca = "seca"
    grasa = "grasa"
    sensible = "sensible"
    mixta = "mixta"
    normal = "normal"
    acneica = "acneica"
    madura = "madura"
    todo_tipo = "todo_tipo"