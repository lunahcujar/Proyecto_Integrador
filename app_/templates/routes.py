from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
)
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid, os, json
from datetime import datetime
from app_.api.models import *

from app_.core.dbconnection import get_db
from app_.api.models import User, Habito
from supabase import create_client
from fastapi.responses import RedirectResponse
import shutil

# ==============================
# Configuración de router y plantillas
# ==============================
router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")

# ==============================
# Página principal (Home)
# ==============================
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ==============================
# Test de Hábitos
# ==============================
@router.get("/test_habitos", response_class=HTMLResponse)
async def test_habitos(request: Request):
    return templates.TemplateResponse("test_habitos.html", {"request": request})

# ==============================
# Página de rutina
# ==============================
@router.get("/rutina", response_class=HTMLResponse)
async def rutina(request: Request):
    return templates.TemplateResponse("rutina.html", {"request": request})

# ==============================
# Configuración de Supabase (opcional)
# ==============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "usuarios")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception:
    supabase = None

# ==============================
# API: Registrar usuario
# ==============================
@router.post("/api/usuarios")
async def registrar_usuario(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    nombre = data.get("name")
    correo = data.get("mail")
    quiz = data.get("quiz", {})

    if not nombre or not correo:
        raise HTTPException(status_code=400, detail="Faltan datos del usuario.")

    # Verificar si el usuario ya existe
    existing_user = await db.execute(select(User).where(User.correo == correo))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El usuario ya está registrado.")

    # Crear el usuario
    nuevo_usuario = User(nombre=nombre, correo=correo)
    db.add(nuevo_usuario)
    await db.flush()  # Para obtener el ID antes de commit

    # Extraer respuestas del test
    habit_data = Habito(
        usuario_id=nuevo_usuario.id,
        lavarse_cara=quiz.get("pregunta_1"),
        protector_solar=quiz.get("pregunta_2"),
        exfoliacion=quiz.get("pregunta_3"),
        tipo_piel=quiz.get("pregunta_4"),
        objetivo=quiz.get("pregunta_5"),
        edad=int(quiz.get("pregunta_6", 0)) if quiz.get("pregunta_6") else None
    )

    db.add(habit_data)
    await db.commit()

    return {"message": "Usuario y hábitos registrados correctamente"}
# ==============================
# API: Guardar hábitos
# ==============================
@router.post("/api/habitos")
async def crear_habito(
    nombre: str = Form(...),
    correo: str = Form(...),
    edad: int = Form(None),
    quiz: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        respuestas = json.loads(quiz)
        nuevo_habito = Habito(
            nombre=nombre,
            correo=correo,
            edad=edad,
            respuestas=respuestas
        )
        db.add(nuevo_habito)
        await db.commit()
        await db.refresh(nuevo_habito)
        return {"mensaje": "Hábito guardado correctamente", "id": nuevo_habito.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/usuarios/{id}")
async def actualizar_usuario(id: int, datos: UserUpdate, db: AsyncSession = Depends(get_db)):
    usuario = await db.get(User, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.edad is not None:
        usuario.edad = datos.edad
    if datos.foto_url is not None:
        usuario.foto_url = datos.foto_url

    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.get("/perfil/{usuario_id}")
async def mostrar_perfil(usuario_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    usuario = await db.get(User, usuario_id)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("perfil.html", {"request": request, "usuario": usuario})


@router.post("/perfil/{usuario_id}")
async def actualizar_perfil(
    usuario_id: int,
    edad: int = Form(None),
    foto: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    usuario = await db.get(User, usuario_id)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    if edad:
        usuario.edad = edad

    if foto:
        path = f"static/img/perfiles/{usuario_id}_{foto.filename}"
        os.makedirs("static/img/perfiles", exist_ok=True)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        usuario.foto_url = f"/{path}"

    await db.commit()
    return RedirectResponse(url=f"/perfil/{usuario_id}", status_code=303)



@router.get("/api/rutina")
async def generar_rutina(email: str, db: AsyncSession = Depends(get_db)):
    print(f"📩 Recibiendo solicitud de rutina para: {email}")
    try:
        usuario = await db.execute(select(User).where(User.correo == email))
        usuario = usuario.scalars().first()
        if not usuario:
            print("❌ Usuario no encontrado")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        habito = await db.execute(select(Habito).where(Habito.usuario_id == usuario.id))
        habito = habito.scalars().first()
        if not habito:
            print("❌ No hay hábitos registrados")
            raise HTTPException(status_code=404, detail="No hay hábitos registrados")

        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conexión a Supabase exitosa")

        resp = supabase.table("productos").select("*").eq("skin_type", habito.tipo_piel).execute()
        productos = resp.data
        print(f"🧴 Productos encontrados: {len(productos)} para piel {habito.tipo_piel}")

        def normalizar_tipo(tipo):
            return tipo.lower().strip()

        tipos_manana = ["limpiador", "cleanser", "hidratante", "moisturizer", "bloqueador solar", "sunscreen"]
        tipos_noche = ["limpiador", "cleanser", "exfoliante", "scrub", "hidratante", "moisturizer"]

        rutina_manana = [p for p in productos if normalizar_tipo(p["product_type"]) in tipos_manana]
        rutina_noche = [p for p in productos if normalizar_tipo(p["product_type"]) in tipos_noche]

        print(f"🌞 Rutina mañana: {len(rutina_manana)} productos")
        print(f"🌙 Rutina noche: {len(rutina_noche)} productos")

        return {
            "manana": rutina_manana[:3],
            "noche": rutina_noche[:3]
        }

    except Exception as e:
        print(f"💥 Error al generar rutina: {e}")
        raise HTTPException(status_code=500, detail=str(e))
