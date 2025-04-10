from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import Boolean

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import models
from habit_operations import *
from models import *
from db_operations import *
from typing import List
from contextlib import asynccontextmanager
from database import Base
from dbconnection import AsyncSessionLocal, get_db_session, get_engine
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from db_operations import *
from user_operations import *
from products_operations import *

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

#user
#create user
@app.post("/user", response_model=userWithId)
async def create_user(user: user):
    return new_user(user)

#update_by_name
@app.put("/user/by-name/{name}", response_model=userWithId)
def update_user_by_name(name: str, user_update: UpdatedUser):
    updated = modify_user_by_name(
        name, user_update.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
#show_all_users
@app.get("/allusers", response_model=List[userWithId])
async def show_all_users():
    return read_all_users()


@app.exception_handler(HTTPException)
async def http_exception_handler(request,exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message":"Carambas, algo fallo",
            "detail":exc.detail,
            "path":request.url.path
        },
    )
#delete
@app.delete("/user/{user_id}", response_model=userWithId)
def delete_user(user_id: int):
    deleted_user = remove_user_by_id(user_id)

    if not deleted_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return deleted_user



#products


@app.post("/products/", response_model=Product)
def create_product_view(p: Product, db: Session = Depends(get_db_session())):
    return create_product(db=db, p=p)

@app.get("/products/", response_model=list[Product])
def get_all_products_view(db: Session = Depends(get_db_session)):
    return get_all_products(db=db)

@app.get("/products/{product_name}", response_model=Product)
def get_product_by_name_view(product_name: str, db: Session = Depends(get_db_session)):
    product = get_product_by_name(db=db, product_name=product_name)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_name}", response_model=Product)
def update_product_view(product_name: str, updated_data: Product, db: Session = Depends(get_db_session())):
    updated = update_product(db=db, product_name=product_name, updated_data=updated_data.dict())
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated
@app.delete("/products/{product_name}", response_model=Product)
def delete_product_view(product_name: str, db: Session = Depends(get_db_session)):
    deleted = delete_product(db=db, product_name=product_name)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted



#habits
@app.post("/habits/", response_model=habit)
def create_habit(h: habit):
    return new_habit(h)

@app.get("/habits/", response_model=list[habit])
def get_all_habits():
    return read_all_habits()

@app.put("/habits/{habit_name}", response_model=habit)
def update_habit(habit_name: str, updated_data: dict):
    updated = modify_habit_by_name(habit_name, updated_data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated

#database_products




