from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid, os, json, shutil
from datetime import datetime
from app_.api.models import User, Habito
from app_.core.dbconnection import get_db
from app_.core.supabase_config import supabase  # ✅ ya tienes esto
from supabase import create_client


# ==============================
# Configuración de router y plantillas
# ==============================
router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")


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
    data = await request.json()
    nombre = data.get("name")
    correo = data.get("mail")
    quiz = data.get("quiz", {})

    if not nombre or not correo:
        raise HTTPException(status_code=400, detail="Faltan datos del usuario.")

    try:
        query = select(User).where(User.correo == correo)
        raw_result = await db.execute(query)

        result = None
        try:
            if hasattr(raw_result, "scalars"):
                result = raw_result.scalars().first()
            elif hasattr(raw_result, "first"):
                maybe_coro = raw_result.first
                if callable(maybe_coro):
                    maybe_val = maybe_coro()
                    result = await maybe_val if hasattr(maybe_val, "__await__") else maybe_val
                else:
                    result = maybe_coro
        except Exception as e:
            print("⚠️ Error interno manejando raw_result:", e)

        if result:
            raise HTTPException(status_code=400, detail="El usuario ya está registrado.")

        nuevo_usuario = User(nombre=nombre, correo=correo)
        db.add(nuevo_usuario)
        await db.flush()

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

        return {"message": "Usuario y hábitos registrados correctamente"}

    except Exception as e:
        print(f"💥 Error en registrar_usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# API: Generar rutina personalizada
# ==============================
@router.get("/api/rutina")
async def generar_rutina(email: str, db: AsyncSession = Depends(get_db)):
    print(f"📩 Recibiendo solicitud de rutina para: {email}")
    try:
        query_user = select(User).where(User.correo == email)
        raw_user = await db.execute(query_user)
        usuario = raw_user.scalars().first() if hasattr(raw_user, "scalars") else None

        if not usuario:
            print("❌ Usuario no encontrado")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        query_habito = select(Habito).where(Habito.usuario_id == usuario.id)
        raw_habito = await db.execute(query_habito)
        habito = raw_habito.scalars().first() if hasattr(raw_habito, "scalars") else None

        if not habito:
            print("❌ No hay hábitos registrados")
            raise HTTPException(status_code=404, detail="No hay hábitos registrados")

        # ✅ Aquí el test podrá reemplazar `supabase`
        global supabase
        if not supabase:
            supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase no configurado")

        print("✅ Conexión a Supabase exitosa")
        resp = supabase.table("productos").select("*").eq("skin_type", habito.tipo_piel).execute()
        productos = resp.data or []
        print(f"🧴 Productos encontrados: {len(productos)} para piel {habito.tipo_piel}")

        def normalizar_tipo(tipo):
            return tipo.lower().strip()

        tipos_manana = ["limpiador", "cleanser", "hidratante", "moisturizer", "bloqueador solar", "sunscreen"]
        tipos_noche = ["limpiador", "cleanser", "exfoliante", "scrub", "hidratante", "moisturizer"]

        rutina_manana = [p for p in productos if normalizar_tipo(p["product_type"]) in tipos_manana]
        rutina_noche = [p for p in productos if normalizar_tipo(p["product_type"]) in tipos_noche]

        return {
            "manana": rutina_manana[:3],
            "noche": rutina_noche[:3]
        }

    except Exception as e:
        print(f"💥 Error al generar rutina: {e}")
        raise HTTPException(status_code=500, detail=str(e))
