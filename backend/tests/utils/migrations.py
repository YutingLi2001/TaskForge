import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url

from backend.app import config as app_config

TEST_DB_DIR = Path(__file__).resolve().parents[1] / ".test_dbs"


def build_test_db_url(name: str, *, async_driver: bool) -> str:
    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
    db_path = (TEST_DB_DIR / f"{name}.db").resolve()
    driver = "sqlite+aiosqlite" if async_driver else "sqlite+pysqlite"
    return f"{driver}:///{db_path.as_posix()}"


def reset_database(database_url: str) -> None:
    os.environ["DATABASE_URL"] = database_url
    app_config.DATABASE_URL = database_url
    try:
        import app.config as app_config_alt
    except ModuleNotFoundError:
        app_config_alt = None
    if app_config_alt is not None:
        app_config_alt.DATABASE_URL = database_url

    alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", database_url)

    try:
        command.downgrade(config, "base")
    except Exception:
        pass
    command.upgrade(config, "head")


def sync_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername == "sqlite+aiosqlite":
        url = url.set(drivername="sqlite")
    return url.render_as_string(hide_password=False)
