import asyncio
from sqlalchemy import inspect
from app_.core.dbconnection import engine  # tu AsyncEngine

async def check_tables():
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(tables)
