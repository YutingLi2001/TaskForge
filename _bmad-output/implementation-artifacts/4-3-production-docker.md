# Story 4.3: Production Docker Configuration

Status: ready-for-dev

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

- [ ] **Task 1: Create Multi-Stage Backend Dockerfile** (AC: 1, 2, 7)
  - [ ] Create `backend/Dockerfile.prod` with multi-stage build
  - [ ] Stage 1: Install dependencies in builder stage
  - [ ] Stage 2: Copy only necessary files to slim runtime image
  - [ ] Create non-root user (appuser) and set ownership
  - [ ] Remove --reload flag from uvicorn command
  - [ ] Verify image size reduction compared to current Dockerfile

- [ ] **Task 2: Add Backend Health Check** (AC: 3)
  - [ ] Add HEALTHCHECK instruction to Dockerfile.prod
  - [ ] Use existing /api/health endpoint
  - [ ] Configure appropriate interval, timeout, and retries

- [ ] **Task 3: Create Backend .dockerignore** (AC: 4)
  - [ ] Create `backend/.dockerignore`
  - [ ] Exclude: __pycache__, .pytest_cache, .coverage, htmlcov, *.pyc
  - [ ] Exclude: .git, .env, tests/, *.md, .vscode

### Phase 2: Frontend Production Dockerfile

- [ ] **Task 4: Create Multi-Stage Frontend Dockerfile** (AC: 1, 2, 6)
  - [ ] Create `frontend/Dockerfile.prod` with multi-stage build
  - [ ] Stage 1: Build static assets with npm run build
  - [ ] Stage 2: Serve with nginx:alpine
  - [ ] Create non-root nginx configuration
  - [ ] Configure nginx for SPA routing (fallback to index.html)
  - [ ] Verify image size reduction compared to current Dockerfile

- [ ] **Task 5: Add Frontend Health Check** (AC: 3)
  - [ ] Add HEALTHCHECK instruction to Dockerfile.prod
  - [ ] Check nginx is serving content
  - [ ] Configure appropriate interval, timeout, and retries

- [ ] **Task 6: Create Frontend .dockerignore** (AC: 4)
  - [ ] Create `frontend/.dockerignore`
  - [ ] Exclude: node_modules, coverage, dist, .git
  - [ ] Exclude: *.md, .vscode, *.test.ts, *.test.tsx

### Phase 3: Production Docker Compose

- [ ] **Task 7: Create docker-compose.prod.yml** (AC: 5)
  - [ ] Create production compose file
  - [ ] Use Dockerfile.prod for backend and frontend
  - [ ] Remove volume mounts (no live reload in prod)
  - [ ] Configure production environment variables
  - [ ] Add restart policies (unless-stopped or always)
  - [ ] Configure proper networking
  - [ ] Add depends_on with health check conditions

- [ ] **Task 8: Create .env.example for Production** (AC: 5)
  - [ ] Document required environment variables
  - [ ] Include DATABASE_URL, JWT_SECRET, etc.
  - [ ] Add comments explaining each variable

### Phase 4: Validation

- [ ] **Task 9: Local Validation**
  - [ ] Build production images locally
  - [ ] Verify image sizes are smaller than dev images
  - [ ] Run docker-compose.prod.yml locally
  - [ ] Verify health checks pass
  - [ ] Verify non-root user with `docker exec ... whoami`
  - [ ] Test application functionality end-to-end
  - [ ] Document build commands in README

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

(To be filled during implementation)

### Implementation Plan

1. Create backend Dockerfile.prod with multi-stage build and non-root user
2. Add backend health check and .dockerignore
3. Create frontend Dockerfile.prod with nginx
4. Add frontend nginx.conf, health check, and .dockerignore
5. Create docker-compose.prod.yml
6. Create .env.example documentation
7. Validate locally with build and run tests
8. Document in README

### Completion Notes List

(To be filled during implementation)

### File List

**New:**
(To be filled during implementation)

**Modified:**
(To be filled during implementation)

### Change Log

- 2026-01-26: Story created with ready-for-dev status.
