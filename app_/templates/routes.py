import csv
import unicodedata
from random import random, shuffle

from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, Query
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import uuid4
import os

from starlette.responses import JSONResponse

# Modelos y conexión
from app_.api.models import User, Habito, Producto, Rutina, RutinaProducto, Consulta
from app_.core.dbconnection import get_db
from app_.core.supabase_config import supabase

# =====================================================
# Inicialización del router y plantillas
# =====================================================
router = APIRouter()
templates = Jinja2Templates(directory="app_/templates")

# =====================================================
# RUTAS HTML
# =====================================================
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
    """
    Carga el perfil del usuario con sus hábitos y productos de rutina.
    """
    result = await db.execute(select(User).where(User.correo == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    result_habitos = await db.execute(select(Habito).where(Habito.usuario_id == user.id))
    habitos = result_habitos.scalars().all()

    productos = []
    result_rutina = await db.execute(select(Rutina).where(Rutina.usuario_id == user.id))
    rutina = result_rutina.scalars().first()
    if rutina:
        result_productos = await db.execute(
            select(Producto)
            .join(RutinaProducto)
            .where(RutinaProducto.rutina_id == rutina.id)
        )
        productos = result_productos.scalars().all()

    return templates.TemplateResponse(
        "users.html",
        {"request": request, "usuario": user, "habitos": habitos, "productos": productos}
    )

# =====================================================
# USUARIOS
# =====================================================
@router.post("/api/usuarios", tags=["Usuarios"])
async def registrar_usuario(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario junto con sus hábitos iniciales.
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

    return {"message": "Usuario y hábitos registrados correctamente", "email": correo}


@router.get("/api/usuarios", tags=["Usuarios"])
async def obtener_usuario(email: str, db: AsyncSession = Depends(get_db)):
    usuario = (await db.execute(select(User).where(User.correo == email))).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo}

# =====================================================
# PRODUCTOS
# =====================================================
@router.post("/api/productos", tags=["Productos"])
async def crear_producto(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    producto = Producto(**data)
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return {"message": "Producto creado", "producto_id": producto.id}


@router.get("/api/productos/{producto_id}", tags=["Productos"])
async def leer_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = (await db.execute(select(Producto).where(Producto.id == producto_id))).scalars().first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/api/generar_rutina", tags=["Rutina"], summary="Generar rutina personalizada y guardarla")
async def generar_rutina(email: str, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar usuario
        usuario = (await db.execute(
            select(User).where(User.correo == email)
        )).scalar_one_or_none()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Eliminar rutina anterior COMPLETA (rutina + productos asociados)
        rutina_existente = (await db.execute(
            select(Rutina).where(Rutina.usuario_id == usuario.id)
        )).scalar_one_or_none()

        if rutina_existente:
            await db.execute(
                delete(RutinaProducto).where(RutinaProducto.rutina_id == rutina_existente.id)
            )
            await db.delete(rutina_existente)
            await db.commit()

        # Crear nueva rutina
        nueva_rutina = Rutina(usuario_id=usuario.id)
        db.add(nueva_rutina)
        await db.commit()
        await db.refresh(nueva_rutina)

        # Obtener productos
        productos = (await db.execute(select(Producto))).scalars().all()

        if not productos:
            raise HTTPException(status_code=404, detail="No hay productos disponibles")

        from random import shuffle
        shuffle(productos)

        seleccionados = productos[:6]

        # Asociar productos
        for p in seleccionados:
            db.add(RutinaProducto(rutina_id=nueva_rutina.id, producto_id=p.id))

        await db.commit()

        # Respuesta limpia
        return {
            "mensaje": "Rutina generada exitosamente",
            "usuario": usuario.correo,
            "productos_asociados": [
                {
                    "id": p.id,
                    "nombre": p.product_name,
                    "tipo": p.product_type,
                    "tipo_piel": p.skin_type,
                    "precio": p.price,
                    "imagen": p.image_url or "https://via.placeholder.com/200"
                }
                for p in seleccionados
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar rutina: {str(e)}")


def normalizar(texto: str) -> str:
    """
    Convierte a minúsculas y elimina acentos para comparaciones.
    """
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode().lower()

@router.get("/api/rutina", tags=["Rutina"], summary="Obtener rutina personalizada del usuario")
async def obtener_rutina_usuario(email: str, db: AsyncSession = Depends(get_db)):
    try:
        # 🔹 Buscar usuario
        usuario = (await db.execute(select(User).where(User.correo == email))).scalar_one_or_none()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # 🔹 Buscar rutina asociada
        rutina = (await db.execute(select(Rutina).where(Rutina.usuario_id == usuario.id))).scalar_one_or_none()
        if not rutina:
            raise HTTPException(status_code=404, detail="No se encontró rutina para este usuario")

        # 🔹 Obtener los productos asociados a la rutina
        productos = (await db.execute(
            select(Producto)
            .join(RutinaProducto, Producto.id == RutinaProducto.producto_id)
            .where(RutinaProducto.rutina_id == rutina.id)
        )).scalars().all()

        if not productos:
            raise HTTPException(status_code=404, detail="No hay productos asociados a la rutina")

        # 🔹 Organizar los productos según el momento del día
        rutina_organizada = {
            "mañana": [p for p in productos if any(x in normalizar(p.product_type) for x in ["bloqueador", "protector", "limpiador"])],
            "tarde": [p for p in productos if any(x in normalizar(p.product_type) for x in ["tonico", "hidratante", "serum"])],
            "noche": [p for p in productos if any(x in normalizar(p.product_type) for x in ["exfoliante", "mascarilla", "crema", "aceite"])],
        }

        # 🔹 Estructurar respuesta final
        rutina_final = {
            "usuario": usuario.correo,
            "rutina_id": str(rutina.id),
            "rutina": {
                momento: [
                    {
                        "id": p.id,
                        "nombre": p.product_name,
                        "descripcion": p.product_type,
                        "tipo_piel": p.skin_type,
                        "precio": p.price,
                        "imagen": p.image_url
                    }
                    for p in productos_list
                ]
                for momento, productos_list in rutina_organizada.items() if productos_list
            }
        }

        return rutina_final

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


CSV_FILE = "/home/lunahcujar/PycharmProjects/Proyecto_Integrador/usuarios.csv"


# app_/routes/usuario.py  (o donde tengas el router)
from fastapi import APIRouter, HTTPException, Query, Body
from sqlalchemy.orm import Session
@router.put("/api/editar_usuario", tags=["Usuario"])
async def editar_usuario(
    correo: str = Query(..., description="Correo del usuario a editar"),
    datos: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Edita cualquier campo del usuario y/o sus hábitos.
    Puedes enviar solo los campos que quieras modificar.
    """
    try:
        # ================================
        # 1. Buscar usuario por correo
        # ================================
        usuario = (
            await db.execute(select(User).where(User.correo == correo))
        ).scalar_one_or_none()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cambios = []

        # ================================
        # 2. Editar campos del usuario
        # ================================
        if "nombre" in datos and datos["nombre"]:
            usuario.nombre = datos["nombre"].strip()
            cambios.append("nombre")

        # Nuevo: permitir cambiar el correo
        if "correo" in datos and datos["correo"]:
            nuevo_correo = datos["correo"].strip()

            # Verificar que no exista ya
            existe = (
                await db.execute(select(User).where(User.correo == nuevo_correo))
            ).scalar_one_or_none()

            if existe and existe.id != usuario.id:
                raise HTTPException(
                    status_code=400,
                    detail="Ese correo ya está registrado por otro usuario"
                )

            usuario.correo = nuevo_correo
            cambios.append("correo")

        # ================================
        # 3. Obtener o crear hábitos
        # ================================
        habito = (
            await db.execute(select(Habito).where(Habito.usuario_id == usuario.id))
        ).scalar_one_or_none()

        if not habito:
            habito = Habito(usuario_id=usuario.id)
            db.add(habito)

        # ================================
        # 4. Actualizar hábitos
        # ================================
        campos_habito = {
            "tipo_piel": str,
            "edad": int,
            "lavarse_cara": lambda x: str(x).lower() in ["true", "1", "yes", "sí", "si"],
            "protector_solar": lambda x: str(x).lower() in ["true", "1", "yes", "sí", "si"],
            "exfoliacion": str,
            "objetivo": str,
        }

        for campo, tipo in campos_habito.items():
            if campo in datos:
                val = datos[campo]
                if val in ["", None]:
                    setattr(habito, campo, None)
                else:
                    try:
                        setattr(habito, campo, tipo(val))
                    except:
                        setattr(habito, campo, None)

                cambios.append(campo)

        # ================================
        # 5. Guardar cambios
        # ================================
        await db.commit()
        await db.refresh(usuario)
        await db.refresh(habito)

        return {
            "mensaje": "Perfil actualizado correctamente",
            "usuario": usuario.correo,
            "campos_actualizados": cambios or ["No cambiaste ningún campo"]
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print("[ERROR EDITAR USUARIO]", str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar el perfil")



@router.delete("/api/eliminar_usuario", tags=["Usuario"])
async def eliminar_usuario(correo: str = Query(..., description="Correo del usuario a eliminar")):
    if not os.path.exists(CSV_FILE):
        raise HTTPException(status_code=404, detail="Archivo de usuarios no encontrado")

    usuarios = []
    eliminado = False

    # Leer usuarios y filtrar
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["correo"] == correo:
                eliminado = True
                continue  # no lo agregamos, se elimina
            usuarios.append(row)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Guardar cambios
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id","nombre","correo","tipo_piel","edad"])
        writer.writeheader()
        writer.writerows(usuarios)

    return {"mensaje": "Usuario eliminado correctamente", "correo": correo}


@router.get("/seguimiento")
async def seguimiento(request: Request):
    return templates.TemplateResponse("seguimiento.html", {"request": request})

@router.post("/api/seguimiento")
async def seguimiento_ia_alias(data: Consulta):
    respuesta = await dermatology_agent.chat("default_user", data.pregunta)
    return {"respuesta": respuesta}









# app_/routes/api.py (o como lo tengas)
from fastapi import APIRouter, Form, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os

# Tus módulos corregidos
from app_.ia_agent.agent import dermatology_agent
from app_.ia_agent.vision import analyze_skin_photo        # ← la versión async corregida
from app_.ia_agent.routines import generate_routine        # ← ahora es async
from app_.ia_agent.memory import get_user_memory, update_user_memory
from app_.ia_agent.chat import save_message                 # (opcional, ya no se usa aquí)

# Supabase
from supabase import create_client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))




# --------------------------------------------------
# 1. CHAT GENERAL (el más importante del frontend)
# --------------------------------------------------
@router.post("/chat")
async def chat_with_agent(
    user_id: str = Form(...),
    message: str = Form(...)
):
    if not user_id or not message.strip():
        raise HTTPException(400, detail="Falta user_id o mensaje")

    try:
        # El agente ya guarda el mensaje internamente (chat.py)

        response = await dermatology_agent(user_id, message)  # ← ¡ahora debe ser async!
        return {"reply": response}

    except Exception as e:
        print(f"[ERROR /chat] {e}")
        raise HTTPException(500, detail="Error del asistente dermatológico")


# --------------------------------------------------
# 2. ANÁLISIS DE FOTO DE PIEL (GPT-4 Vision)
# --------------------------------------------------

from app_.ia_agent.vision import analyze_skin_photo

@router.post("/skin-analysis")
async def analyze_skin(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not user_id:
        raise HTTPException(400, detail="user_id requerido")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, detail="Solo JPG, PNG o WebP")

    try:
        image_bytes = await file.read()
        analysis = await analyze_skin_photo(user_id, image_bytes, file.filename)
        return {"skin_condition": analysis}
    except Exception as e:
        print(f"[ERROR /skin-analysis] {e}")
        raise HTTPException(500, detail="Error analizando la imagen")
# --------------------------------------------------
# 3. GENERAR RUTINA PERSONALIZADA
# --------------------------------------------------
@router.post("/routine")
async def generate_routine_endpoint(user_id: str = Form(...)):
    if not user_id:
        raise HTTPException(400, detail="user_id requerido")

    try:
        routine = await generate_routine(user_id)  # ← async
        return {"routine": routine}
    except Exception as e:
        print(f"[ERROR /routine] {e}")
        raise HTTPException(500, detail="Error generando rutina")


# --------------------------------------------------
# 4. GUARDAR TEST DE PIEL (cuestionario)
# --------------------------------------------------
@router.post("/save-test")
async def save_test(
    user_id: str = Form(...),
    limpia: str = Form("false"),
    bloqueador: str = Form("false"),
    exfoliacion: str = Form("nunca")
):
    data = {
        "lava_cara": limpia.lower() == "true",
        "usa_bloqueador": bloqueador.lower() == "true",
        "frecuencia_exfoliacion": exfoliacion
    }
    update_user_memory(user_id, data)
    return {"message": "Test guardado correctamente", "data": data}


# --------------------------------------------------
# 5. OBTENER MEMORIA COMPLETA DEL USUARIO
# --------------------------------------------------
@router.get("/memory/{user_id}")
async def get_user_memory_endpoint(user_id: str):
    memory = get_user_memory(user_id)
    return memory or {}


# --------------------------------------------------
# 6. OBTENER O CREAR user_id POR EMAIL
# --------------------------------------------------
@router.post("/get_user_id")
async def get_user_id(request: Request):
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()

        if not email:
            return JSONResponse({"user_id": None})

        # Buscar usuario
        result = supabase.table("usuarios")\
            .select("id")\
            .eq("correo", email)\
            .execute()

        if result.data:
            return {"user_id": result.data[0]["id"]}

        # Crear si no existe
        new_user = supabase.table("usuarios").insert({
            "id": str(uuid.uuid4()),
            "correo": email,
            "created_at": "now()"
        }).execute()

        return {"user_id": new_user.data[0]["id"]}

    except Exception as e:
        print(f"[ERROR /get_user_id] {e}")
        return JSONResponse({"user_id": None})


