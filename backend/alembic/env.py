from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

try:
    import app.models  # noqa: F401  - Needed to register models with SQLAlchemy metadata
    from app.config import DATABASE_URL
    from app.database import Base
except ModuleNotFoundError:  # Allow running Alembic from repo root in tests.
    import backend.app.models  # noqa: F401  - Needed to register models
    from backend.app.config import DATABASE_URL
    from backend.app.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_sync_database_url() -> str:
    url = make_url(DATABASE_URL)

    if url.drivername == "postgresql+asyncpg":
        url = url.set(drivername="postgresql+psycopg2")
    elif url.drivername == "sqlite+aiosqlite":
        # Convert async SQLite driver to sync
        url = url.set(drivername="sqlite")
        # Special handling for in-memory databases: use shared cache
        # so migrations and app/tests see the same in-memory database
        if url.database == ":memory:" or ":memory:" in str(url):
            # Use shared cache URI for in-memory SQLite
            return "sqlite:///:memory:?cache=shared&uri=true"
    elif url.drivername == "mysql+aiomysql":
        url = url.set(drivername="mysql+pymysql")

    return url.render_as_string(hide_password=False)


sync_database_url = _get_sync_database_url()
config.set_main_option("sqlalchemy.url", sync_database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

is_sqlite = make_url(sync_database_url).drivername.startswith("sqlite")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=is_sqlite,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use StaticPool for in-memory SQLite to preserve the database across connections
    poolclass = pool.StaticPool if ":memory:" in sync_database_url else pool.NullPool

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=poolclass,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=is_sqlite,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
