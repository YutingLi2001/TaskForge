from pathlib import Path


def test_alembic_ini_uses_env_url_and_timezone() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    ini_path = repo_root / "backend" / "alembic.ini"
    content = ini_path.read_text(encoding="utf-8")

    for line in content.splitlines():
        if line.strip().startswith("sqlalchemy.url"):
            _, value = line.split("=", 1)
            assert value.strip() == "", "sqlalchemy.url should be empty in alembic.ini"
            break
    else:
        raise AssertionError("sqlalchemy.url line not found in alembic.ini")

    assert "timezone = UTC" in content, "Expected timezone = UTC in alembic.ini"


def test_alembic_env_configured_for_models() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    env_path = repo_root / "backend" / "alembic" / "env.py"
    content = env_path.read_text(encoding="utf-8")

    expected_snippets = [
        "config.set_main_option(\"sqlalchemy.url\"",
        "target_metadata = Base.metadata",
        "compare_type=True",
        "render_as_batch=",
    ]

    for snippet in expected_snippets:
        assert snippet in content, f"Expected '{snippet}' in alembic/env.py"
