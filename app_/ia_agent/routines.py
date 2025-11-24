from openai import OpenAI
import os
from supabase import create_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_routine(user_profile, skin_analysis, products):
    """Genera una rutina personalizada con IA."""

    context = f"""
Eres un dermatólogo profesional.

DATOS DEL USUARIO:
Tipo de piel: {user_profile.get("skin_type")}
Preocupaciones: {user_profile.get("concerns")}
Hábitos del test: {user_profile.get("test_results")}

ANÁLISIS VISUAL RECIENTE:
{skin_analysis}

PRODUCTOS DISPONIBLES EN LA BASE DE DATOS:
{products}

Crea:
- Rutina de mañana
- Rutina de tarde
- Rutina de noche
Incluye productos compatibles y explica el por qué.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": context}]
    )

    return resp.choices[0].message["content"]
