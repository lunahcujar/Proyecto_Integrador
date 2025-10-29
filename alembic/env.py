from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app_.core.dbconnection import Base  # 👈 importa tu Base real

config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Asignar metadata de los modelos
target_metadata = Base.metadata

# 🔧 Aquí defines tu URL directamente
DATABASE_URL_SYNC = "postgresql+psycopg2://postgres:Mi1familia234@db.lajsdmootdbzlnlyfeum.supabase.co:5432/postgres"


def run_migrations_offline():
    """Ejecutar migraciones en modo offline."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecutar migraciones en modo online."""
    connectable = engine_from_config(
        {
            "sqlalchemy.url": DATABASE_URL_SYNC
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
