from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

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
    id:int=Field(...,min_length=1, max_length=100)
    name:str = Field(..., min_length=3, max_length=20)
    frequency:str = Field(...,min_length=3,max_length=25)
    user_id:int

class product(BaseModel):
    id:int=Field(...,min_length=1, max_length=100)
    name:str = Field(..., min_length=3, max_length=20)
    skin:Optional[str] = Field(...)
    ingredients:str = Field(...,min_length=3,max_length=100)
    price: float = Field(..., min_length=1, max_length=100)

class habitRecord(BaseModel):
    id: int = Field(..., min_length=1, max_length=100)
    user_id: int
    habit_id: int
    timestamp: datetime
    effectiveness: Optional[int] = Field(None, ge=1, le=5)

class weatherCondition(BaseModel):
    id: int = Field(..., gt=0)
    user_id: int
    date: datetime
    temperature: float
    habit_related: Optional[str] = Field(None, max_length=100)


class UpdatedPet(BaseModel):
    name: Optional[str] = Field(..., min_length=3, max_length=20)
    breed:Optional[str] = Field(..., min_length=3, max_length=25)