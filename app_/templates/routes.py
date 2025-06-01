# routes.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from requests import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.post("/api/usuarios")
async def registrar_usuario(usuario: UserCreate, db: AsyncSession = Depends(get_db)):
    nuevo_usuario = User(
        name=usuario.name,
        mail=usuario.mail,
        type_skin=usuario.type_skin,
        preferences=usuario.preferences or False
    )
    db.add(nuevo_usuario)
    await db.commit()  # importante: await aquí
    return {"mensaje": "Usuario registrado"}

@router.get("/registro", response_class=HTMLResponse)
async def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})






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










