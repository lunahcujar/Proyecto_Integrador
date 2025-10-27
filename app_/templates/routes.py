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
from app_.api.models import User, Habit
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
async def registrar_usuario(
    name: str = Form(...),
    mail: str = Form(...),
    quiz: str = Form(None),  # respuestas del test
    db: AsyncSession = Depends(get_db)
):
    try:
        # Verificar si el correo ya existe
        result = await db.execute(select(User).where(User.correo == mail))
        usuario_existente = result.scalars().first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado.")

        # Crear nuevo usuario
        nuevo_usuario = User(
            nombre=name,
            correo=mail,
            foto_url=None  # ya no se solicita foto
        )
        db.add(nuevo_usuario)
        await db.commit()
        await db.refresh(nuevo_usuario)

        # Procesar y guardar los hábitos (respuestas del test)
        if quiz:
            try:
                respuestas = json.loads(quiz)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Error al procesar las respuestas del test.")

            for pregunta, respuesta in respuestas.items():
                nuevo_habito = Habit(
                    user_id=nuevo_usuario.id,
                    pregunta=pregunta,
                    respuesta=respuesta
                )
                db.add(nuevo_habito)

            await db.commit()

        return {"mensaje": "✅ Usuario y hábitos registrados correctamente."}

    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"❌ Error al registrar usuario: {str(e)}")

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
