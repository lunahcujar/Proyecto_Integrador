import os
import ssl
from typing import AsyncGenerator
from dotenv import load_dotenv
from supabase import create_client
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargar variables desde .env
load_dotenv()
print("🔍 SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("🔍 SUPABASE_KEY:", os.getenv("SUPABASE_KEY")[:10], "...")


# Variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Conexión a la base de datos (Supabase Postgres)
DATABASE_URL = (
    "postgresql+asyncpg://"
    "postgres.lajsdmootdbzlnlyfeum:Mi1familia234"
    "@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
)


# Configurar SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Crear motor de conexión asincrónica
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)

# Base declarativa
Base = declarative_base()

# Sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency para FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
