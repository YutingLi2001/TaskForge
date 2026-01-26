# Story 4.2: Test Coverage Reporting

Status: ready-for-dev

## Story

As a **developer**,
I want **test coverage to be tracked and visible**,
So that **I can identify untested code**.

## Acceptance Criteria

1. **Given** CI pipeline runs backend tests **When** tests complete **Then** coverage report is generated using pytest-cov
2. **Given** CI pipeline runs frontend tests **When** tests complete **Then** coverage report is generated using vitest coverage
3. **Given** CI completes **Then** coverage percentage is displayed in PR comments or check summary
4. **Given** backend test coverage **When** coverage is below 80% **Then** CI fails with clear error message
5. **Given** frontend test coverage **When** coverage is below 70% **Then** CI fails with clear error message
6. **Given** coverage reports are generated **Then** they are uploaded as CI artifacts for detailed review
7. **Given** a PR is opened **Then** coverage badge or summary shows current coverage levels

## Tasks / Subtasks

### Phase 1: Backend Coverage Setup

- [x] **Task 1: Install pytest and pytest-cov** (AC: 1)
  - [x] Add `pytest`, `pytest-asyncio`, and `pytest-cov` to `backend/requirements.txt`
  - [x] Create `pytest.ini` or `pyproject.toml` pytest configuration
  - [x] Configure pytest to discover tests in `backend/tests/`
  - [x] Verify tests still pass with pytest runner locally

- [x] **Task 2: Configure Coverage for Backend** (AC: 1, 4, 6)
  - [x] Add coverage configuration to `pytest.ini` or `.coveragerc`
  - [x] Set source to `backend/app` (exclude tests from coverage)
  - [x] Configure coverage output formats (terminal, XML for CI, HTML for local)
  - [x] Set minimum coverage threshold to 80% with `--cov-fail-under=80`
  - [x] Run locally to verify coverage report generation

### Phase 2: Frontend Coverage Setup

- [x] **Task 3: Configure Vitest Coverage** (AC: 2, 5)
  - [x] Install `@vitest/coverage-v8` (or `@vitest/coverage-istanbul`)
  - [x] Update `vitest.config.ts` with coverage configuration
  - [x] Set coverage thresholds: lines 70%, functions 70%, branches 70%, statements 70%
  - [x] Configure coverage reporters (text, json, lcov for CI)
  - [x] Run `npm run test -- --coverage` locally to verify

### Phase 3: CI Integration

- [x] **Task 4: Update CI Workflow for Backend Coverage** (AC: 1, 4, 6)
  - [x] Modify `.github/workflows/ci.yml` backend job
  - [x] Change test command to `pytest --cov=backend/app --cov-report=xml --cov-report=term --cov-fail-under=80`
  - [x] Upload coverage XML as artifact
  - [x] Ensure CI fails if coverage threshold not met

- [x] **Task 5: Update CI Workflow for Frontend Coverage** (AC: 2, 5, 6)
  - [x] Modify `.github/workflows/ci.yml` frontend job
  - [x] Change test command to include coverage: `npm run test -- --coverage`
  - [x] Upload coverage report as artifact
  - [x] Ensure CI fails if coverage threshold not met

- [x] **Task 6: PR Coverage Summary** (AC: 3, 7)
  - [x] Option A: Use GitHub Actions job summary to display coverage
  - [ ] Option B: Add coverage badge to README using shields.io or codecov
  - [x] Document how developers can view coverage details

### Phase 4: Validation

- [ ] **Task 7: End-to-End Validation**
  - [ ] Create test PR and verify backend coverage report in CI
  - [ ] Verify frontend coverage report in CI
  - [ ] Verify coverage artifacts are downloadable
  - [ ] Test threshold enforcement: temporarily lower coverage and verify CI fails
  - [ ] Verify coverage summary is visible in PR
  - [ ] Document current coverage levels

## Dev Notes

### Architecture Compliance

**New Files:**
- `pytest.ini` or update `pyproject.toml` - Pytest configuration
- `.coveragerc` (optional) - Coverage configuration if not in pytest.ini

**Modified Files:**
- `backend/requirements.txt` - Add pytest, pytest-asyncio, pytest-cov
- `frontend/package.json` - Add coverage script
- `frontend/vite.config.ts` or `vitest.config.ts` - Coverage configuration
- `.github/workflows/ci.yml` - Coverage commands and artifact uploads

### Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = backend/tests
asyncio_mode = auto
addopts = -v --tb=short

# Coverage settings
[coverage:run]
source = backend/app
omit =
    backend/tests/*
    */__pycache__/*

[coverage:report]
fail_under = 80
show_missing = true
```

### Vitest Coverage Configuration

```typescript
// vitest.config.ts (or vite.config.ts test section)
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'lcov'],
      reportsDirectory: './coverage',
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/**/*.d.ts'],
    },
  },
});
```

### CI Workflow Updates

```yaml
# .github/workflows/ci.yml changes

jobs:
  backend:
    # ... existing setup ...
    steps:
      # ... checkout, setup-python, install deps ...
      - name: Run linting
        run: ruff check backend/

      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term --cov-fail-under=80
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/taskforge_test

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: backend/coverage.xml

  frontend:
    # ... existing setup ...
    steps:
      # ... checkout, setup-node, npm install ...
      - name: Run linting
        run: cd frontend && npm run lint

      - name: Run tests with coverage
        run: cd frontend && npm run test -- --coverage

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: frontend-coverage
          path: frontend/coverage/
```

### Test Migration Notes

The current tests use Python's `unittest`. When adding pytest:
1. Pytest can run unittest tests directly - no immediate migration needed
2. `pytest-asyncio` handles async test methods
3. Gradually migrate to pytest fixtures for cleaner test setup
4. The `asyncio.run()` pattern in current tests works with pytest-asyncio's `auto` mode

### Coverage Thresholds Rationale

| Component | Threshold | Rationale |
|-----------|-----------|-----------|
| Backend | 80% | Core business logic should be well-tested |
| Frontend | 70% | UI has more edge cases, visual testing gaps |

### Current Test Inventory

**Backend Tests:**
- `backend/tests/api/` - API integration tests (5 files)
- `backend/tests/unit/` - Unit tests (2 files)

**Frontend Tests:**
- `frontend/src/**/*.test.tsx` - Component and route tests

### Viewing Coverage Locally

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Frontend
cd frontend
npm run test -- --coverage
# Open coverage/index.html in browser
```

## References

- Epic: [epics-post-mvp.md](../planning-artifacts/epics-post-mvp.md) - Epic 4: CI/CD & DevOps
- FR16: Test coverage is tracked and reported
- NFR11: Test coverage > 80% for backend, > 70% for frontend
- Pytest-cov docs: https://pytest-cov.readthedocs.io/
- Vitest coverage docs: https://vitest.dev/guide/coverage.html
- Story 4.1: [4-1-github-actions-ci.md](./4-1-github-actions-ci.md) - Existing CI workflow

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

1. Add pytest and pytest-cov to backend, configure pytest.ini
2. Verify existing tests pass with pytest runner
3. Add coverage configuration with 80% threshold
4. Configure Vitest coverage with 70% threshold
5. Update CI workflow with coverage commands
6. Add coverage artifact uploads
7. Add coverage summary to job output
8. Validate with test PR

### Completion Notes List

- Added pytest dependencies and `pytest.ini` for backend test discovery.
- Added coverage configuration and backend health/init tests to meet 80% threshold.
- Ran `python -m pytest -q` (115 tests passed, coverage 80.29%).
- Added Vitest coverage configuration and tests to satisfy 70% thresholds.
- Ran `npm run test -- --coverage` (96 tests passed, coverage thresholds met).
- Updated CI backend job to run pytest with coverage and upload coverage artifacts.
- Updated CI frontend job to run vitest coverage and upload coverage artifacts.
- Added CI job summaries for backend/frontend coverage and documented artifact access (Option A for PR summary).

### File List

**New:**
- pytest.ini
- .coveragerc
- backend/tests/unit/test_main.py
- frontend/src/App.test.tsx
- frontend/src/main.test.tsx

**Modified:**
- backend/requirements.txt
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/src/api/client.test.ts
- .github/workflows/ci.yml
- README.md

### Change Log

- 2026-01-26: Story created with ready-for-dev status.
- 2026-01-26: Added pytest dependencies and configuration for backend tests.
- 2026-01-26: Added backend coverage config and health/init tests to reach 80% coverage threshold.
- 2026-01-26: Added frontend coverage config and tests to meet 70% thresholds.
- 2026-01-26: Updated CI backend job to run pytest coverage and upload artifacts.
- 2026-01-26: Updated CI frontend job to run coverage and upload artifacts.
- 2026-01-26: Added PR coverage summaries and coverage viewing documentation.
