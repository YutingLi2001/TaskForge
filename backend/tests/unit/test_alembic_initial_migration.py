from pathlib import Path


def test_initial_migration_includes_core_tables() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    versions_dir = repo_root / "backend" / "alembic" / "versions"

    migrations = sorted(versions_dir.glob("*.py"))
    assert migrations, "Expected at least one migration file in alembic/versions"

    content = migrations[0].read_text(encoding="utf-8")
    expected_tables = ["users", "projects", "tasks"]

    for table in expected_tables:
        assert f"op.create_table('{table}'" in content, (
            f"Expected migration to create '{table}' table"
        )
