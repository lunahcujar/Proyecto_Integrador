from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum

class user(BaseModel):
    name:str = Field(..., min_length=3, max_length=50)
    mail:str = Field(...,min_length=3,max_length=25)
    type_skin:Optional[str]= Field(...)
    preferences:bool = Field(...)
    date:datetime

class userWithId(user):
    id: int


class UpdatedUser(BaseModel):
    name: Optional[str] = Field(..., min_length=3, max_length=20)
    mail:Optional[str] = Field(..., min_length=3, max_length=25)

class habit(BaseModel):
    id:int=Field(...,)
    name:str = Field(..., min_length=3, max_length=20)
    frequency:str = Field(...,max_length=25)
    user_id:int

class UpdatedHabit(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=20)
    frequency: Optional[str] = Field(None, max_length=25)
    user_id: Optional[int] = None

class SkinType(str,Enum):
    seca="seca"
    grasa="grasa"
    sensible="sensible"
    mixta="mixta"
    normal="normal"
    acneica="acneica"
    madura="madura"
    todo_tipo="todo_tipo"


# Modelo Product con el campo skin como Enum
class Product(BaseModel):

    id :int=Field(...,)
    name: str=Field(...,min_length=3, max_length=20)
    skin:SkinType=Field(...)  # Usamos el Enum aquí
    ingredients:str=Field(...,min_length=3,max_length=100)
    price:float=Field(...,min_length=3,max_length=100)






