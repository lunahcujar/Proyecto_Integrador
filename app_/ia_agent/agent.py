from openai import OpenAI
import os

from app_.ia_agent.memory import get_user_memory, update_user_memory
from app_.ia_agent.chat import save_message, get_chat_history
from app_.ia_agent.routines import generate_routine
from supabase import create_client

# 👉 Aquí toma tu API key del entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 👉 Estas también se leen desde .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def dermatology_agent(user_id: str, question: str):
    """Agente principal que responde preguntas usando memoria + historial + análisis."""

    profile = get_user_memory(user_id)
    history = get_chat_history(user_id)

    skin_data = (
        supabase.table("skin_analysis")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
        .data
    )

    skin_report = skin_data[0]["analysis"] if skin_data else "No hay análisis visual reciente."

    products = supabase.table("products").select("*").execute().data

    context = f"""
Actúa como dermatólogo experto.

PERFIL DEL USUARIO:
{profile}

ANÁLISIS RECIENTE DE SU PIEL:
{skin_report}

HISTORIAL DE CONVERSACIÓN:
{[(h["message"], h["response"]) for h in history]}

PRODUCTOS DISPONIBLES:
{products}

RESPONDE A LA PREGUNTA DEL USUARIO:
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": question}
        ]
    )

    answer = response.choices[0].message["content"]

    save_message(user_id, question, answer)

    return answer
