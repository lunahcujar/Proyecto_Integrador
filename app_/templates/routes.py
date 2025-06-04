# routes.py
import csv
import os
from typing import List

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from requests import Session
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, FileResponse

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
    # Obtener todos los productos
    result = await db.execute(select(Product))
    productos = result.scalars().all()

    # Convertir a diccionario con imagen corregida
    lista = [
        {
            "id": p.id,
            "name": p.name,
            "url": p.url,
            "type": p.type,
            "ingredients": p.ingredients,
            "price": p.price,
            "image_url": extract_direct_image_url(p.image_url) if p.image_url and p.image_url.startswith("http") else "https://via.placeholder.com/250x200?text=Sin+imagen",
            "skin_type": p.skin_type
        }
        for p in productos
    ]

    # Paginación
    page = int(request.query_params.get("page", 1))
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = lista[start:end]
    has_next = end < len(lista)

    # Mensaje opcional de éxito (después de editar, por ejemplo)
    msg = request.query_params.get("msg", "")

    return templates.TemplateResponse("list.html", {
        "request": request,
        "nombre_modelo": "Producto",
        "items": paginated_items,
        "all_items": lista,
        "page": page,
        "has_next": has_next,
        "msg": msg
    })



from urllib.parse import urlencode

@router.post("/productos/editar")
async def editar_producto(
    request: Request,
    id: int = Form(...),
    name: str = Form(...),
    url: str = Form(""),
    type: str = Form(""),
    ingredients: str = Form(""),
    price: float = Form(0.0),
    image_url: str = Form(""),
    skin_type: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == id))
    producto = result.scalar_one_or_none()

    if producto:
        producto.name = name
        producto.url = url
        producto.type = type
        producto.ingredients = ingredients
        producto.price = price
        producto.image_url = image_url
        producto.skin_type = skin_type
        await db.commit()
        return RedirectResponse(url="/productos?msg=✅+Producto+actualizado+correctamente", status_code=303)

    return HTMLResponse(content="❌ Producto no encontrado", status_code=404)



@router.get("/productos/editar")
async def mostrar_formulario_edicion(request: Request):
    return templates.TemplateResponse("edit_products.html", {"request": request})



CSV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "productos_eliminados.csv"))

@router.get("/productos/eliminar")
async def mostrar_formulario_eliminar(request: Request, mensaje: str = None):
    return templates.TemplateResponse("delete_products.html", {"request": request, "mensaje": mensaje})


@router.post("/productos/eliminar")
async def eliminar_producto_por_nombre(
    request: Request,
    name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.name == name))
    producto = result.scalar_one_or_none()

    if producto:
        # Guardar en CSV antes de eliminar
        file_exists = os.path.isfile(CSV_FILE_PATH)
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'url', 'type', 'ingredients', 'price', 'image_url', 'skin_type', 'deleted_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                'id': producto.id,
                'name': producto.name,
                'url': producto.url,
                'type': producto.type,
                'ingredients': producto.ingredients,
                'price': producto.price,
                'image_url': producto.image_url,
                'skin_type': producto.skin_type,
                'deleted_at': datetime.now().isoformat()
            })

        await db.execute(delete(Product).where(Product.name == name))
        await db.commit()
        return RedirectResponse(url="/productos/eliminar?mensaje=Producto+eliminado+correctamente", status_code=303)

    # Mostrar mensaje de error si no se encontró el producto
    return templates.TemplateResponse("delete_products.html", {
        "request": request,
        "error": f"No se encontró el producto con nombre: {name}"
    }, status_code=404)


@router.get("/descargar/eliminados")
async def descargar_productos_eliminados():
    if os.path.exists(CSV_FILE_PATH):
        return FileResponse(path=CSV_FILE_PATH, filename="productos_eliminados.csv", media_type='text/csv')
    return HTMLResponse(content="No hay productos eliminados aún.", status_code=404)
