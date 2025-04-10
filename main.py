
from fastapi import FastAPI
from fastapi import HTTPException
from starlette.responses import JSONResponse
from models import *
from user_operations import *
from typing import List
from fastapi import FastAPI
from models import user, userWithId
from user_operations import get_next_ID, write_user_into_csv
from product_operations import new_product, read_all_products, modify_product_by_name
from models import product
from habit_operations import new_habit, read_all_habits, modify_habit_by_name

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


@app.post("/products/", response_model=product)
def create_product(p: product):
    return new_product(p)

@app.get("/products/", response_model=list[product])
def get_all_products():
    return read_all_products()

@app.put("/products/{product_name}", response_model=product)
def update_product(product_name: str, updated_data: dict):
    updated = modify_product_by_name(product_name, updated_data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated




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