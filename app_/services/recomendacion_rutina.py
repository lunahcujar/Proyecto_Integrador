from typing import Dict, List
from app_.api.models import Habit, User
from app_.api.products import Product

def construir_rutina(usuario: User, habitos: Habit, productos: List[Product]) -> Dict[str, List[Product]]:
    rutina = {
        "mañana": [],
        "noche": []
    }

    for producto in productos:
        if usuario.type_skin != producto.skin_type:
            continue

        if "limpiador" in producto.name.lower():
            if not habitos.limpieza:
                rutina["mañana"].append(producto)
                rutina["noche"].append(producto)

        if "hidratante" in producto.name.lower():
            rutina["mañana"].append(producto)
            rutina["noche"].append(producto)

        if "protector solar" in producto.name.lower() and not habitos.usa_protector:
            rutina["mañana"].append(producto)

        if "serum" in producto.name.lower():
            rutina["noche"].append(producto)

    return rutina
