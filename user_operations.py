from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional
from models import *

# Configuración de la base de datos (ajusta los parámetros de conexión según sea necesario)
DATABASE_URL = "postgresql://udafrfxeywqopsnngsxy:qOpKiLpt06qQF3VFmbiSllPf7J7ZW6@byjnneiuugcgy4m2iqlh-postgresql.services.clever-cloud.com:50013/byjnneiuugcgy4m2iqlh"

Base = declarative_base()


# Definir el modelo para usuarios eliminados
class DeletedUser(Base):
    __tablename__ = 'users_deleted'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    type_skin = Column(String, nullable=True)
    preferences = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)


# Crear la sesión de la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Crear las tablas en la base de datos (si no existen)
Base.metadata.create_all(engine)


def new_user(name: str, mail: str, type_skin: Optional[str] = None, preferences: Optional[bool] = False) -> User:
    new_user = User(name=name, mail=mail, type_skin=type_skin, preferences=preferences)
    session.add(new_user)
    session.commit()
    return new_user


def get_next_ID() -> int:
    # La base de datos maneja automáticamente el ID de los usuarios, por lo que no es necesario calcularlo manualmente
    return session.query(User).count() + 1


def modify_user_by_name(name: str, user_data: dict) -> Optional[User]:
    user = session.query(User).filter_by(name=name).first()
    if user:
        if 'name' in user_data:
            user.name = user_data['name']
        if 'mail' in user_data:
            user.mail = user_data['mail']
        if 'type_skin' in user_data:
            user.type_skin = user_data['type_skin']
        if 'preferences' in user_data:
            user.preferences = user_data['preferences']
        if 'date' in user_data:
            user.date = datetime.fromisoformat(user_data['date'])

        session.commit()
        return user
    return None


def read_all_users() -> List[User]:
    return session.query(User).all()


def remove_user_by_id(id: int) -> Optional[User]:
    user = session.query(User).filter_by(id=id).first()
    if user:
        # Movemos el usuario a la tabla de eliminados
        deleted_user = DeletedUser(
            name=user.name,
            mail=user.mail,
            type_skin=user.type_skin,
            preferences=user.preferences,
            date=user.date
        )
        session.delete(user)
        session.add(deleted_user)
        session.commit()
        return deleted_user
    return None

