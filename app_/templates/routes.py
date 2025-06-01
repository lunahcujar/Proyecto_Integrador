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


@router.get("/add_user", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


class SessionLocal:
    pass


@router.post("/registrar_usuario")
async def register_user(
    name: str = Form(...),
    mail: str = Form(...),
    type_skin: SkinType = Form(...),
    preferences: bool = Form(False)
):
    db: Session = SessionLocal()
    nuevo_usuario = User(
        name=name,
        mail=mail,
        type_skin=type_skin,
        preferences=preferences
    )
    db.add(nuevo_usuario)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)




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







# Listar elementos
@router.get("/{modelo}s", response_class=HTMLResponse)
async def listar(request: Request, modelo: str):
    modelo = modelo.capitalize()
    if modelo not in csv_files:
        return HTMLResponse("Modelo no encontrado", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    df["id"] = df.index
    lista = df.to_dict(orient="records")

    return templates.TemplateResponse("list.html", {
        "request": request,
        "nombre_modelo": modelo,
        "items": lista
    })

# Mostrar formulario para agregar
@router.get("/{modelo}/add", response_class=HTMLResponse)
async def mostrar_formulario(request: Request, modelo: str):
    modelo = modelo.capitalize()
    if modelo not in campos_modelos:
        return HTMLResponse("Modelo no válido", status_code=404)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "nombre_modelo": modelo,
        "campos": campos_modelos[modelo],
        "valores": {},
        "ruta_accion": f"/{modelo}/add"
    })

# Procesar formulario
@router.post("/{modelo}/add")
async def agregar_item(request: Request, modelo: str, **datos: str):
    modelo = modelo.capitalize()
    if modelo not in campos_modelos:
        return HTMLResponse("Modelo no válido", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    nuevo_registro = [datos[campo] for campo in campos_modelos[modelo]]
    df.loc[len(df)] = nuevo_registro
    df.to_csv(csv_files[modelo], index=False)

    return RedirectResponse(url=f"/{modelo}s", status_code=303)

# Ver detalle de un ítem
@router.get("/{modelo}/detail/{id}", response_class=HTMLResponse)
async def ver_detalle(request: Request, modelo: str, id: int):
    modelo = modelo.capitalize()
    if modelo not in csv_files:
        return HTMLResponse("Modelo no encontrado", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    if id < 0 or id >= len(df):
        return HTMLResponse("Ítem no encontrado", status_code=404)

    fila = df.iloc[id].to_dict()

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "nombre_modelo": modelo,
        "item": fila
    })

