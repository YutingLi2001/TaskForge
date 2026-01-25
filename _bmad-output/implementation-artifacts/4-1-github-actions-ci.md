# Story 4.1: GitHub Actions CI

Status: ready-for-dev

## Story

As a **developer**,
I want **automated tests to run on every pull request**,
So that **code quality is validated before merging**.

## Acceptance Criteria

1. **Given** I open a pull request to `develop` branch **When** GitHub Actions workflow triggers **Then** all CI jobs run automatically
2. **Given** CI is running **Then** backend tests execute using `python -m unittest discover`
3. **Given** CI is running **Then** frontend tests execute using `npm run test`
4. **Given** CI is running **Then** backend linting passes using `ruff check`
5. **Given** CI is running **Then** frontend linting passes using `npm run lint`
6. **Given** CI is running **Then** frontend build succeeds using `npm run build` (includes TypeScript type-check)
7. **Given** CI is running **Then** backend and frontend jobs run in parallel
8. **Given** CI is running **Then** PostgreSQL database is available for backend tests
9. **Given** the workflow completes **Then** it finishes in < 5 minutes
10. **Given** any CI check fails **Then** the PR cannot be merged to `develop`
11. **Given** CI completes **Then** logs are visible in GitHub Actions UI and downloadable as artifacts

## Tasks / Subtasks

### Phase 1: Backend CI Configuration

- [x] **Task 1: Add Ruff Configuration** (AC: 4)
  - [x] Add `ruff` to `backend/requirements.txt` (or create `requirements-dev.txt`)
  - [x] Create `ruff.toml` or `pyproject.toml` with ruff settings
  - [x] Configure ruff rules (recommend: `select = ["E", "F", "I"]` for errors, pyflakes, isort)
  - [x] Run `ruff check backend/` locally to verify no initial errors (fix if needed)

- [x] **Task 2: Backend CI Job** (AC: 2, 4, 8)
  - [x] Create `.github/workflows/ci.yml`
  - [x] Configure trigger: `pull_request` to `develop` branch
  - [x] Add `backend` job with `ubuntu-latest` runner
  - [x] Add PostgreSQL service container with health check
  - [x] Set environment variables for database connection
  - [x] Add steps: checkout, setup-python (3.11), install dependencies, ruff check, run tests
  - [x] Upload test logs as artifacts

### Phase 2: Frontend CI Configuration

- [x] **Task 3: Frontend CI Job** (AC: 3, 5, 6)
  - [x] Add `frontend` job to `.github/workflows/ci.yml`
  - [x] Use `ubuntu-latest` runner
  - [x] Add steps: checkout, setup-node (20), npm install, npm run lint, npm run test, npm run build
  - [x] Upload build artifacts (optional, for verification)

### Phase 3: Parallelization & Branch Protection

- [ ] **Task 4: Parallel Job Configuration** (AC: 7, 9)
  - [x] Ensure `backend` and `frontend` jobs have no `needs` dependency (run in parallel)
  - [x] Add timeout limits to jobs (e.g., 10 minutes max)
  - [ ] Test workflow locally or on a test PR to verify parallel execution

- [ ] **Task 5: Branch Protection Rules** (AC: 10)
  - [ ] Document branch protection setup in story file (manual GitHub UI step)
  - [ ] Enable "Require status checks to pass before merging" for `develop`
  - [ ] Select `backend` and `frontend` jobs as required checks
  - [ ] Enable "Require branches to be up to date before merging" (optional but recommended)

### Phase 4: Validation

- [ ] **Task 6: End-to-End Validation**
  - [ ] Create test PR with passing code
  - [ ] Verify both jobs run in parallel
  - [ ] Verify all checks pass
  - [ ] Verify logs are accessible and downloadable
  - [ ] Verify workflow completes in < 5 minutes
  - [ ] Create test PR with failing test
  - [ ] Verify merge is blocked when checks fail
  - [ ] Document any issues and fixes

## Dev Notes

### Architecture Compliance

**New Files:**
- `.github/workflows/ci.yml` - Main CI workflow
- `ruff.toml` or `pyproject.toml` - Ruff linter configuration

**Modified Files:**
- `backend/requirements.txt` - Add ruff dependency (or create requirements-dev.txt)

### CI Workflow Structure

```yaml
name: CI

on:
  pull_request:
    branches: [develop]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: taskforge_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: ruff check backend/
      - run: python -m unittest discover -s backend/tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/taskforge_test

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test
      - run: cd frontend && npm run build
```

### Ruff Configuration

```toml
# ruff.toml
[lint]
select = ["E", "F", "I"]  # pycodestyle errors, pyflakes, isort
ignore = ["E501"]  # line too long (let formatter handle)

[lint.isort]
known-first-party = ["app"]
```

### Branch Protection Setup (Manual)

1. Go to GitHub repo → Settings → Branches
2. Add rule for `develop` branch
3. Enable "Require a pull request before merging"
4. Enable "Require status checks to pass before merging"
5. Search and select: `backend`, `frontend`
6. Enable "Require branches to be up to date before merging"
7. Save changes

### Environment Variables

Backend tests need these environment variables in CI:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - For auth tests (can use a test value)
- `JWT_ALGORITHM` - HS256

### Local vs CI Relationship

| Aspect | Local (Windows/Mac) | CI (Linux) |
|--------|---------------------|------------|
| Trigger | Manual (.ps1/.sh) | Automatic (PR) |
| Database | SQLite (test) | PostgreSQL (service) |
| Logs | `logs/` folder | GitHub Actions UI |
| Linting | Optional | Required |
| Purpose | Fast feedback | Gate for merge |

### Success Metrics

- [ ] CI completes in < 5 minutes
- [ ] Both jobs run in parallel
- [ ] Failed checks block PR merge
- [ ] Logs are accessible in GitHub UI

## References

- Epic: [epics-post-mvp.md](../planning-artifacts/epics-post-mvp.md) - Epic 4: CI/CD & DevOps
- FR15: Automated CI/CD pipeline validates all code changes
- NFR10: CI pipeline runs in < 5 minutes
- GitHub Actions docs: https://docs.github.com/en/actions
- Ruff docs: https://docs.astral.sh/ruff/

## Dev Agent Record

### Agent Model Used

(To be filled by implementing agent)

### Implementation Plan

1. Add ruff to backend dependencies and configure
2. Fix any existing linting errors
3. Create CI workflow with backend job (PostgreSQL service, ruff, tests)
4. Add frontend job (lint, test, build)
5. Verify parallel execution
6. Test with passing and failing PRs
7. Configure branch protection (manual step, document completion)

### Completion Notes List

- Added `ruff` to backend requirements and created `ruff.toml` configuration.
- Ran `python -m ruff check --fix backend/` and `python -m ruff check backend/` to resolve import ordering and unused imports.
- Added GitHub Actions CI workflow with parallel backend/frontend jobs, PostgreSQL service, and log artifacts (pending PR validation).

### File List

**New:**
- .github/workflows/ci.yml
- ruff.toml (or pyproject.toml)

**Modified:**
- backend/requirements.txt (add ruff)
- backend/app/config.py
- backend/app/main.py
- backend/app/models/user.py
- backend/app/routers/auth.py
- backend/app/schemas/user.py
- backend/app/utils/auth.py
- backend/tests/api/test_auth_login_api.py
- backend/tests/api/test_projects_api.py
- backend/tests/api/test_tasks_api.py
- backend/tests/unit/test_auth_registration.py
- backend/tests/unit/test_project_model.py

### Change Log

- 2026-01-24: Story created with ready-for-dev status based on requirements discussion.
