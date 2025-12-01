from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# --- Permite importar los modelos desde el proyecto principal ---
# Si tu estructura es distinta, ajusta el path:
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # <-- Aquí está tu declarative_base
from database import Base
import models  # <-- Importa todos los modelos para que Alembic los detecte

# --- Configuración base de Alembic ---
config = context.config

# Lee la configuración del archivo alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData de tus modelos (para autogenerate)
target_metadata = Base.metadata

# --- Si quieres usar variables de entorno (por ejemplo en Docker) ---
db_user = os.getenv("POSTGRES_USER", "papu")
db_pass = os.getenv("POSTGRES_PASSWORD", "CocteauTwins")
db_host = os.getenv("POSTGRES_HOST", "postgres_metadata_db")
db_name = os.getenv("POSTGRES_DB", "postgres_metadata_db")

config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
)

# --- Funciones estándar de Alembic ---
def run_migrations_offline():
    """Ejecuta migraciones en modo 'offline' (sin conexión directa)."""
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
    """Ejecuta migraciones en modo 'online' (con conexión activa)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# --- Selecciona el modo según el contexto ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
