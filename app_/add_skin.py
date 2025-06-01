import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv("skincare_products_with_images_sample.csv")

# Función para asignar tipo de piel
def asignar_tipo_piel(nombre, ingredientes):
    texto = f"{nombre} {ingredientes}".lower()
    if "oil" in texto or "matte" in texto or "acne" in texto:
        return "Grasa"
    elif "hydrating" in texto or "moisture" in texto or "dry" in texto:
        return "Seca"
    elif "sensitive" in texto or "calm" in texto or "soothing" in texto:
        return "Sensible"
    elif "combination" in texto:
        return "Mixta"
    else:
        return "Normal"

# Aplicar la función
df["skin_type"] = df.apply(lambda row: asignar_tipo_piel(row["product_name"], row["clean_ingreds"]), axis=1)

# Guardar el nuevo archivo
df.to_csv("skincare_products_with_skin_type.csv", index=False)
