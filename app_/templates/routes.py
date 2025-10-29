from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
)
from fastapi.responses import HTMLResponse
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from unidecode import unidecode

from app_.api.models import User, Habito, Producto, Rutina, RutinaProducto
from app_.core.dbconnection import get_db, engine
from app_.core.supabase_config import supabase
from supabase import create_client

router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")

# ==============================
# Páginas HTML
# ==============================
@router.get("/", response_class=HTMLResponse, tags=["Páginas"])
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/test_habitos", response_class=HTMLResponse, tags=["Páginas"])
async def test_habitos(request: Request):
    return templates.TemplateResponse("test_habitos.html", {"request": request})

@router.get("/rutina", response_class=HTMLResponse, tags=["Páginas"])
async def rutina(request: Request):
    return templates.TemplateResponse("rutina.html", {"request": request})

@router.get("/perfil", response_class=HTMLResponse, tags=["Páginas"])
async def perfil(request: Request, email: str, db: AsyncSession = Depends(get_db)):
    # Buscar usuario
    result = await db.execute(select(User).where(User.correo == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Buscar hábitos
    result_habitos = await db.execute(select(Habito).where(Habito.usuario_id == user.id))
    habitos = result_habitos.scalars().all()
    # Buscar rutina y productos
    productos = []
    result_rutina = await db.execute(select(Rutina).where(Rutina.usuario_id == user.id))
    rutina = result_rutina.scalars().first()
    if rutina:
        result_productos = await db.execute(
            select(Producto).join(RutinaProducto).where(RutinaProducto.rutina_id == rutina.id)
        )
        productos = result_productos.scalars().all()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "usuario": user, "habitos": habitos, "productos": productos}
    )

# ==============================
# Usuarios
# ==============================
@router.post("/api/usuarios", tags=["Usuarios"], summary="Registrar un usuario")
async def registrar_usuario(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario y sus hábitos.
    """
    data = await request.json()
    nombre = data.get("name") or data.get("nombre")
    correo = data.get("email") or data.get("mail")
    quiz = data.get("quiz", {})

    if not nombre or not correo:
        raise HTTPException(status_code=400, detail="Faltan datos del usuario.")

    existing_user = (await db.execute(select(User).where(User.correo == correo))).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado.")

    nuevo_usuario = User(nombre=nombre, correo=correo)
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)

    habit_data = Habito(
        usuario_id=nuevo_usuario.id,
        lavarse_cara=quiz.get("pregunta_1"),
        protector_solar=quiz.get("pregunta_2"),
        exfoliacion=quiz.get("pregunta_3"),
        tipo_piel=quiz.get("pregunta_4"),
        objetivo=quiz.get("pregunta_5"),
        edad=int(quiz.get("pregunta_6", 0)) if quiz.get("pregunta_6") else None,
    )
    db.add(habit_data)
    await db.commit()

    return {"message": "Usuario y hábitos registrados correctamente", "id": nuevo_usuario.id, "email": correo}

@router.put("/api/usuarios/{user_id}", tags=["Usuarios"], summary="Actualizar usuario")
async def actualizar_usuario(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    usuario = (await db.execute(select(User).where(User.id == user_id))).scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = data.get("name", usuario.nombre)
    usuario.correo = data.get("mail", usuario.correo)
    await db.commit()
    await db.refresh(usuario)
    return {"message": "Usuario actualizado", "usuario": usuario}

@router.delete("/api/usuarios/{user_id}", tags=["Usuarios"], summary="Eliminar usuario")
async def eliminar_usuario(user_id: int, db: AsyncSession = Depends(get_db)):
    usuario = (await db.execute(select(User).where(User.id == user_id))).scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(usuario)
    await db.commit()
    return {"message": "Usuario eliminado"}

@router.get("/api/usuarios", tags=["Usuarios"], summary="Obtener usuario por correo")
async def obtener_usuario(email: str, db: AsyncSession = Depends(get_db)):
    usuario = (await db.execute(select(User).where(User.correo == email))).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo}

# ==============================
# Hábitos
# ==============================
@router.get("/api/habitos/usuario/{usuario_id}", tags=["Hábitos"], summary="Obtener hábitos de un usuario")
async def obtener_habitos(usuario_id: int, db: AsyncSession = Depends(get_db)):
    habitos = (await db.execute(select(Habito).where(Habito.usuario_id == usuario_id))).scalars().all()
    if not habitos:
        raise HTTPException(status_code=404, detail="No hay hábitos registrados")
    return [{"lavarse_cara": h.lavarse_cara, "protector_solar": h.protector_solar,
             "exfoliacion": h.exfoliacion, "tipo_piel": h.tipo_piel,
             "objetivo": h.objetivo, "edad": h.edad} for h in habitos]

# ==============================
# Productos
# ==============================
@router.post("/api/productos", tags=["Productos"], summary="Crear un producto")
async def crear_producto(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    producto = Producto(**data)
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return {"message": "Producto creado", "producto_id": producto.id}

@router.get("/api/productos/{producto_id}", tags=["Productos"], summary="Leer un producto")
async def leer_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = (await db.execute(select(Producto).where(Producto.id == producto_id))).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.put("/api/productos/{producto_id}", tags=["Productos"], summary="Actualizar producto")
async def actualizar_producto(producto_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    producto = (await db.execute(select(Producto).where(Producto.id == producto_id))).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in data.items():
        setattr(producto, key, value)
    await db.commit()
    await db.refresh(producto)
    return {"message": "Producto actualizado", "producto": producto}

@router.delete("/api/productos/{producto_id}", tags=["Productos"], summary="Eliminar producto")
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = (await db.execute(select(Producto).where(Producto.id == producto_id))).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    await db.delete(producto)
    await db.commit()
    return {"message": "Producto eliminado"}

@router.get("/api/productos/usuario/{usuario_id}", tags=["Productos"], summary="Productos recomendados para un usuario")
async def obtener_productos_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    habito = (await db.execute(select(Habito).where(Habito.usuario_id == usuario_id))).scalars().first()
    if not habito or not habito.tipo_piel:
        raise HTTPException(status_code=404, detail="No hay hábitos o tipo de piel definido")
    global supabase
    if not supabase:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    resp = supabase.table("productos").select("*").eq("skin_type", habito.tipo_piel).execute()
    productos = resp.data or []
    return [{"id": p.get("id"), "product_name": p.get("product_name"),
             "product_type": p.get("product_type"), "clean_ingreds": p.get("clean_ingreds"),
             "product_url": p.get("product_url"), "image_url": p.get("image_url")} for p in productos]

# ==============================
# Rutina
# ==============================
@router.get("/api/rutina", tags=["Rutina"], summary="Generar rutina personalizada")
async def generar_rutina(email: str, db: AsyncSession = Depends(get_db)):
    # (Aquí puedes pegar tu endpoint corregido de rutina que te pasé antes)
    ...

# ==============================
# Comprobación de tablas
# ==============================
@router.get("/check-tables", tags=["Debug"], summary="Verificar tablas en DB")
async def check_tables():
    try:
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}
