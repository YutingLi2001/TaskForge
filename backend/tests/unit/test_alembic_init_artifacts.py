from pathlib import Path


def test_alembic_init_artifacts_exist() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    backend_root = repo_root / "backend"

    expected_paths = [
        backend_root / "alembic.ini",
        backend_root / "alembic" / "env.py",
        backend_root / "alembic" / "script.py.mako",
        backend_root / "alembic" / "README",
        backend_root / "alembic" / "versions",
    ]

    missing = [path for path in expected_paths if not path.exists()]
    assert not missing, f"Missing Alembic init artifacts: {missing}"
