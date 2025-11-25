# app_/ia_agent/memory.py
from supabase import create_client
import os
from typing import Dict, Any, Optional

# ------------------------------------------------------------------
# SUPABASE CLIENT (una sola instancia)
# ------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_memory(user_id: str) -> Dict[str, Any]:
    """
    Obtiene el perfil completo del usuario.
    SIEMPRE devuelve un diccionario (nunca None ni lanza error).

    ¿Por qué es mejor así?
    → Nunca se rompe el agente si el usuario es nuevo
    → Puedes usar memoria por defecto segura
    """
    try:
        response = (
            supabase.table("user_profile")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()  # ← ¡CLAVE! No falla si no existe
            .execute()
        )

        if response.data:
            return response.data
        else:
            # Usuario nuevo → memoria por defecto
            return {
                "tipo_piel": "desconocido",
                "lava_cara": None,
                "usa_bloqueador": None,
                "frecuencia_exfoliacion": None,
                "sensibilidad": None,
                "edad": None,
                "genero": None,
                "preocupaciones": []
            }

    except Exception as e:
        print(f"[ERROR] Fallo al leer memoria de {user_id}: {e}")
        return {
            "tipo_piel": "desconocido",
            "lava_cara": None,
            "usa_bloqueador": None,
            "frecuencia_exfoliacion": None,
            "sensibilidad": None,
            "edad": None,
            "genero": None,
            "preocupaciones": []
        }


def update_user_memory(user_id: str, new_data: Dict[str, Any]) -> None:
    """
    Actualiza o crea el perfil del usuario (UPSERT inteligente).

    ¿Por qué es mejor que tu versión?
    → Usa UPSERT → una sola consulta (más rápido y sin errores de carrera)
    → Nunca falla aunque el usuario no exista antes
    → Limpia los datos antes de guardar
    """
    try:
        # Limpiar datos (evitar nulos raros o strings vacíos)
        clean_data = {}
        for key, value in new_data.items():
            if value is not None and value != "":
                clean_data[key] = value

        # Añadir user_id y timestamp
        clean_data["user_id"] = user_id
        clean_data["updated_at"] = "now()"  # Supabase lo convierte automáticamente

        # UPSERT = insert si no existe, update si existe
        supabase.table("user_profile").upsert(
            clean_data,
            on_conflict="user_id"  # ← clave primaria o única en la tabla
        ).execute()

    except Exception as e:
        print(f"[ERROR] No se pudo actualizar memoria de {user_id}: {e}")
        # No rompemos el flujo aunque falle
        pass


# ------------------------------------------------------------------
# FUNCIÓN EXTRA (te la regalo, es oro)
# ------------------------------------------------------------------
def merge_user_memory(user_id: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza solo algunos campos sin borrar los demás.
    Ejemplo: solo actualizas "lava_cara" pero mantienes el tipo de piel.
    """
    current = get_user_memory(user_id)
    current.update(partial_data)
    update_user_memory(user_id, current)
    return current