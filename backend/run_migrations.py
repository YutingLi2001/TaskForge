import logging
import time
from pathlib import Path

from alembic import command
from alembic.config import Config

try:
    from app.config import DATABASE_URL
except ModuleNotFoundError:
    from backend.app.config import DATABASE_URL

logger = logging.getLogger("taskforge.migrations")


def run_migrations(max_attempts: int = 10, delay_seconds: float = 1.0) -> None:
    alembic_ini = Path(__file__).with_name("alembic.ini")
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            logger.info("Running Alembic migrations.")
            command.upgrade(config, "head")
            logger.info("Alembic migrations completed.")
            return
        except Exception as exc:
            last_error = exc
            logger.warning("Migration attempt failed; retrying.")
            time.sleep(delay_seconds)

    if last_error:
        raise last_error


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
