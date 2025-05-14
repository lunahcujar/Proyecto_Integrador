from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import Boolean
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi import Depends
from habit_operations import *
from models import *
from db_operations import *
from typing import List
from contextlib import asynccontextmanager
from products import Base
from dbconnection import AsyncSessionLocal, get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from db_operations import *
from user_operations import *
from products_operations import *
from create_tables import  *
from products import *
app = FastAPI()


#bnuevos cambios
#nueos cambiossss

@app.on_event("startup")
async def startup():
    # Crear las tablas cuando la aplicación inicie
    await create_tables()

# Aquí van tus rutas y otras configuraciones de FastAPI
@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

#user

# Crear usuario

@app.post("/user", response_model=UserWithId)
async def create_user(user: UpdatedUser, db: AsyncSession = Depends(get_db)):
    try:
        new_user_instance = await new_user(user.name, user.mail, user.type_skin, user.preferences, db)
        return new_user_instance
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno al crear usuario")


#update_by_name
@app.put("/user/by-name/{name}", response_model=UserWithId)
async def update_user_by_name(
    name: str,
    user_update: UpdatedUser,
    db: AsyncSession = Depends(get_db)
):
    updated = await modify_user_by_name(name, user_update.dict(exclude_unset=True), db)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

#show_all_users
@app.get("/allusers", response_model=List[UserWithId])
async def show_all_users(db: AsyncSession = Depends(get_db)):
    return await read_all_users(db)

@app.delete("/user/{user_id}", response_model=UserWithId)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted_user = await remove_user_by_id(user_id, db)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return deleted_user

"""""
#products


# Endpoint para crear un producto
@app.post("/products/", response_model=ProductWithId)
async def create_product_view(p: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = await create_product(db=db, p=p)
    return db_product

# Endpoint para obtener todos los productos
@app.get("/products/", response_model=list[ProductWithId])
async def get_all_products_view(db: AsyncSession = Depends(get_db)):
    return await get_all_products(db=db)

# Endpoint para obtener un producto por nombre
@app.get("/products/{product_name}", response_model=ProductWithId)
async def get_product_by_name_view(product_name: str, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_name(db=db, product_name=product_name)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Endpoint para actualizar un producto
@app.put("/products/{product_name}", response_model=ProductWithId)
async def update_product_view(product_name: str, updated_data: UpdatedProduct, db: AsyncSession = Depends(get_db)):
    updated = await update_product(db=db, product_name=product_name, updated_data=updated_data.dict())
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

# Endpoint para eliminar un producto
@app.delete("/products/{product_name}", response_model=ProductWithId)
async def delete_product_view(product_name: str, db: AsyncSession = Depends(get_db)):
    deleted = await delete_product(db=db, product_name=product_name)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted
"""

#habits
#create habit
@app.post("/habits/", response_model=HabitWithId)
async def create_habit(habit: UpdatedHabit, db: AsyncSession = Depends(get_db)):
    try:
        new_habit_instance = await new_habit(habit.name, habit.frequency, habit.user_id, db)
        return new_habit_instance  # ✅ sin paréntesis
    except Exception as e:
        print(f"❌ Error al crear habito: {e}")
        raise HTTPException(status_code=500, detail="Error interno al crear habito")


# Obtener todos los hábitos
@app.get("/habits/", response_model=list[HabitWithId])
async def get_all_habits(db: AsyncSession = Depends(get_db)):
    return await read_all_habits(db)

# Actualizar hábito por ID
@app.put("/habits/{habit_id}", response_model=HabitWithId)
async def update_habit_by_id(habit_id: int, updated_data: UpdatedHabit, db: AsyncSession = Depends(get_db)):
    try:
        updated = await modify_habit_by_id(habit_id, updated_data.dict(exclude_unset=True), db)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error al actualizar hábito: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar hábito")

# Eliminar hábito por nombre
@app.delete("/habits/{habit_name}", response_model=HabitWithId)
async def remove_habit(habit_name: str, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await delete_habit_by_name(habit_name, db)
        if deleted:
            return deleted
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    except Exception as e:
        print(f"❌ Error al eliminar hábito: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar hábito")



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
