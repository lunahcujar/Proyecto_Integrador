import asyncio
from app_.core.dbconnection import engine, Base  # Asegúrate que 'Base' sea tu Base declarativa
from app_.api.models import User, Producto, Habito  # importa todos tus modelos

async def init_models():
    async with engine.begin() as conn:
        # Borra y recrea las tablas (solo en desarrollo)
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas en Supabase correctamente")

if __name__ == "__main__":
    asyncio.run(init_models())

