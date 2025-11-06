import os
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------
# Ensure Python can find the "source" package no matter where Alembic runs
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root (Ai-Clinical-Trial-MatchMaker)
sys.path.insert(0, str(BASE_DIR))  # Add project root to sys.path

# ---------------------------------------------------------------------
# Import DB config and models
# ---------------------------------------------------------------------
from source.database.config import DatabaseConfig
from source.database.models import BaseDbModel
from source.modules.user.models import User

# ---------------------------------------------------------------------
# Alembic configuration setup
# ---------------------------------------------------------------------
config = context.config

# Load DB URL dynamically from .env or fallback to default from DatabaseConfig
db_config = DatabaseConfig()
database_url = db_config.database_url

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# ---------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------
# Target metadata for autogenerate support
# ---------------------------------------------------------------------
target_metadata = BaseDbModel.metadata


# ---------------------------------------------------------------------
# Offline mode migrations
# ---------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url", database_url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------
# Online mode migrations
# ---------------------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
