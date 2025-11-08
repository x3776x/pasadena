from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Permitir importar modelos desde app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base  # Asegúrate que en models/__init__.py esté declarado Base

# Configuración principal de Alembic
config = context.config
fileConfig(config.config_file_name)

# Conectar con los metadatos del modelo SQLAlchemy
target_metadata = Base.metadata


def run_migrations_offline():
    """Ejecuta migraciones en modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecuta migraciones en modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
