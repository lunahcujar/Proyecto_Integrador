# habit_operations.py

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import NoResultFound
from models import Habit
from dbconnection import get_db


async def new_habit(name: str, frequency: str, user_id: int, db: AsyncSession) -> Habit:
    new_habit = Habit(name=name, frequency=frequency, user_id=user_id)
    db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)
    return new_habit



# Leer todos los hábitos
async def read_all_habits(db: AsyncSession) -> list[Habit]:
    result = await db.execute(select(Habit))
    habits = result.scalars().all()
    return habits


# Modificar un hábito por ID
async def modify_habit_by_id(habit_id: int, updated_fields: dict, db: AsyncSession) -> Habit:
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()

    if habit is None:
        raise ValueError("Hábito no encontrado")

    for key, value in updated_fields.items():
        setattr(habit, key, value)

    await db.commit()
    await db.refresh(habit)
    return habit


# Eliminar un hábito por nombre
async def delete_habit_by_name(habit_name: str, db: AsyncSession) -> Optional[Habit]:
    result = await db.execute(select(Habit).where(Habit.name == habit_name))
    habit = result.scalar_one_or_none()

    if habit:
        await db.delete(habit)
        await db.commit()
        return habit

    return None
