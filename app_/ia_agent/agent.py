# app_/ia_agent/agent.py
from groq import AsyncGroq  # ← GRATIS y ULTRARRÁPIDO
import os
from app_.ia_agent.memory import get_user_memory
from app_.ia_agent.chat import save_message, get_chat_history_as_openai_messages
from supabase import create_client

# Cliente ASÍNCRONO de GROQ (¡GRATIS!)
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


async def dermatology_agent(user_id: str, question: str) -> str:
    """
    Agente dermatológico con GROQ + Llama 3.1 70B - GRATIS, RÁPIDO Y PERFECTO
    """
    try:
        # 1. Perfil del usuario
        profile = get_user_memory(user_id) or {}
        profile_str = "\n".join([f"{k}: {v}" for k, v in profile.items() if v])

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
        skin_report = skin_data[0]["analysis"] if skin_data else "No hay análisis de piel reciente."

        # 3. Productos disponibles
        products_raw = supabase.table("products").select("name", "category", "beneficios").execute().data
        products_text = "\n".join([
            f"- {p['name']} ({p.get('category', 'otro')}): {p.get('beneficios', 'Sin descripción')}"
            for p in products_raw[:15]
        ]) if products_raw else "No hay productos disponibles."

        # 4. Historial del chat
        history_messages = get_chat_history_as_openai_messages(user_id, limit_pairs=6)

        # 5. System prompt optimizado para Llama
        system_prompt = f"""Eres un dermatólogo experto y muy amable de la app "AyudaMe Dermatología".

Datos del paciente:
{profile_str}

Último análisis de piel:
{skin_report}

Productos disponibles en la tienda:
{products_text}

Normas:
- Responde siempre en español, cercano y profesional
- Solo recomienda productos de la lista
- Si no sabes algo, recomienda visita presencial al dermatólogo
- Sé breve pero útil
"""

        # 6. Mensajes
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(history_messages)
        messages.append({"role": "user", "content": question})

        # 7. Llamada a GROQ (¡ASÍNCRONA Y GRATIS!)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ← CAMBIA ESTO,  # ← GRATIS, rápido y experto en medicina
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )

        answer = response.choices[0].message.content.strip()

        # 8. Guardar historial
        save_message(user_id, question, answer)

        return answer

    except Exception as e:
        print(f"[ERROR CRÍTICO] dermatology_agent → {e}")
        return "Lo siento, ocurrió un error técnico. Por favor intenta de nuevo en unos segundos."