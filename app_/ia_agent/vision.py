# app_/ia_agent/vision.py
# GEMINI 1.5 FLASH VISION - LIBRERÍA OFICIAL GOOGLE (NOVIEMBRE 2025) - 100% GRATIS

import google.generativeai as genai
import io
from supabase import create_client
import os
from datetime import datetime
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro-exp-0801")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

async def analyze_skin_photo(user_id: str, image_bytes: bytes, filename: str = "photo.jpg") -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes))

        prompt = """
Eres dermatólogo experto. Analiza esta selfie del rostro con máxima precisión:

1. Tipo de piel (seca, grasa, mixta, normal, sensible)
2. Nivel de hidratación (alta, media, baja)
3. Acné o imperfecciones (ninguno, leve, moderado, grave + tipo)
4. Poros (cerrados, visibles, dilatados)
5. Manchas o hiperpigmentación
6. Rojeces o rosácea
7. Textura de la piel
8. Otros detalles importantes

Responde SOLO con lista numerada del 1 al 8 en español.
        """

        response = model.generate_content([prompt, img])
        analysis = response.text.strip()

        supabase.table("skin_analysis").insert({
            "user_id": user_id,
            "analysis": analysis,
            "image_name": filename,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return f"**Análisis de tu piel:**\n{analysis}"

    except Exception as e:
        print(f"[ERROR GEMINI] {e}")
        return "Error temporal. Intenta de nuevo en 10 segundos."