from typing import List, Optional
from models import User
from dbconnection import get_db  # Importa el contexto de la sesión asíncrona
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Crear un nuevo usuario
async def new_user(name: str, mail: str, type_skin: Optional[str], preferences: Optional[bool], db: AsyncSession) -> User:
    db_user = User(name=name, mail=mail, type_skin=type_skin, preferences=preferences)
    db.add(db_user)
    await db.commit()  # Confirmar la transacción
    await db.refresh(db_user)  # Refrescar los datos del objeto para obtener el ID generado
    return db_user

# Modificar un usuario por su nombre
async def modify_user_by_name(name: str, user_data: dict, db: AsyncSession) -> Optional[User]:
    async with db.begin():  # Usamos el contexto asíncrono
        # Usamos select para consultas asíncronas más eficientes
        result = await db.execute(select(User).filter_by(name=name))
        user = result.scalars().first()  # Escalamos para obtener el primer usuario
        if user:
            # Actualizamos los campos del usuario si están presentes en user_data
            for field in ['name', 'mail', 'type_skin', 'preferences', 'date']:
                if field in user_data:
                    setattr(user, field, user_data[field])
            await db.commit()  # Confirmar la transacción
            return user
        return None

# Leer todos los usuarios
async def read_all_users(db: AsyncSession) -> List[User]:
    async with db.begin():  # Usamos el contexto asíncrono
        # Usamos select para consultas asíncronas
        result = await db.execute(select(User))
        users = result.scalars().all()  # Obtenemos todos los usuarios
        return users

# Eliminar un usuario por ID
async def remove_user_by_id(id: int, db: AsyncSession) -> Optional[User]:
    async with db.begin():  # Usamos el contexto asíncrono con transacción
        # Usamos select para consultas asíncronas
        result = await db.execute(select(User).filter_by(id=id))
        user = result.scalars().first()  # Obtenemos el primer usuario

        if user:
            await db.delete(user)  # Usamos delete asíncrono para eliminar el usuario
            await db.commit()  # Confirmar la transacción
            return user  # Devolvemos el usuario eliminado

        return None  # Si no se encuentra el usuario, retornamos None
