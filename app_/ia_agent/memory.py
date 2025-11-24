from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_memory(user_id: str):
    """Obtiene el perfil del usuario desde Supabase."""
    result = supabase.table("user_profile").select("*").eq("user_id", user_id).single().execute()
    return result.data


def update_user_memory(user_id: str, data: dict):
    """Crea o actualiza la memoria del usuario."""
    existing = supabase.table("user_profile").select("*").eq("user_id", user_id).single().execute()

    if existing.data:
        return supabase.table("user_profile").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        return supabase.table("user_profile").insert(data).execute()
