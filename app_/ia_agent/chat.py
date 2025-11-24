from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_message(user_id: str, message: str, response: str):
    """Guarda cada interacción de chat."""
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "message": message,
        "response": response,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()


def get_chat_history(user_id: str, limit: int = 10):
    """Recupera las últimas interacciones del chat."""
    data = supabase.table("chat_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("timestamp", desc=True) \
        .limit(limit) \
        .execute()
    return data.data
