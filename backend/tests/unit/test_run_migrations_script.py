from pathlib import Path


def test_run_migrations_script_exists() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "backend" / "run_migrations.py"

    assert script_path.exists(), "Expected backend/run_migrations.py to exist"

    content = script_path.read_text(encoding="utf-8")
    assert "alembic" in content, "Expected Alembic usage in run_migrations.py"
    assert "upgrade" in content, "Expected upgrade command in run_migrations.py"
