import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Needed for correct metadata registration for alembic
from src.apps.registry.infrastructure.db_models.models import *  # noqa: F401,F403
from src.apps.users.infrastructure.db_models.models import *  # noqa: F401,F403
from src.apps.platform_rules.infrastructure.db_models.models import *  # noqa: F401,F403
from src.apps.catalogs.infrastructure.db_models.models import *  # noqa: F401,F403
from src.apps.patients.infrastructure.db_models.association_tables import *  # noqa: F401,F403
from src.apps.patients.infrastructure.db_models.patients import *  # noqa: F401,F403

from src.apps.assets_journal.infrastructure.db_models.models import * # noqa: F401,F403

from src.core.settings import Settings
from src.shared.infrastructure.base import Base

config = context.config
target_metadata = Base.metadata
settings = Settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    url = settings.DATABASE_URI

    connectable: AsyncEngine = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
