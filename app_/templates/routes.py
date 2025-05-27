# routes.py o home.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

templates = Jinja2Templates(directory="templates")
router = APIRouter()

csv_files = {
    "Usuario": "data/usuarios.csv",
    "Producto": "data/productos.csv",
    "Habito": "data/habitos.csv"
}

campos_modelos = {
    "Usuario": ["name", "mail", "type_skin", "preferences"],
    "Producto": ["name", "description", "type_skin"],
    "Habito": ["name", "frequency", "user_id"]
}


@router.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/{modelo}s", response_class=HTMLResponse)
async def listar(request: Request, modelo: str):
    modelo = modelo.capitalize()
    if modelo not in csv_files:
        return HTMLResponse("Modelo no encontrado", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    df["id"] = df.index
    lista = df.to_dict(orient="records")

    return templates.TemplateResponse("list.html", {
        "request": request,
        "nombre_modelo": modelo,
        "items": lista
    })


@router.get("/{modelo}/add", response_class=HTMLResponse)
async def mostrar_formulario(request: Request, modelo: str):
    modelo = modelo.capitalize()
    if modelo not in campos_modelos:
        return HTMLResponse("Modelo no válido", status_code=404)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "nombre_modelo": modelo,
        "campos": campos_modelos[modelo],
        "valores": {},
        "ruta_accion": f"/{modelo}/add"
    })


@router.post("/{modelo}/add")
async def agregar_item(
        request: Request,
        modelo: str,
        **datos: str
):
    modelo = modelo.capitalize()
    if modelo not in campos_modelos:
        return HTMLResponse("Modelo no válido", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    nuevo_registro = [datos[campo] for campo in campos_modelos[modelo]]
    df.loc[len(df)] = nuevo_registro
    df.to_csv(csv_files[modelo], index=False)

    return RedirectResponse(url=f"/{modelo}s", status_code=303)


@router.get("/{modelo}/detail/{id}", response_class=HTMLResponse)
async def ver_detalle(request: Request, modelo: str, id: int):
    modelo = modelo.capitalize()
    if modelo not in csv_files:
        return HTMLResponse("Modelo no encontrado", status_code=404)

    df = pd.read_csv(csv_files[modelo])
    if id < 0 or id >= len(df):
        return HTMLResponse("Ítem no encontrado", status_code=404)

    fila = df.iloc[id].to_dict()

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "nombre_modelo": modelo,
        "item": fila
    })
