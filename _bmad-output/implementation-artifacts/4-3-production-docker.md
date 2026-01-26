# Story 4.3: Production Docker Configuration

Status: review

## Story

As a **developer**,
I want **optimized Docker images for production**,
So that **deployments are fast and secure**.

## Acceptance Criteria

1. **Given** I build Docker images for production **When** the build completes **Then** images use multi-stage builds for smaller size
2. **Given** production containers are running **When** I inspect the process **Then** containers run as non-root user
3. **Given** production containers are running **When** orchestrator checks health **Then** health check endpoints respond correctly
4. **Given** I build Docker images **When** build context is sent **Then** .dockerignore excludes unnecessary files (node_modules, __pycache__, .git, tests, etc.)
5. **Given** I want to deploy to production **When** I run docker-compose **Then** docker-compose.prod.yml is available with production settings
6. **Given** frontend is built for production **When** container starts **Then** static files are served via nginx (not dev server)
7. **Given** backend is built for production **When** container starts **Then** uvicorn runs without --reload flag

## Tasks / Subtasks

### Phase 1: Backend Production Dockerfile

- [x] **Task 1: Create Multi-Stage Backend Dockerfile** (AC: 1, 2, 7)
  - [x] Create `backend/Dockerfile.prod` with multi-stage build
  - [x] Stage 1: Install dependencies in builder stage
  - [x] Stage 2: Copy only necessary files to slim runtime image
  - [x] Create non-root user (appuser) and set ownership
  - [x] Remove --reload flag from uvicorn command
  - [x] Verify image size reduction compared to current Dockerfile (417MB → 401MB)

- [x] **Task 2: Add Backend Health Check** (AC: 3)
  - [x] Add HEALTHCHECK instruction to Dockerfile.prod
  - [x] Use existing /api/health endpoint
  - [x] Configure appropriate interval, timeout, and retries

- [x] **Task 3: Create Backend .dockerignore** (AC: 4)
  - [x] Create `backend/.dockerignore`
  - [x] Exclude: __pycache__, .pytest_cache, .coverage, htmlcov, *.pyc
  - [x] Exclude: .git, .env, tests/, *.md, .vscode

### Phase 2: Frontend Production Dockerfile

- [x] **Task 4: Create Multi-Stage Frontend Dockerfile** (AC: 1, 2, 6)
  - [x] Create `frontend/Dockerfile.prod` with multi-stage build
  - [x] Stage 1: Build static assets with npm run build
  - [x] Stage 2: Serve with nginx:alpine
  - [x] Create non-root nginx configuration
  - [x] Configure nginx for SPA routing (fallback to index.html)
  - [x] Verify image size reduction compared to current Dockerfile (507MB → 93MB, 82% reduction)

- [x] **Task 5: Add Frontend Health Check** (AC: 3)
  - [x] Add HEALTHCHECK instruction to Dockerfile.prod
  - [x] Check nginx is serving content
  - [x] Configure appropriate interval, timeout, and retries

- [x] **Task 6: Create Frontend .dockerignore** (AC: 4)
  - [x] Create `frontend/.dockerignore`
  - [x] Exclude: node_modules, coverage, dist, .git
  - [x] Exclude: *.md, .vscode, *.test.ts, *.test.tsx

### Phase 3: Production Docker Compose

- [x] **Task 7: Create docker-compose.prod.yml** (AC: 5)
  - [x] Create production compose file
  - [x] Use Dockerfile.prod for backend and frontend
  - [x] Remove volume mounts (no live reload in prod)
  - [x] Configure production environment variables
  - [x] Add restart policies (unless-stopped or always)
  - [x] Configure proper networking
  - [x] Add depends_on with health check conditions

- [x] **Task 8: Create .env.example for Production** (AC: 5)
  - [x] Document required environment variables
  - [x] Include DATABASE_URL, JWT_SECRET, etc.
  - [x] Add comments explaining each variable

### Phase 4: Validation

- [x] **Task 9: Local Validation**
  - [x] Build production images locally
  - [x] Verify image sizes are smaller than dev images (Backend: 417→401MB, Frontend: 507→93MB)
  - [x] Run docker-compose.prod.yml locally
  - [x] Verify health checks pass (all containers healthy)
  - [x] Verify non-root user with `docker exec ... whoami` (appuser, nginx)
  - [x] Test application functionality end-to-end (registration, health check)
  - [x] Document build commands in README

## Dev Notes

### Architecture Compliance

**New Files:**
- `backend/Dockerfile.prod` - Production backend Dockerfile
- `backend/.dockerignore` - Backend build exclusions
- `frontend/Dockerfile.prod` - Production frontend Dockerfile
- `frontend/.dockerignore` - Frontend build exclusions
- `frontend/nginx.conf` - Nginx configuration for SPA
- `docker-compose.prod.yml` - Production compose configuration
- `.env.example` - Environment variable documentation

**Existing Files (unchanged):**
- `backend/Dockerfile` - Keep for development
- `frontend/Dockerfile` - Keep for development
- `docker-compose.yml` - Keep for development

### Current Docker Setup Analysis

**Backend Dockerfile (current - development):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
Issues: Single stage, runs as root, --reload flag, copies everything

**Frontend Dockerfile (current - development):**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```
Issues: Single stage, runs dev server, runs as root, copies everything

### Backend Production Dockerfile Template

```dockerfile
# backend/Dockerfile.prod

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup app/ ./app/

# Set environment
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Production Dockerfile Template

```dockerfile
# frontend/Dockerfile.prod

# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --only=production=false

COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user setup (nginx alpine runs as nginx user by default)
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration Template

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # SPA routing - fallback to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Compose Production Template

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### .dockerignore Templates

**backend/.dockerignore:**
```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov
coverage.xml
.git
.gitignore
.env
.env.*
tests/
*.md
README*
.vscode
.idea
Dockerfile
Dockerfile.*
docker-compose*
```

**frontend/.dockerignore:**
```
node_modules
coverage
dist
.git
.gitignore
*.md
README*
.vscode
.idea
*.test.ts
*.test.tsx
__tests__
Dockerfile
Dockerfile.*
docker-compose*
.env
.env.*
```

### Expected Image Size Comparison

| Image | Current (Dev) | Production | Reduction |
|-------|---------------|------------|-----------|
| Backend | ~500MB | ~150MB | ~70% |
| Frontend | ~1GB | ~25MB | ~97% |

### Security Considerations

1. **Non-root user**: Both containers run as non-root
2. **Minimal base images**: python:3.11-slim, nginx:alpine
3. **No dev dependencies**: Production images exclude test tools
4. **No source maps**: Frontend build excludes source maps in prod
5. **Read-only filesystem**: Can be enabled in compose

### Testing Commands

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Check image sizes
docker images | grep taskforge

# Run production stack
docker-compose -f docker-compose.prod.yml up -d

# Verify health checks
docker-compose -f docker-compose.prod.yml ps

# Check running user
docker exec taskforge-backend-1 whoami
docker exec taskforge-frontend-1 whoami

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## References

- Epic: [epics-post-mvp.md](../planning-artifacts/epics-post-mvp.md) - Epic 4: CI/CD & DevOps
- Story 4.1: [4-1-github-actions-ci.md](./4-1-github-actions-ci.md) - CI Pipeline
- Story 4.2: [4-2-test-coverage-reporting.md](./4-2-test-coverage-reporting.md) - Test Coverage
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Docker security best practices: https://docs.docker.com/develop/security-best-practices/
- Nginx Docker: https://hub.docker.com/_/nginx

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex CLI)

### Implementation Plan

1. Add production-ready Dockerfiles for backend/frontend (multi-stage, non-root, healthchecks)
2. Add .dockerignore files and nginx SPA configuration
3. Create docker-compose.prod.yml with health-aware dependencies and prod env
4. Update .env.example and README with production guidance
5. Validate with pytest and docker-compose build/run (pending Docker engine)

### Completion Notes List

- Added production Dockerfiles, nginx SPA config, and .dockerignore files for backend/frontend.
- Added docker-compose.prod.yml and production env examples in .env.example.
- Updated README with production Docker commands.
- Tests: `PYTHONPATH=. pytest` (pass); `ruff check .` (pass).
- Docker validation complete: All images built, containers healthy, non-root users verified (appuser, nginx).
- Image sizes: Backend 417→401MB, Frontend 507→93MB (82% reduction).
- End-to-end test: User registration via nginx proxy successful.

### File List

**New:**
- backend/Dockerfile.prod
- backend/.dockerignore
- frontend/Dockerfile.prod
- frontend/.dockerignore
- frontend/nginx.conf
- docker-compose.prod.yml

**Modified:**
- .env.example
- README.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-01-26: Story created with ready-for-dev status.
- 2026-01-26: Added production Docker assets and compose config; updated env docs/README.
- 2026-01-26: Docker validation complete. All ACs met. Status changed to review.
