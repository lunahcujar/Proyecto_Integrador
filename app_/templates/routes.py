# routes.py
from typing import List

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from requests import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app_.dbconnection import get_db
from app_.models import SkinType, User
from app_.products import Product
from flask import Flask, render_template
from urllib.parse import urlparse, parse_qs

router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")


# registrar_usuario.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app_.models import User, UserCreate
from app_.dbconnection import get_db
from app_ .models import *


#users

@router.post("/api/usuarios")
async def registrar_usuario(usuario: UserCreate, db: AsyncSession = Depends(get_db)):
    nuevo_usuario = User(
        name=usuario.name,
        mail=usuario.mail,
        type_skin=usuario.type_skin,
        preferences=usuario.preferences or False
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)  # <-- Esto es necesario para obtener el ID generado

    return {
        "mensaje": "Usuario registrado",
        "id": nuevo_usuario.id  # <-- Devuelve el ID

    }

@router.get("/api/usuarios/{user_id}")
async def obtener_usuario(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    usuario = result.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/registro", response_class=HTMLResponse)
async def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@router.get("/api/productos")
async def obtener_productos(skin_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Product).where(Product.skin_type.ilike(skin_type))  # Insensible a mayúsculas
    )
    productos = result.scalars().all()
    return productos


@router.get("/api/productos")
async def obtener_productos_por_tipo(skin_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.skin_type == skin_type))
    productos = result.scalars().all()
    return productos



#test_habitos

@router.post("/api/habitos")
async def crear_habitos(habits: List[HabitCreate], db: AsyncSession = Depends(get_db)):
    nuevos_habitos = []

    for habit_data in habits:
        result = await db.execute(select(User).where(User.id == habit_data.user_id))
        user = result.scalar_one_or_none()
        if not user:
            return JSONResponse(status_code=400, content={"detail": f"Usuario {habit_data.user_id} no existe"})

        nuevo = Habit(
            name=habit_data.name,
            frequency=habit_data.frequency,
            user_id=habit_data.user_id
        )
        db.add(nuevo)
        nuevos_habitos.append(nuevo)

    await db.commit()
    return {"mensaje": f"{len(nuevos_habitos)} hábitos registrados correctamente"}




@router.get("/test-habitos", response_class=HTMLResponse)
async def mostrar_test_habitos(request: Request):
    return templates.TemplateResponse("test_habitos.html", {"request": request})


#recomendaciones

async def obtener_productos_por_tipo(skin_type: str, db: AsyncSession):
    stmt = select(Product).where(Product.skin_type == skin_type)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/recomendaciones", response_class=HTMLResponse)
async def mostrar_recomendaciones(request: Request):
    return templates.TemplateResponse("recomendaciones.html", {"request": request})




# Página principal
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Archivos CSV por modelo
csv_files = {
    "Usuario": "app_/usuarios.csv",
    "Producto": "app_/productos.csv",
    "Habito": "app_/habitos.csv"
}

# Campos por modelo
campos_modelos = {
    "Usuario": ["name", "mail", "type_skin", "preferences"],
    "Producto": ["name", "description", "type_skin"],
    "Habito": ["name", "frequency", "user_id"]
}

#catalogo (list)

def extract_direct_image_url(full_url):
    try:
        query = urlparse(full_url).query
        return parse_qs(query)["url"][0]
    except:
        return full_url  # si falla, deja el original


# ✅ Función para limpiar la URL de Lookfantastic
from urllib.parse import urlparse, parse_qs, unquote

def extract_direct_image_url(proxy_url: str) -> str:
    try:
        parsed = urlparse(proxy_url)
        query = parse_qs(parsed.query)
        real_url = query.get("url", [None])[0]
        if real_url:
            return unquote(real_url)  # decodifica %3A%2F%2F, etc.
        return proxy_url
    except Exception:
        return proxy_url


@router.get("/productos", response_class=HTMLResponse)
async def mostrar_catalogo(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    productos = result.scalars().all()

    lista = [
        {
            "id": p.id,
            "name": p.name,
            "url": p.url,
            "type": p.type,
            "ingredients": p.ingredients,
            "price": p.price,
            "image_url": extract_direct_image_url(p.image_url),
            "skin_type": p.skin_type
        }
        for p in productos
    ]

    return templates.TemplateResponse("list.html", {
        "request": request,
        "nombre_modelo": "Producto",
        "items": lista
    })










