import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ─────────────────────────────────────────────
#   HACER QUE ALEMBIC VEA TU PROYECTO
# ─────────────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar Base y modelos
from app_.core.dbconnection import Base
from app_.api.models import *  # Asegura que Alembic vea todos los modelos

# ─────────────────────────────────────────────
#   CONFIG
# ─────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# URL correcta de Supabase en modo síncrono
DATABASE_URL_SYNC = (
    "postgresql+psycopg2://postgres:Mi1familia234"
    "@db.lajsdmootdbzlnlyfeum.supabase.co:5432/postgres?sslmode=require"
)

# ─────────────────────────────────────────────
#   OFFLINE
# ─────────────────────────────────────────────
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL_SYNC,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ─────────────────────────────────────────────
#   ONLINE
# ─────────────────────────────────────────────
def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL_SYNC},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# ─────────────────────────────────────────────
#   EJECUCIÓN
# ─────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
