from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid, os, json, shutil
from datetime import datetime

from unidecode import unidecode

from app_.api.models import User, Habito,Producto, Rutina, RutinaProducto
from app_.core.dbconnection import get_db, engine
from app_.core.supabase_config import supabase  # ✅ ya tienes esto
from supabase import create_client


# ==============================
# Configuración de router y plantillas
# ==============================
router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")

@router.get("/check-tables")
async def check_tables():
    """
    Endpoint para listar todas las tablas de la base de datos.
    """
    try:
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}
# ==============================
# Páginas principales
# ==============================
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/test_habitos", response_class=HTMLResponse)
async def test_habitos(request: Request):
    return templates.TemplateResponse("test_habitos.html", {"request": request})


@router.get("/rutina", response_class=HTMLResponse)
async def rutina(request: Request):
    return templates.TemplateResponse("rutina.html", {"request": request})


# ==============================
# Configuración de Supabase (segura y testeable)
# ==============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "usuarios")


def get_supabase_client():
    """Crea o devuelve el cliente de Supabase de forma segura."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("⚠️ Supabase no configurado correctamente (faltan variables de entorno).")
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        print(f"💥 Error al crear cliente Supabase: {e}")
        return None


# ✅ Ahora la variable `supabase` existe a nivel de módulo
supabase = get_supabase_client()


# ==============================
# API: Registrar usuario
# ==============================

@router.post("/api/usuarios")
async def registrar_usuario(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        print("📥 Datos recibidos:", data)

        nombre = data.get("name") or data.get("nombre")
        correo = data.get("email") or data.get("mail")
        quiz = data.get("quiz", {})

        if not nombre or not correo:
            raise HTTPException(status_code=400, detail="Faltan datos del usuario.")

        # Verificar si el usuario ya existe
        existing_user = (await db.execute(select(User).where(User.correo == correo))).scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya está registrado.")

        # Crear nuevo usuario
        nuevo_usuario = User(nombre=nombre, correo=correo)
        db.add(nuevo_usuario)
        await db.commit()  # <-- commit para guardar realmente
        await db.refresh(nuevo_usuario)  # <-- refresca la instancia con el id generado

        # Crear hábitos asociados
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
        await db.commit()  # commit para guardar hábitos también

        perfil_url = f"/perfil?email={correo}"
        return {
            "message": "Usuario y hábitos registrados correctamente",
            "id": nuevo_usuario.id,
            "email": correo,
            "perfil_url": perfil_url
        }

    except Exception as e:
        print(f"💥 Error en registrar_usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/usuarios/{user_id}")
async def actualizar_usuario(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    query = select(User).where(User.id == user_id)
    usuario = (await db.execute(query)).scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = data.get("name", usuario.nombre)
    usuario.correo = data.get("mail", usuario.correo)
    await db.commit()
    await db.refresh(usuario)
    return {"message": "Usuario actualizado", "usuario": usuario}

@router.delete("/api/usuarios/{user_id}")
async def eliminar_usuario(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    usuario = (await db.execute(query)).scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(usuario)
    await db.commit()
    return {"message": "Usuario eliminado"}

@router.get("/api/usuarios")
async def obtener_usuario(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.correo == email)
    result = await db.execute(query)
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo
    }


# ==============================
# API: Generar rutina personalizada
# ============================== # pip install unidecode

@router.get("/api/rutina")
async def generar_rutina(email: str, db: AsyncSession = Depends(get_db)):
    from unidecode import unidecode

    print(f"📩 Generando rutina para: {email}")
    try:
        # ✅ Buscar usuario
        result_user = await db.execute(select(User).where(User.correo == email))
        usuario = result_user.scalars().first()
        if not usuario:
            return {"manana": [], "noche": [], "error": "Usuario no encontrado"}

        # ✅ Buscar hábito
        result_habito = await db.execute(select(Habito).where(Habito.usuario_id == usuario.id))
        habito = result_habito.scalars().first()
        if not habito or not habito.tipo_piel:
            return {"manana": [], "noche": [], "error": "No hay hábitos o tipo de piel registrado"}

        # ✅ Cliente Supabase
        global supabase
        if not supabase:
            supabase = get_supabase_client()
        if not supabase:
            return {"manana": [], "noche": [], "error": "Supabase no configurado"}

        # ✅ Obtener productos
        resp = supabase.table("productos").select("*").execute()
        productos = resp.data or []

        if not productos:
            return {"manana": [], "noche": [], "error": "No se encontraron productos en Supabase"}

        # 🔤 Función de normalización
        def normalizar(texto):
            return unidecode((texto or "").strip().lower())

        tipo_piel_usuario = normalizar(habito.tipo_piel)
        print(f"👤 Tipo de piel usuario: {tipo_piel_usuario}")

        # 🔍 Intentar detectar si el campo es 'skin_type' o 'tipo_piel'
        ejemplo = productos[0]
        campo_piel = "skin_type" if "skin_type" in ejemplo else "tipo_piel" if "tipo_piel" in ejemplo else None
        campo_tipo = "product_type" if "product_type" in ejemplo else "tipo_producto" if "tipo_producto" in ejemplo else None

        if not campo_piel or not campo_tipo:
            return {"manana": [], "noche": [], "error": "Campos de producto no encontrados"}

        # ✅ Filtrar productos por tipo de piel
        productos_filtrados = [
            p for p in productos if normalizar(p.get(campo_piel)) == tipo_piel_usuario
        ]

        print(f"🧴 Productos filtrados por piel ({habito.tipo_piel}): {len(productos_filtrados)}")

        # ✅ Tipos de producto y mini descripciones
        tipos_manana = ["limpiador", "cleanser", "hidratante", "moisturiser", "bloqueador solar", "sunscreen", "serum"]
        tipos_noche = ["limpiador", "cleanser", "exfoliante", "scrub", "hidratante", "moisturiser", "serum"]

        descripciones = {
            "limpiador": "Úsalo para limpiar tu rostro al comenzar el día o antes de dormir.",
            "cleanser": "Aplica una pequeña cantidad para limpiar suavemente tu piel.",
            "hidratante": "Mantén tu piel suave aplicando después del limpiador.",
            "moisturiser": "Mantén tu piel suave aplicando después del limpiador.",
            "bloqueador solar": "Aplícalo al final de tu rutina de la mañana para protegerte del sol.",
            "sunscreen": "Aplícalo al final de tu rutina de la mañana para protegerte del sol.",
            "exfoliante": "Úsalo 2-3 veces por semana para eliminar células muertas.",
            "scrub": "Úsalo 2-3 veces por semana para eliminar células muertas.",
            "serum": "Aplica unas gotas antes del hidratante para mejores resultados."
        }

        # ✅ Crear rutina con mini descripciones
        rutina_manana = [
            {
                **p,
                "mini_desc": descripciones.get(normalizar(p.get(campo_tipo)), "Producto para el cuidado diario de tu piel.")
            }
            for p in productos_filtrados
            if normalizar(p.get(campo_tipo)) in tipos_manana
        ]

        rutina_noche = [
            {
                **p,
                "mini_desc": descripciones.get(normalizar(p.get(campo_tipo)), "Producto ideal para tu rutina nocturna.")
            }
            for p in productos_filtrados
            if normalizar(p.get(campo_tipo)) in tipos_noche
        ]

        print(f"☀️ {len(rutina_manana)} productos mañana, 🌙 {len(rutina_noche)} productos noche")

        if not rutina_manana and not rutina_noche:
            return {"manana": [], "noche": [], "error": "No hay productos recomendados para tu rutina."}

        return {"manana": rutina_manana[:3], "noche": rutina_noche[:3]}

    except Exception as e:
        print(f"💥 Error inesperado al generar rutina: {e}")
        return {"manana": [], "noche": [], "error": str(e)}





@router.get("/perfil", response_class=HTMLResponse)
async def perfil(request: Request, email: str, db: AsyncSession = Depends(get_db)):
    # Buscar usuario
    result = await db.execute(select(User).where(User.correo == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Buscar hábitos del usuario
    result_habitos = await db.execute(select(Habito).where(Habito.usuario_id == user.id))
    habitos = result_habitos.scalars().all()

    # Buscar rutina asociada (si existe)
    result_rutina = await db.execute(select(Rutina).where(Rutina.usuario_id == user.id))
    rutina = result_rutina.scalars().first()

    # Buscar productos asociados a la rutina
    productos = []
    if rutina:
        result_productos = await db.execute(
            select(Producto)
            .join(RutinaProducto)
            .where(RutinaProducto.rutina_id == rutina.id)
        )
        productos = result_productos.scalars().all()

    # Renderizar plantilla
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "usuario": user,
            "habitos": habitos,
            "productos": productos,
        }
    )



@router.post("/api/productos")
async def crear_producto(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    producto = Producto(**data)
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return {"message": "Producto creado", "producto_id": producto.id}

@router.get("/api/productos/{producto_id}")
async def leer_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Producto).where(Producto.id == producto_id)
    producto = (await db.execute(query)).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.put("/api/productos/{producto_id}")
async def actualizar_producto(producto_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    query = select(Producto).where(Producto.id == producto_id)
    producto = (await db.execute(query)).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in data.items():
        setattr(producto, key, value)
    await db.commit()
    await db.refresh(producto)
    return {"message": "Producto actualizado", "producto": producto}

@router.delete("/api/productos/{producto_id}")
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Producto).where(Producto.id == producto_id)
    producto = (await db.execute(query)).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    await db.delete(producto)
    await db.commit()
    return {"message": "Producto eliminado"}

# ==============================
# API: Obtener productos según usuario
# ==============================
@router.get("/api/productos/usuario/{usuario_id}")
async def obtener_productos_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """
    Devuelve los productos recomendados para un usuario según su tipo de piel.
    """
    # 1️⃣ Obtener el hábito del usuario
    query_habito = select(Habito).where(Habito.usuario_id == usuario_id)
    result_habito = await db.execute(query_habito)
    habito = result_habito.scalars().first()

    # Si no hay hábito, retornar lista vacía
    if not habito or not habito.tipo_piel:
        raise HTTPException(status_code=404, detail="No hay hábitos o tipo de piel definido")

    tipo_piel = habito.tipo_piel

    # 2️⃣ Traer productos del Supabase filtrando por tipo de piel
    global supabase
    if not supabase:
        supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    try:
        resp = supabase.table("productos").select("*").eq("skin_type", tipo_piel).execute()
        productos = resp.data or []

        # 3️⃣ Formatear la respuesta
        return [
            {
                "id": p.get("id"),
                "product_name": p.get("product_name"),
                "product_type": p.get("product_type"),
                "clean_ingreds": p.get("clean_ingreds"),
                "product_url": p.get("product_url"),
                "image_url": p.get("image_url")
            }
            for p in productos
        ]

    except Exception as e:
        print(f"💥 Error al obtener productos: {e}")
        return []




@router.get("/api/habitos/usuario/{usuario_id}")
async def obtener_habitos(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """
    Devuelve los hábitos de un usuario dado su ID.
    """
    query = select(Habito).where(Habito.usuario_id == usuario_id)
    result = await db.execute(query)
    habitos = result.scalars().all()

    if not habitos:
        raise HTTPException(status_code=404, detail="No hay hábitos registrados")

    # Retornamos en formato JSON
    return [
        {
            "lavarse_cara": h.lavarse_cara,
            "protector_solar": h.protector_solar,
            "exfoliacion": h.exfoliacion,
            "tipo_piel": h.tipo_piel,
            "objetivo": h.objetivo,
            "edad": h.edad
        }
        for h in habitos
    ]