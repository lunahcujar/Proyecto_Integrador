# routes.py
import csv
import os
from typing import List
from urllib import request

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from requests import Session
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import db
from starlette.responses import JSONResponse, FileResponse

from app_.dbconnection import get_db
from app_.models import SkinType, User
from app_.products import Product
from flask import Flask, render_template, redirect
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
    # Validación opcional: evitar correos duplicados
    existing = await db.execute(
        select(User).where(User.mail == usuario.mail)
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    nuevo_usuario = User(
        name=usuario.name,
        mail=usuario.mail,
        type_skin=usuario.type_skin,
        preferences=usuario.preferences or False,
        image_url=usuario.image_url  # Asegúrate de que el esquema y modelo lo incluyan
    )

    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario registrado",
        "id": nuevo_usuario.id
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



from app_.products import Product



from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

@router.post('/productos/editar/{id}')
async def editar_producto(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    # Consulta asincrónica
    result = await db.execute(select(Product).where(Product.id == id))
    producto = result.scalar_one_or_none()

    if not producto:
        return templates.TemplateResponse("404.html", {"request": request, "mensaje": "Producto no encontrado"}, status_code=404)

    form = await request.form()
    producto.name = form.get("name")
    producto.url = form.get("url")
    producto.type = form.get("type")
    producto.ingredients = form.get("ingredients")
    producto.price = float(form.get("price"))
    producto.image_url = form.get("image_url")
    producto.skin_type = form.get("skin_type")

    await db.commit()

    return RedirectResponse(url="/productos", status_code=303)





@router.get("/productos/editar/{id}")
async def mostrar_edicion_producto(id: int, request: Request, db: Session = Depends(get_db)):
    producto = await db.get(Product, id)
    if not producto:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("edit_products.html", {"request": request, "producto": producto})


# Mostrar el formulario de creación
@router.get("/productos/nuevo")
async def form_crear_producto(request: Request):
    return templates.TemplateResponse("add_products.html", {"request": request})

# Guardar el producto en la base de datos
@router.post("/productos/crear")
async def crear_producto(
    name: str = Form(...),
    url: str = Form(""),
    type: str = Form(""),
    ingredients: str = Form(""),
    price: float = Form(0.0),
    image_url: str = Form(""),
    skin_type: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    nuevo_producto = Product(
        name=name,
        url=url,
        type=type,
        ingredients=ingredients,
        price=price,
        image_url=image_url,
        skin_type=skin_type
    )
    db.add(nuevo_producto)
    await db.commit()
    return RedirectResponse(url="/productos?creado=1", status_code=303)







CSV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "productos_eliminados.csv"))






@router.get("/productos/eliminar/{id}")
async def eliminar_producto_por_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    producto = result.scalar_one_or_none()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Guardar en CSV antes de eliminar
    try:
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
    except Exception as e:
        print(f"[ERROR] Falló al escribir en CSV: {e}")

    await db.execute(delete(Product).where(Product.id == id))
    await db.commit()

    # Redirección con parámetro para mostrar SweetAlert
    return RedirectResponse(url="/productos?eliminado=1", status_code=303)




@router.get("/descargar/eliminados")
async def descargar_productos_eliminados():
    if os.path.exists(CSV_FILE_PATH):
        return FileResponse(path=CSV_FILE_PATH, filename="productos_eliminados.csv", media_type='text/csv')
    return HTMLResponse(content="No hay productos eliminados aún.", status_code=404)


















#Endpoint con la información del desarrollador

@router.get("/info/desarrollador")
async def info_desarrollador():
    return {
        "nombre": "Tu Nombre",
        "correo": "tuemail@ejemplo.com",
        "semestre": "6º",
        "programa": "Ingeniería de Sistemas y Computación"
    }


#Endpoint con la información de la fase de planeación

@router.get("/info/planeacion")
async def info_planeacion():
    return {
        "objetivo": "Analizar hábitos de cuidado de piel y recomendar productos",
        "actividades": [
            "Definición de requerimientos",
            "Diseño de modelos",
            "Planificación de interfaz",
            "Conexión con base de datos"
        ]
    }


#Endpoint con la información del diseño

@router.get("/info/diseno")
async def info_diseno():
    return {
        "colores": ["#a85d74", "#843a50"],
        "estructura": "Estilo limpio, navegación clara, formularios amigables",
        "plantillas": ["base.html", "formulario_habitos.html", "registro.html"]
    }


# Endpoint con el objetivo del proyecto

@router.get("/info/objetivo")
async def objetivo_proyecto():
    return {
        "objetivo": "Ofrecer una plataforma web que ayude a los usuarios a identificar y mejorar sus rutinas de cuidado de piel, recomendando productos adecuados según sus hábitos."
    }
