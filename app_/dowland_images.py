import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Cargar el archivo
df = pd.read_csv("app_/skincare_products_clean.csv")

# Trabajar solo con los primeros 10 productos para prueba
df_sample = df.head(1139)

# Lista para guardar las URLs de las imágenes
image_urls = []

# Cabecera para simular navegador real
headers = {"User-Agent": "Mozilla/5.0"}

total = len(df_sample)
start_time = time.time()

for i, url in enumerate(df_sample['product_url']):
    print(f"[{i+1}/{total}] Procesando: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        img = soup.find("img")
        if img and img.get("src"):
            image_urls.append(img["src"])
        else:
            image_urls.append("No encontrada")
    except Exception as e:
        image_urls.append("Error")
        print(f"  ⚠️ Error al procesar {url}: {e}")

    time.sleep(1)

    elapsed = time.time() - start_time
    avg_time = elapsed / (i + 1)
    remaining = avg_time * (total - i - 1)
    print(f"  ⏱ Estimado restante: {int(remaining)} segundos")

# Agregar la columna al DataFrame de prueba
df_sample["image_url"] = image_urls

# Guardar nuevo archivo con las imágenes
df_sample.to_csv("skincare_products_with_images_sample.csv", index=False)
print("✅ Archivo de prueba guardado con las URLs de las imágenes.")
