import pandas as pd
import sqlite3

# Ruta del archivo CSV generado
file_path = "products.csv"  # Asegúrate de que esté en la misma carpeta del proyecto o ajusta la ruta

# Cargar CSV
df = pd.read_csv(file_path)

# Seleccionar columnas necesarias (en este caso ya están limpias y son las únicas)
columnas_deseadas = ["id", "name", "skin", "ingredients", "price"]
df_filtrado = df[columnas_deseadas]

# Guardar en base de datos SQLite
conn = sqlite3.connect("productos_piel.db")
df_filtrado.to_sql("productos", conn, if_exists="replace", index=False)
conn.close()

print("✅ Base de datos 'productos_piel.db' creada con éxito con los campos seleccionados.")



