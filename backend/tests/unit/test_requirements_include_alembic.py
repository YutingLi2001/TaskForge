from pathlib import Path


def test_requirements_include_alembic() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    requirements_path = repo_root / "backend" / "requirements.txt"
    requirements = requirements_path.read_text(encoding="utf-8").splitlines()

    assert any(
        line.strip().startswith("alembic") for line in requirements if line.strip()
    ), "Expected 'alembic' in backend/requirements.txt"
