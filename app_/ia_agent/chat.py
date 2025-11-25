# app_/ia_agent/chat.py
from supabase import create_client
import os
from datetime import datetime
from typing import List, Dict, Any

# ------------------------------------------------------------------
# CONFIGURACIÓN SUPABASE (una sola vez al iniciar la app)
# ------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Faltan SUPABASE_URL o SUPABASE_KEY en las variables de entorno")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_message(user_id: str, message: str, response: str) -> None:
    """
    Guarda el mensaje del usuario y la respuesta del agente.

    ¿Por qué estos cambios son importantes?
    → try/except: si Supabase falla un segundo, la app NO se cae
    → .strip(): evita guardar mensajes con puros espacios o saltos de línea
    → timestamp en UTC: evita problemas de zona horaria
    """
    try:
        supabase.table("chat_history").insert({
            "user_id": user_id,
            "message": message.strip(),
            "response": response.strip(),
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        # Nunca rompemos el flujo del chat aunque falle la base de datos
        print(f"[ERROR] No se pudo guardar mensaje en chat_history → {e}")


def get_chat_history(user_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Devuelve el historial del usuario (orden cronológico: del más antiguo al más nuevo)

    ¿Por qué estos cambios son importantes?
    → Siempre devuelve una lista (nunca None) → evita errores "undefined"
    → Orden invertido al final → OpenAI prefiere el contexto en orden natural
    → limit por defecto 15 → suficiente memoria sin saturar tokens
    → Manejo de errores → si Supabase está caído, el agente sigue funcionando
    """
    try:
        response = (
            supabase.table("chat_history")
            .select("message", "response", "timestamp")  # solo lo necesario
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

        history = response.data or []  # ← nunca devuelve None
        return list(reversed(history))  # ← orden correcto para GPT

    except Exception as e:
        print(f"[ERROR] Fallo al obtener historial de chat → {e}")
        return []  # ← fallback seguro


# ------------------------------------------------------------------
# FUNCIÓN EXTRA (la uso siempre y te la regalo)
# ------------------------------------------------------------------
def get_chat_history_as_openai_messages(user_id: str, limit_pairs: int = 8) -> List[Dict[str, str]]:
    """
    Devuelve el historial listo para meter directamente en messages=[] de OpenAI

    Ejemplo de salida:
    [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Hola! ¿Cómo estás?"},
        ...
    ]

    ¿Por qué es importante?
    → Evitas tener que convertir el historial en cada llamada al agente
    → Mucho más limpio y rápido
    → Controlas exactamente cuántos pares user/assistant envías
    """
    raw_history = get_chat_history(user_id, limit_pairs * 2)
    messages = []

    # Tomamos solo los últimos N pares (user + assistant)
    for entry in raw_history[-limit_pairs * 2:]:
        messages.append({"role": "user", "content": entry["message"]})
        messages.append({"role": "assistant", "content": entry["response"]})

    return messages