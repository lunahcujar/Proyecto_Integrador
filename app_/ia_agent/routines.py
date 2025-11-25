# app_/ia_agent/routines.py
# =====================================================
# RUTINAS CON GROQ (GRATIS, RÁPIDO Y PERFECTO)
# =====================================================

from groq import AsyncGroq
import os
from app_.ia_agent.memory import get_user_memory
from supabase import create_client

# Cliente de Groq (GRATIS e ILIMITADO)
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


async def generate_routine(user_id: str) -> str:
    """Genera una rutina 100% personalizada con Llama 3.1 70B vía Groq (GRATIS)"""
    try:
        # 1. Perfil del usuario
        profile = get_user_memory(user_id) or {}

        # 2. Último análisis de piel
        skin_data = (
            supabase.table("skin_analysis")
            .select("analysis")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        skin_analysis = skin_data[0]["analysis"] if skin_data else "No hay análisis reciente."

        # 3. Productos disponibles
        products_raw = supabase.table("products").select("name", "category", "beneficios").execute().data
        products_text = "\n".join([
            f"- {p['name']} ({p.get('category', 'general')}): {p.get('beneficios', 'Sin descripción')}"
            for p in products_raw
        ]) if products_raw else "No hay productos disponibles."

        # Prompt optimizado para Llama 3.1 (funciona perfecto)
        system_prompt = f"""Eres un dermatólogo experto y muy amable de la app "AyudaMe Dermatología".

Datos del paciente:
- Tipo de piel: {profile.get('tipo_piel', 'desconocido')}
- Edad: {profile.get('edad', 'no especificada')}
- Preocupaciones: {', '.join(profile.get('preocupaciones', [])) or 'ninguna'}
- Lava la cara: {'Sí' if profile.get('lava_cara') else 'No'}
- Usa bloqueador: {'Sí' if profile.get('usa_bloqueador') else 'No'}
- Exfolia: {profile.get('frecuencia_exfoliacion', 'nunca')}

Último análisis de piel:
{skin_analysis}

Productos disponibles (usa SOLO estos):
{products_text}

Genera una rutina REALISTA y PERSONALIZADA con este formato exacto:

RUTINA DE MAÑANA
1. Limpieza → Nombre del producto → Por qué
2. Hidratante → Nombre del producto → Por qué
3. Protector solar → Nombre del producto → Por qué

RUTINA DE NOCHE
1. Limpieza → Nombre del producto → Por qué
2. Tratamiento → Nombre del producto → Por qué
3. Hidratante → Nombre del producto → Por qué

Sé breve, claro y profesional. Responde SOLO la rutina, sin saludos ni introducciones."""

        # Llamada a Groq (GRATIS y ultrarrápido)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ← CAMBIA ESTO,  # El mejor modelo gratis del mundo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Por favor, genera mi rutina personalizada de cuidado de la piel."}
            ],
            temperature=0.7,
            max_tokens=900
        )

        routine = response.choices[0].message.content.strip()
        return routine

    except Exception as e:
        print(f"[ERROR] Fallo al generar rutina para {user_id}: {e}")
        return (
            "Lo siento, no pude generar tu rutina en este momento.\n\n"
            "Rutina básica recomendada mientras tanto:\n\n"
            "Mañana:\n"
            "• Limpieza suave\n"
            "• Hidratante ligero\n"
            "• Protector solar FPS 50+\n\n"
            "Noche:\n"
            "• Doble limpieza\n"
            "• Sérum o tratamiento\n"
            "• Crema hidratante nutritiva"
        )