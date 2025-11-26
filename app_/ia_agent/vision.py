# app_/ia_agent/vision.py
# GEMINI 2.5 / 3.0 VISION - ACTUALIZADO PARA NOVIEMBRE 2025 (Gemini 1.5 deprecado)

import google.generativeai as genai
import io
import os
from datetime import datetime
from PIL import Image
from supabase import create_client

# ===================== CONFIGURACIÓN GEMINI =====================
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # También vale GEMINI_API_KEY

# ELIGE EL MODELO ACTUAL (Gemini 1.5 ya no existe - deprecado abril 2025):
model = genai.GenerativeModel("gemini-2.5-flash")   # ← Rápido, barato y con visión perfecta
# model = genai.GenerativeModel("gemini-2.5-pro")   # ← Máxima precisión (descomenta si quieres)
# model = genai.GenerativeModel("gemini-3-pro-preview")  # ← Lo más nuevo (súper potente)

# ===================== CONFIGURACIÓN SUPABASE (v2.x) =====================
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("⚠️ Faltan SUPABASE_URL y/o SUPABASE_KEY en el archivo .env")

supabase = create_client(supabase_url, supabase_key)


# ===================== FUNCIÓN PRINCIPAL =====================
async def analyze_skin_photo(user_id: str, image_bytes: bytes, filename: str = "photo.jpg") -> str:
    """
    Analiza una selfie del rostro con Gemini Vision y guarda el resultado en Supabase
    """
    try:
        # Convertir bytes → imagen PIL (requerido por Gemini)
        img = Image.open(io.BytesIO(image_bytes))

        prompt = """Eres dermatólogo experto. Analiza esta selfie del rostro con máxima precisión:

1. Tipo de piel (seca, grasa, mixta, normal, sensible)
2. Nivel de hidratación (alta, media, baja)
3. Acné o imperfecciones (ninguno, leve, moderado, grave + tipo)
4. Poros (cerrados, visibles, dilatados)
5. Manchas o hiperpigmentación
6. Rojeces o rosácea
7. Textura de la piel
8. Otros detalles importantes

Responde SOLO con lista numerada del 1 al 8 en español, sin introducción ni conclusión."""

        # Llamada a Gemini (funciona igual con los modelos nuevos)
        response = model.generate_content([prompt, img])

        # Protección contra bloqueos o respuestas vacías
        if not getattr(response, "text", None):
            analysis = "No se pudo analizar la imagen (posible bloqueo de seguridad). Prueba con otra selfie bien iluminada."
        else:
            analysis = response.text.strip()

        # Guardar en Supabase
        supabase.table("skin_analysis").insert({
            "user_id": user_id,
            "analysis": analysis,
            "image_name": filename,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return f"**Análisis de tu piel:**\n{analysis}"

    except Exception as e:
        print(f"[ERROR GEMINI] {type(e).__name__}: {e}")
        return "Error temporal. Intenta de nuevo en 10 segundos."