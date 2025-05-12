from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    mail = Column(String(25), nullable=False)
    type_skin = Column(String(20), nullable=True)
    preferences = Column(Boolean, nullable=False)
    date = Column(DateTime, nullable=False)

    habits = relationship("Habit", back_populates="user")  # Relación con la clase Habit

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, mail={self.mail})>"



# Modelo de Pydantic para un usuario con ID
class UserWithId(BaseModel):
    id: int
    name: str
    mail: str
    type_skin: Optional[str] = None
    preferences: bool
    date: datetime

    class Config:
        orm_mode = True  # Esto permite convertir los objetos SQLAlchemy en Pydantic models

class UpdatedUser(BaseModel):
    name: Optional[str]
    mail: Optional[str]
    type_skin: Optional[str]
    preferences: Optional[bool]
    date: Optional[datetime]

    class Config:
        orm_mode = True





class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    frequency = Column(String(25), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits")


class SkinType(PyEnum):
    seca = "seca"
    grasa = "grasa"
    sensible = "sensible"
    mixta = "mixta"
    normal = "normal"
    acneica = "acneica"
    madura = "madura"
    todo_tipo = "todo_tipo"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    skin = Column(SQLAlchemyEnum(SkinType), nullable=False)
    ingredients = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)



