from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
from models import Habit, Base
from user_operations import session


# Crear un hábito
def new_habit(name: str, frequency: str, user_id: int) -> Habit:
    new_habit = Habit(name=name, frequency=frequency, user_id=user_id)
    session.add(new_habit)
    session.commit()
    return new_habit

# Leer todos los hábitos
def read_all_habits() -> List[Habit]:
    return session.query(Habit).all()

# Modificar un hábito por ID
def modify_habit_by_id(habit_id: int, updated_data: dict) -> Optional[Habit]:
    habit = session.query(Habit).filter_by(id=habit_id).first()
    if habit:
        for key, value in updated_data.items():
            setattr(habit, key, value)
        session.commit()
        return habit
    return None

# Eliminar un hábito por nombre
def delete_habit_by_name(habit_name: str) -> Optional[Habit]:
    habit = session.query(Habit).filter_by(name=habit_name).first()
    if habit:
        session.delete(habit)
        session.commit()
        return habit
    return None
