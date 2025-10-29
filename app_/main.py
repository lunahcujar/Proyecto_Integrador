from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app_.core.dbconnection import get_db
from app_.templates.routes import router as views_router
from sqlalchemy import inspect
from app_.core.dbconnection import engine
# Cargar variables de entorno (.env)
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(title="Sistema de Cuidado de la Piel", version="1.0")

# Montar carpeta estática para imágenes, CSS y JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir las rutas HTML (home, registro, test_habitos, etc.)
app.include_router(views_router)

from app_.core.dbconnection import create_async_engine
@app.get("/check-tables")
async def check_tables():
    async with create_async_engine() as conn:
        # Aquí usamos run_sync para inspeccionar
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        return {"tables": tables}
# ========================================
# EVENTO DE INICIO
# ========================================

# ========================================
# MANEJO GLOBAL DE ERRORES
# ========================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Personaliza los mensajes de error HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": "Carambas, algo falló 😅",
            "detail": exc.detail,
            "path": str(request.url),
        },
    )

# ========================================
# RUTA RAÍZ POR DEFECTO (opcional)
# ========================================
@app.get("/")
async def root():
    """Redirige al home.html o muestra un mensaje simple."""
    return {"message": "Bienvenido a la API del Sistema de Cuidado de la Piel 💆‍♀️"}
