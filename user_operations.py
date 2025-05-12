from typing import List, Optional
from models import User, DeletedUser
from dbconnection import get_db_session  # Importa el contexto de la sesión asíncrona
from sqlalchemy.ext.asyncio import AsyncSession


# Crear un nuevo usuario
async def new_user(name: str, mail: str, type_skin: Optional[str] = None, preferences: Optional[bool] = False) -> User:
    async with get_db_session() as session:  # Usamos el contexto asíncrono
        user = User(name=name, mail=mail, type_skin=type_skin, preferences=preferences)
        session.add(user)
        await session.commit()  # Usamos commit asíncrono
        return user

# Modificar un usuario por su nombre
async def modify_user_by_name(name: str, user_data: dict) -> Optional[User]:
    async with get_db_session() as session:  # Usamos el contexto asíncrono
        user = await session.query(User).filter_by(name=name).first()  # Usamos consulta asíncrona
        if user:
            for field in ['name', 'mail', 'type_skin', 'preferences', 'date']:
                if field in user_data:
                    setattr(user, field, user_data[field])
            await session.commit()  # Usamos commit asíncrono
            return user
        return None

# Leer todos los usuarios
async def read_all_users() -> List[User]:
    async with get_db_session() as session:  # Usamos el contexto asíncrono
        users = await session.query(User).all()  # Usamos consulta asíncrona
        return users

# Eliminar un usuario por ID y moverlo a la tabla de eliminados
async def remove_user_by_id(id: int) -> Optional[DeletedUser]:
    async with get_db_session() as session:  # Usamos el contexto asíncrono
        user = await session.query(User).filter_by(id=id).first()  # Usamos consulta asíncrona
        if user:
            deleted_user = DeletedUser(
                name=user.name,
                mail=user.mail,
                type_skin=user.type_skin,
                preferences=user.preferences,
                date=user.date
            )
            await session.delete(user)  # Usamos delete asíncrono
            session.add(deleted_user)
            await session.commit()  # Usamos commit asíncrono
            return deleted_user
        return None
