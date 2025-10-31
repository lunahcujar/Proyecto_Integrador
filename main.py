from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app_.templates.routes import router as app_router

# =====================================================
# Inicialización de la app
# =====================================================
app = FastAPI(
    title="Sistema de Cuidado de la Piel 💆‍♀️",
    version="1.0"
)

# =====================================================
# Configurar CORS (si tu frontend usa otro dominio)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Archivos estáticos (CSS, imágenes, JS)
# =====================================================
# ⚠️ Cambiado: ahora apunta correctamente a app_/static
app.mount("/static", StaticFiles(directory="static"), name="static")

# =====================================================
# Incluir rutas principales (usuarios, rutina, productos, vistas)
# =====================================================
app.include_router(app_router)

# =====================================================
# Ruta raíz → redirige al home.html
# =====================================================
@app.get("/", include_in_schema=False)
async def root():
    """
    Redirige automáticamente al home.html
    """
    return RedirectResponse(url="/home")
