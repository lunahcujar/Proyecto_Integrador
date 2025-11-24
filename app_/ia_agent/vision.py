from openai import OpenAI
import base64
from supabase import create_client
import os
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def analyze_skin_photo(user_id: str, image_bytes: bytes):
    """Analiza una foto de la piel usando GPT-4.1-Vision."""
    encoded = base64.b64encode(image_bytes).decode()

    response = client.chat.completions.create(
        model="gpt-4.1-vision-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analiza esta piel y describe problemas visibles."},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded}"}
                ]
            }
        ]
    )

    analysis = response.choices[0].message["content"]

    supabase.table("skin_analysis").insert({
        "user_id": user_id,
        "analysis": analysis,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return analysis
