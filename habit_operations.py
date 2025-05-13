# habit_operations.py

from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import NoResultFound
from models import Habit
from dbconnection import get_db


# Crear un hábito
async def new_habit(name: str, frequency: str, user_id: int) -> Habit:
    async with get_db_session() as session:
        new_habit = Habit(name=name, frequency=frequency, user_id=user_id)
        session.add(new_habit)
        await session.commit()
        await session.refresh(new_habit)
        return new_habit


# Leer todos los hábitos
async def read_all_habits() -> List[Habit]:
    async with get_db_session() as session:
        result = await session.execute(select(Habit))
        return result.scalars().all()


# Modificar un hábito por ID
async def modify_habit_by_id(habit_id: int, updated_data: dict) -> Optional[Habit]:
    async with get_db_session() as session:
        result = await session.execute(select(Habit).where(Habit.id == habit_id))
        habit = result.scalar_one_or_none()
        if habit:
            for key, value in updated_data.items():
                setattr(habit, key, value)
            await session.commit()
            await session.refresh(habit)
            return habit
        return None


# Eliminar un hábito por nombre
async def delete_habit_by_name(habit_name: str) -> Optional[Habit]:
    async with get_db_session() as session:
        result = await session.execute(select(Habit).where(Habit.name == habit_name))
        habit = result.scalar_one_or_none()
        if habit:
            await session.delete(habit)
            await session.commit()
            return habit
        return None
