# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from dbconnection import Base
from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional



# Asegúrate que Base venga del archivo central de config


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    type_skin = Column(String, nullable=True)
    preferences = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)

    habits = relationship("Habit", back_populates="user")


class DeletedUser(Base):
    __tablename__ = 'users_deleted'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    type_skin = Column(String, nullable=True)
    preferences = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)


# models/habit.py

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    frequency = Column(String(25), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits")


# models/product.py

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


class HabitWithId(BaseModel):
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
        from_attributes = True



