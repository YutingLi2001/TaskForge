from pathlib import Path


def test_docker_compose_runs_migrations() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    compose_path = repo_root / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")

    assert "python run_migrations.py" in content, (
        "Expected migration runner in docker-compose.yml"
    )


def test_docker_compose_prod_runs_migrations() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    compose_path = repo_root / "docker-compose.prod.yml"
    content = compose_path.read_text(encoding="utf-8")

    assert "python run_migrations.py" in content, (
        "Expected migration runner in docker-compose.prod.yml"
    )
