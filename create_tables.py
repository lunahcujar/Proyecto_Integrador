import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from models import Base  # O el nombre correcto del archivo que contiene tus clases Base, User, etc.

DATABASE_URL = "postgresql+asyncpg://udafrfxeywqopsnngsxy:qOpKiLpt06qQF3VFmbiSllPf7J7ZW6@byjnneiuugcgy4m2iqlh-postgresql.services.clever-cloud.com:50013/byjnneiuugcgy4m2iqlh"

engine = create_async_engine(DATABASE_URL, echo=True)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
