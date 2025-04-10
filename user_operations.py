import csv
from typing import List, Optional
from datetime import datetime
from models import user, userWithId

DATABASE_FILENAME = "users.csv"
DELETED_USERS_FILENAME = "users_deleted.csv"
column_fields = ["id", "name", "mail", "type_skin", "preferences", "date"]


def new_user(user: user) -> userWithId:
    id = get_next_ID()
    user_with_id = userWithId(id=id, **user.model_dump())
    write_user_into_csv(user_with_id)
    return user_with_id



def get_next_ID() -> int:
    try:
        users = read_all_users()
        if not users:
            return 1
        return max(user.id for user in users) + 1
    except FileNotFoundError:
        return 1


def write_user_into_csv(user: userWithId):
    with open(DATABASE_FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=column_fields)
        writer.writerow(user.model_dump())


def modify_user_by_name(name: str, user_data: dict) -> Optional[userWithId]:
    users = read_all_users()
    updated_user = None
    user_found = False

    for idx, u in enumerate(users):
        if u.name.lower() == name.lower():
            if user_data.get("name") is not None:
                users[idx].name = user_data["name"]
            if user_data.get("mail") is not None:
                users[idx].mail = user_data["mail"]
            if user_data.get("type_skin") is not None:
                users[idx].type_skin = user_data["type_skin"]
            if user_data.get("preferences") is not None:
                users[idx].preferences = user_data["preferences"]
            if user_data.get("date") is not None:
                users[idx].date = datetime.fromisoformat(user_data["date"])

            updated_user = users[idx]
            user_found = True
            break

    if user_found:
        with open(DATABASE_FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=column_fields)
            writer.writeheader()
            for u in users:
                writer.writerow(u.model_dump())
        return updated_user

    return None


def read_all_users() -> List[userWithId]:
    users = []
    try:
        with open(DATABASE_FILENAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(userWithId(
                    id=int(row["id"]),
                    name=row["name"],
                    mail=row["mail"],
                    type_skin=row["type_skin"] if row["type_skin"] else None,
                    preferences=row["preferences"].lower() == "true",
                    date=datetime.fromisoformat(row["date"])
                ))
    except FileNotFoundError:
        pass
    return users

def remove_user_by_id(id: int) -> Optional[userWithId]:
    users = read_all_users()
    deleted_user = None

    # Filtrar los usuarios, dejando fuera el que se va a eliminar
    remaining_users = []

    for u in users:
        if u.id == id:
            deleted_user = u
        else:
            remaining_users.append(u)

    # Si el usuario fue encontrado, escribimos en ambos archivos
    if deleted_user:
        # Reescribimos el archivo con los usuarios restantes
        with open("users.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "mail", "type_skin", "preferences", "date"])
            writer.writeheader()
            for u in remaining_users:
                writer.writerow(u.model_dump())

        # Escribimos el usuario eliminado en el archivo de eliminados
        with open("users_deleted.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "mail", "type_skin", "preferences", "date"])
            # Agregamos encabezado solo si el archivo está vacío
            file.seek(0, 2)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(deleted_user.model_dump())

        return deleted_user

    return None
