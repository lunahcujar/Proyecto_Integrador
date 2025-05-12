import csv
from typing import List, Optional
from models import Habit

HABITS_FILENAME = "habits.csv"
habit_fields = ["id", "name", "frequency", "user_id"]


def new_habit(habit: Habit) -> Habit:
    habits = read_all_habits()
    habit_with_id = habit
    write_habit_into_csv(habit_with_id)
    return habit_with_id


def write_habit_into_csv(habit: Habit):
    with open(HABITS_FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=habit_fields)
        writer.writerow(habit.dict())


def modify_habit_by_id(id: int, habit_data: dict) -> Optional[Habit]:
    habits = read_all_habits()
    updated_habit = None

    for idx, h in enumerate(habits):
        if h.id == id:
            # Crear una nueva instancia del hábito con los datos actualizados
            updated_habit = Habit(
                id=h.id,
                name=habit_data.get("name", h.name),
                frequency=habit_data.get("frequency", h.frequency),
                user_id=habit_data.get("user_id", h.user_id),
            )
            habits[idx] = updated_habit
            break

    if updated_habit:
        with open(HABITS_FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=habit_fields)
            writer.writeheader()
            for h in habits:
                writer.writerow(h.model_dump())  # Usa model_dump() con Pydantic v2

        return updated_habit

    return None



def read_all_habits() -> List[Habit]:
    habits = []
    try:
        with open(HABITS_FILENAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)  # Para debug
                habits.append(Habit(
                    id=int(row["id"]),
                    name=row["name"],
                    frequency=row["frequency"],
                    user_id=int(row["user_id"])
                ))
    except FileNotFoundError:
        pass  # O puedes poner return [] aquí también si prefieres

    return habits


def delete_habit_by_name(name: str) -> bool:
    habits = read_all_habits()
    updated_habits = [h for h in habits if h.name.lower() != name.lower()]

    if len(updated_habits) == len(habits):
        return False  # No se encontró el hábito

    with open(HABITS_FILENAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=habit_fields)
        writer.writeheader()
        for h in updated_habits:
            writer.writerow(h.model_dump())

    return True
