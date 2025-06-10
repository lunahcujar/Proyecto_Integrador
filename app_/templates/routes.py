# routes.py
import csv
import os
import traceback
import uuid
from typing import List, Dict
from urllib import request

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from requests import Session
from sqlalchemy import select, delete, text, func
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
from app_.main import *
from app_.models import *

from app_.supabase_config import supabase, SUPABASE_BUCKET, SUPABASE_URL



#users

import uuid
from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app_.models import User
from app_.dbconnection import get_db
from app_.supabase_config import supabase, SUPABASE_URL, SUPABASE_BUCKET

router = APIRouter()


# Página principal
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})





#usuario
@router.get("/registro", response_class=HTMLResponse)
async def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@router.post("/api/usuarios")
async def registrar_usuario(
    name: str = Form(...),
    mail: str = Form(...),
    type_skin: str = Form(...),
    preferences: bool = Form(False),
    photo: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        image_url = None
        if photo:
            filename = f"{uuid.uuid4()}_{photo.filename}"
            content = await photo.read()
            response = supabase.storage.from_(SUPABASE_BUCKET).upload(filename, content)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="❌ Error al subir imagen a Supabase")
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

        nuevo_usuario = User(
            name=name, mail=mail, type_skin=type_skin, preferences=preferences, image_url=image_url
        )
        db.add(nuevo_usuario)
        await db.commit()
        await db.refresh(nuevo_usuario)

        return {
            "mensaje": "✅ Usuario registrado correctamente",
            "id": nuevo_usuario.id,
            "image_url": nuevo_usuario.image_url
        }

    except Exception as e:
        await db.rollback()
        print("❌ ERROR REGISTRANDO USUARIO EN CLEVER:", repr(e))
        raise HTTPException(status_code=500, detail="Error al registrar usuario")


    #consultas

@router.get("/usuarios_list")
async def get_usuarios_json(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    usuarios = result.scalars().all()
    return {"usuarios": [u.__dict__ for u in usuarios]}


@router.get("/usuarios")
async def get_usuarios_html(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    usuarios = result.scalars().all()
    return templates.TemplateResponse("users_show.html", {
        "request": request,
        "usuarios": usuarios
    })


@router.get("/api/usuarios/{user_id}")
async def obtener_usuario_por_id(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    usuario = result.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/api/usuarios", response_model=UsuarioOut)
async def obtener_usuario_por_email(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.mail == email))
    usuario = result.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/usuarios/{email}")
async def redirigir_usuario(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.mail == email))
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    result_habits = await db.execute(select(Habit).where(Habit.user_id == usuario.id))
    habito_existente = result_habits.scalars().first()

    if habito_existente:
        return RedirectResponse(url=f"/rutina?email={email}", status_code=303)
    else:
        return RedirectResponse(url=f"/test-habitos?email={email}", status_code=303)


@router.get("/api/usuarios")
async def obtener_usuario(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.mail == email))
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "email": usuario.mail,
        "name": usuario.name,
        "type_skin": usuario.type_skin,
    }

#crud


@router.get("/modificar_usuario/{user_id}")
async def editar_usuario(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    usuario = result.scalar_one_or_none()
    return templates.TemplateResponse("edit_user.html", {"request": request, "usuario": usuario})


@router.post("/modificar_usuario/{user_id}")
async def actualizar_usuario(
    user_id: int,
    request: Request,
    name: str = Form(...),
    mail: str = Form(...),
    type_skin: str = Form(...),
    preferences: str = Form(...),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        return RedirectResponse(url="/usuarios?mensaje=Usuario+no+encontrado", status_code=303)

    usuario.name = name
    usuario.mail = mail
    usuario.type_skin = SkinType(type_skin)
    usuario.preferences = preferences.lower() == "true"

    if image and image.filename:
        extension = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        content = await image.read()
        supabase.storage.from_("userss").upload(path=filename, file=content, file_options={"content-type": image.content_type})
        public_url = supabase.storage.from_("userss").get_public_url(filename)
        usuario.image_url = public_url

    await db.commit()
    return RedirectResponse(url="/usuarios?mensaje=Usuario+modificado+correctamente", status_code=303)


@router.post("/eliminar_usuario/{user_id}")
async def eliminar_usuario(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        await db.execute(delete(Habit).where(Habit.user_id == user_id))
        if user.image_url:
            try:
                path = user.image_url.split("/storage/v1/object/public/userss/")[1]
                supabase.storage.from_("userss").remove([path])
            except Exception as e:
                print("Error al eliminar la imagen:", e)
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()

    return RedirectResponse(url="/usuarios?mensaje=Usuario+eliminado+correctamente", status_code=303)


#habitos

@router.get("/test-habitos", response_class=HTMLResponse)
async def mostrar_test_habitos_por_correo(request: Request, email: str = None, db: AsyncSession = Depends(get_db)):
    if not email:
        raise HTTPException(status_code=400, detail="Falta el parámetro de email en la URL")

    result = await db.execute(select(User).where(User.mail == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return templates.TemplateResponse("test_habitos.html", {
        "request": request,
        "user_id": user.id
    })

@router.get("/test-habitos", response_class=HTMLResponse)
async def mostrar_test_habitos_por_correo(request: Request, email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.mail == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return templates.TemplateResponse("test_habitos.html", {
        "request": request,
        "user_id": user.id
    })


@router.get("/debug-productos")
async def debug_productos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.skin_type == "Seca"))
    productos = result.scalars().all()
    print("Productos encontrados:", productos)
    return {"cantidad": len(productos)}



@router.post("/enviar-habitos", response_class=RedirectResponse)
async def enviar_habitos_y_redirigir(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()

    try:
        user_id = int(form["user_id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="ID de usuario inválido o faltante")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Lista de hábitos esperados
    claves_habito = ["lavado", "bloqueador", "exfoliacion"]
    for nombre in claves_habito:
        if nombre in form:
            frecuencia = form[nombre]
            habito = Habit(name=nombre, frequency=frecuencia, user_id=user_id)
            db.add(habito)

    await db.commit()

    return RedirectResponse(url=f"/test-habitos?email={user.mail}", status_code=303)


@router.post("/api/habitos")
async def crear_habitos(
    habits: List[HabitCreate],
    db: AsyncSession = Depends(get_db)
):
    nuevos_habitos = []

    for habit_data in habits:
        # Verifica si el usuario existe
        result = await db.execute(select(User).where(User.id == habit_data.user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=400, detail=f"Usuario con ID {habit_data.user_id} no existe")

        # Crea y agrega el hábito
        nuevo = Habit(
            name=habit_data.name,
            frequency=habit_data.frequency,
            user_id=habit_data.user_id
        )
        db.add(nuevo)
        nuevos_habitos.append(nuevo)

    await db.commit()

    return JSONResponse(
        status_code=201,
        content={"mensaje": f"{len(nuevos_habitos)} hábitos registrados correctamente"}
    )


@router.get("/api/habitos", response_model=list[HabitResponse])
async def obtener_habitos(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Habit).where(Habit.user_id == user_id))
    habitos = result.scalars().all()

    if not habitos:
        return []

    return habitos

from typing import Annotated


@router.get("/api/rutina")
async def generar_rutina(
        email: str = Query(...),
        db: AsyncSession = Depends(get_db)
):
    # 1. Obtener usuario
    result = await db.execute(select(User).where(User.mail == email))
    usuario = result.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tipo_piel = usuario.type_skin.capitalize()

    # 2. Obtener hábitos del usuario
    result = await db.execute(select(Habit).where(Habit.user_id == usuario.id))
    habitos = result.scalars().all()
    nombres_habitos = [h.name.lower() for h in habitos]

    # 3. Obtener productos recomendados según tipo de piel
    result = await db.execute(select(Product).where(Product.skin_type == tipo_piel))
    productos = result.scalars().all()

    productos_recomendados = [
        {
            "nombre": p.name,
            "ingredientes": p.ingredients,
            "imagen": p.image_url
        }
        for p in productos
    ]

    # 4. Generar recomendaciones según hábitos
    recomendaciones_habitos = []

    lavado = next((h for h in habitos if h.name == "lavado"), None)
    if lavado:
        if lavado.frequency == "no":
            recomendaciones_habitos.append("Se recomienda lavar tu cara diariamente para remover impurezas.")
    else:
        recomendaciones_habitos.append("No registraste si te lavas la cara.")

    bloqueador = next((h for h in habitos if h.name == "bloqueador"), None)
    if bloqueador:
        if bloqueador.frequency == "no":
            recomendaciones_habitos.append("Usa protector solar diariamente para proteger tu piel del daño solar.")
    else:
        recomendaciones_habitos.append("No registraste si usas bloqueador solar.")

    exfoliacion = next((h for h in habitos if h.name == "exfoliacion"), None)
    if exfoliacion:
        if exfoliacion.frequency == "nunca":
            recomendaciones_habitos.append(
                "La exfoliación ayuda a renovar tu piel. Intenta hacerlo al menos una vez por semana.")
    else:
        recomendaciones_habitos.append("No registraste tu frecuencia de exfoliación.")

    return {
        "productos_recomendados": productos_recomendados,
        "recomendaciones_habitos": recomendaciones_habitos
    }



from app_.dbconnection import AsyncSessionLocal

from app_.products import ProductOut,Product

@router.get("/api/productos_por_tipo", response_model=List[ProductOut])
async def obtener_productos_por_tipo(tipo_piel: str = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.skin_type == tipo_piel)
    result = await db.execute(stmt)
    productos = result.scalars().all()
    return productos

@router.get("/verificar-usuario")
async def redirigir_usuario(email: str, db: AsyncSession = Depends(get_db)):
    # 1. Buscar usuario por email
    result = await db.execute(select(User).where(User.mail == email))
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Buscar hábitos del usuario
    result_habits = await db.execute(select(Habit).where(Habit.user_id == usuario.id))
    habitos = result_habits.scalars().all()

    # 3. Redirigir según si tiene hábitos o no
    if habitos:
        return RedirectResponse(url=f"/rutina?email={email}", status_code=303)
    else:
        return RedirectResponse(url=f"/test-habitos?email={email}", status_code=303)



#rutina

@router.get("/rutina", response_class=HTMLResponse)
async def rutina(request: Request):
    return templates.TemplateResponse("rutina.html", {"request": request})


@router.get("/api/habitos-por-usuario")
async def listar_habitos_por_usuario(db: AsyncSession = Depends(get_db)):
    # Obtener todos los usuarios
    result = await db.execute(select(User))
    usuarios = result.scalars().all()

    datos = []

    # Para cada usuario, obtener sus hábitos
    for user in usuarios:
        result_habitos = await db.execute(select(Habit).where(Habit.user_id == user.id))
        habitos = result_habitos.scalars().all()

        datos.append({
            "usuario": {
                "id": user.id,
                "nombre": user.name,
                "email": user.mail,
                "tipo_piel": user.type_skin
            },
            "habitos": [
                {
                    "id": h.id,
                    "nombre": h.name,
                    "frecuencia": h.frequency
                } for h in habitos
            ]
        })

    return datos


#

#








@router.get("/api/productos_por_piel")
async def obtener_productos_por_tipo_piel(skin_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    if skin_type:
        result = await db.execute(
            select(Product).where(func.lower(Product.skin_type) == skin_type.lower())
        )
    else:
        result = await db.execute(select(Product))

    productos = result.scalars().all()
    return productos


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








@router.get("/api/productos")
async def obtener_productos(skin_type: str = "", db: AsyncSession = Depends(get_db)):
    query = select(Product)
    if skin_type:
        query = query.where(Product.skin_type.ilike(skin_type))
    result = await db.execute(query)
    return result.scalars().all()


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














@router.get("/info", response_class=HTMLResponse)
async def ver_info(request: Request):
    return templates.TemplateResponse("info.html", {"request": request})



#Endpoint con la información del desarrollador

@router.get("/info/desarrollador")
async def info_desarrollador():
    return {
        "nombre": "Luna Herrera Cújar",
        "correo": "lherrera95@ucatolica.edu.co",
        "semestre": "6º",
        "programa": "Ingeniería de Sistemas y Computación"
    }

# Endpoint con la información de la fase de planeación

@router.get("/info/planeacion")
async def info_planeacion():
    return {
        "nombre_proyecto": "Sistema de recomendaciones de cuidado de la piel",
        "descripcion": "Aplicación web que permite a los usuarios registrar sus hábitos de cuidado facial, realizar un test y recibir recomendaciones personalizadas de productos según su tipo de piel."
        ,
        "actividades": [
            "Definición de requerimientos funcionales y no funcionales.",
            "Diseño del modelo entidad-relación para usuarios, hábitos y productos.",
            "Planificación de las vistas HTML y flujo de navegación.",
            "Configuración y conexión con la base de datos PostgreSQL (Clever Cloud).",
            "Construcción de lógica para análisis de hábitos y recomendación de productos."
        ],
        "tecnologias": [
            "FastAPI", "Jinja2", "SQLAlchemy", "PostgreSQL", "HTML5", "CSS3", "JavaScript"
        ],
    }



# Endpoint con la información del diseño

@router.get("/info/diseno")
async def info_diseno():
    return {
        "colores": ["#a85d74", "#843a50"],
        "tipografia": "Montserrat y Roboto para una lectura clara y moderna.",
        "estructura": "Diseño limpio con navegación superior fija, secciones separadas claramente, formularios centrados y tarjetas de producto bien delimitadas.",

        "iconos": "Se usaron íconos de Font Awesome para facilitar la identificación visual."
    }



# Endpoint con el objetivo del proyecto

@router.get("/info/objetivo")
async def objetivo_proyecto():
    return {
        "objetivo_general": "Ofrecer una plataforma web que ayude a los usuarios a identificar y mejorar sus rutinas de cuidado de piel, recomendando productos adecuados según sus hábitos.",
        "justificacion": "Muchas personas no siguen rutinas adecuadas de cuidado facial debido a la falta de información personalizada. Esta plataforma busca llenar ese vacío mediante un sistema automatizado de recomendaciones basado en los hábitos del usuario.",
        "publico_objetivo": "Personas interesadas en mejorar su salud facial, especialmente quienes no tienen una rutina establecida o desean optimizarla.",
        "beneficios": [
            "Evaluación personalizada de hábitos",
            "Recomendaciones automáticas de productos según necesidades individuales",
            "Interfaz amigable y accesible",
            "Facilita la creación de recomendaciones personalizadas",
        ]
    }

