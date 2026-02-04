# TaskForge

A full-stack personal task and project tracking application built with FastAPI, React, Docker, and deployed on AWS Lightsail, featuring JWT-based authentication and RESTful APIs.

## Quick Start

```batch
# Start development environment
scripts\windows\docker-dev.bat

# Run all tests
scripts\windows\test-all.bat

# Run linting
scripts\windows\lint.bat
```

## Windows Scripts

All scripts are in `scripts\windows\`. Double-click `.bat` files or run from terminal.

### Docker Scripts

| Script | Description |
|--------|-------------|
| `docker-dev.bat` | Start development stack (hot reload) |
| `docker-dev-reset.bat` | Start dev stack with fresh database |
| `docker-prod.bat` | Start production stack (nginx, health checks) |
| `docker-prod-reset.bat` | Start prod stack with fresh database |

**Development** (port 5173): Uses Vite dev server with hot reload
**Production** (port 80): Uses nginx with optimized images

### Testing Scripts

| Script | Description |
|--------|-------------|
| `test-backend.bat` | Run backend tests with pytest + coverage |
| `test-frontend.bat` | Run frontend tests with vitest + coverage |
| `test-all.bat` | Run all tests (backend + frontend) |

### Quality Scripts

| Script | Description |
|--------|-------------|
| `lint.bat` | Run ruff (backend) + eslint (frontend) |
| `typecheck.bat` | Run TypeScript type checking |

### Maintenance Scripts

| Script | Description |
|--------|-------------|
| `logs-clean.bat` | Delete all log files |
| `logs-rotate.bat` | Keep only the 10 most recent logs |

## Coverage

- CI coverage summaries appear in the GitHub Actions job summary on pull requests.
- Backend coverage artifacts: download `backend-coverage` and open `htmlcov/index.html`.
- Frontend coverage artifacts: download `frontend-coverage` and open `coverage/index.html`.

## Manual Commands

### Development

```bash
# Start development stack
docker compose up --build -d

# View logs
docker compose logs -f
```

### Production

```bash
# Build and start production stack
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Check container health
docker compose -f docker-compose.prod.yml ps

# Verify non-root users
docker exec taskforge-backend-1 whoami   # Should be: appuser
docker exec taskforge-frontend-1 whoami  # Should be: nginx
```

### Migrations

```bash
# Generate a migration after model changes
cd backend
alembic revision --autogenerate -m "Describe change"

# Apply migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Run migrations programmatically (used in Docker entrypoints)
python run_migrations.py
```

### Testing

```bash
# Backend tests (from project root)
PYTHONPATH=. pytest backend/tests/ -v

# Frontend tests
cd frontend && npm test
```

### Linting

```bash
# Backend
ruff check backend/

# Frontend
cd frontend && npm run lint
```
