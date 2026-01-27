# TaskForge
A full-stack personal task and project tracking application built with FastAPI, React, Docker, and deployed on AWS Lightsail, featuring JWT-based authentication and RESTful APIs.

## Coverage

- CI coverage summaries appear in the GitHub Actions job summary on pull requests.
- Backend coverage artifacts: download `backend-coverage` and open `htmlcov/index.html`.
- Frontend coverage artifacts: download `frontend-coverage` and open `coverage/index.html`.

## Production Docker

### Windows Scripts (Recommended)

```batch
# Start production stack (with health checks and security verification)
scripts\windows\run-localhost-prod.bat

# Start with fresh database
scripts\windows\run-localhost-prod-reset.bat
```

### Manual Commands

Build and run the production stack locally:

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

Check health and logs:

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

Verify container users:

```bash
docker exec taskforge-backend-1 whoami
docker exec taskforge-frontend-1 whoami
```

## Development Docker

### Windows Scripts

```batch
# Start development stack
scripts\windows\run-localhost.bat

# Start with fresh database
scripts\windows\run-localhost-reset.bat
```
