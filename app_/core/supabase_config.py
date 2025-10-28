import os
from supabase import create_client

# ==============================
# Inicialización segura de Supabase
# ==============================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase inicializado correctamente")
    else:
        print("⚠️ Variables de entorno de Supabase no configuradas.")
except Exception as e:
    print(f"💥 Error al inicializar Supabase: {e}")
    supabase = None
