import csv
from typing import List, Optional
from models import habit

HABITS_FILENAME = "habits.csv"
habit_fields = ["id", "name", "frequency", "user_id"]


def new_habit(habit: habit) -> habit:
    habits = read_all_habits()
    habit_with_id = habit
    write_habit_into_csv(habit_with_id)
    return habit_with_id


def write_habit_into_csv(habit: habit):
    with open(HABITS_FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=habit_fields)
        writer.writerow(habit.model_dump())


def modify_habit_by_name(name: str, habit_data: dict) -> Optional[habit]:
    habits = read_all_habits()
    updated_habit = None

    for idx, h in enumerate(habits):
        if h.name.lower() == name.lower():
            if habit_data.get("name") is not None:
                habits[idx].name = habit_data["name"]
            if habit_data.get("frequency") is not None:
                habits[idx].frequency = habit_data["frequency"]
            if habit_data.get("user_id") is not None:
                habits[idx].user_id = habit_data["user_id"]

            updated_habit = habits[idx]
            break

    if updated_habit:
        with open(HABITS_FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=habit_fields)
            writer.writeheader()
            for h in habits:
                writer.writerow(h.model_dump())

        return updated_habit

    return None


def read_all_habits() -> List[habit]:
    habits = []
    try:
        with open(HABITS_FILENAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                habits.append(habit(
                    id=int(row["id"]),
                    name=row["name"],
                    frequency=row["frequency"],
                    user_id=int(row["user_id"])
                ))
    except FileNotFoundError:
        pass
    return habits
