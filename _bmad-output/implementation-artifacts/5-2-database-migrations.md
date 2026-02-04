# Story 5.2: Database Migrations (Alembic)

Status: ready-for-dev

## Story

As a **developer**,
I want **database schema changes managed via Alembic migrations**,
So that **schema updates are versioned and reversible**.

## Background

Currently, the TaskForge application uses SQLAlchemy models but lacks a formal migration system. Schema changes require manual SQL or dropping/recreating tables, which is:
- Not version-controlled
- Not reversible
- Risky in production
- Difficult to coordinate across environments

Alembic provides:
- Automated migration generation from model changes
- Version-controlled migration history
- Rollback capability
- Safe production deployments

This story is part of Epic 5: Production Deployment and is a prerequisite for safe production database management.

## Acceptance Criteria

1. **Given** I modify a SQLAlchemy model **When** I generate a migration **Then** Alembic creates a migration file with upgrade() and downgrade() functions
2. **Given** I have a new migration **When** I run `alembic upgrade head` **Then** the database schema is updated to match the models
3. **Given** a migration is applied **When** I check migration history **Then** the migration version is tracked in alembic_version table
4. **Given** a problematic migration **When** I run `alembic downgrade -1` **Then** the migration is rolled back successfully
5. **Given** application starts **When** Docker containers initialize **Then** migrations run automatically before the app starts
6. **Given** CI pipeline runs **When** tests execute **Then** test database uses migrations for schema setup
7. **Given** migrations exist **When** I deploy to production **Then** migrations run as part of deployment process

## Tasks / Subtasks

### Phase 1: Alembic Setup

- [x] **Task 1: Install Alembic** (AC: 1, 2)
  - [x] Add `alembic` to `backend/requirements.txt`
  - [x] Run `pip install -r backend/requirements.txt` to install
  - [x] Verify Alembic CLI is available: `alembic --version`

- [x] **Task 2: Initialize Alembic** (AC: 1, 3)
  - [x] Navigate to `backend/` directory
  - [x] Run `alembic init alembic` to create migration environment
  - [x] Verify directory structure created:
    ```
    backend/
    ├── alembic/
    │   ├── versions/         # Migration files go here
    │   ├── env.py            # Migration runtime config
    │   ├── script.py.mako    # Migration template
    │   └── README
    └── alembic.ini           # Alembic configuration
    ```

- [x] **Task 3: Configure Alembic** (AC: 1, 2)
  - [x] Update `alembic.ini`:
    - Set `sqlalchemy.url` to use environment variable
    - Configure file template location
    - Set timezone handling
  - [x] Update `alembic/env.py`:
    - Import app configuration and database URL from `app/config.py`
    - Import Base metadata from `app/models/__init__.py`
    - Configure `target_metadata = Base.metadata`
    - Set `compare_type=True` for type checking
    - Add `render_as_batch=True` for SQLite compatibility (dev/test)
  - [x] Verify configuration by running `alembic current` (should show no version yet)

### Phase 2: Initial Migration

- [x] **Task 4: Generate Initial Migration** (AC: 1, 2, 3)
  - [x] Ensure all models are imported in `app/models/__init__.py`
  - [x] Generate initial migration capturing current schema:
    ```bash
    alembic revision --autogenerate -m "Initial schema"
    ```
  - [x] Review generated migration file in `alembic/versions/`
  - [x] Verify it includes tables: users, projects, tasks
  - [x] Check for correct column types, constraints, and indexes

- [x] **Task 5: Test Initial Migration** (AC: 2, 3, 4)
  - [x] Apply migration to development database:
    ```bash
    alembic upgrade head
    ```
  - [x] Verify tables are created correctly
  - [x] Check `alembic_version` table shows current revision
  - [x] Test downgrade:
    ```bash
    alembic downgrade -1
    ```
  - [x] Verify tables are dropped and version is updated
  - [x] Re-apply migration: `alembic upgrade head`

### Phase 3: Integration with Application

- [x] **Task 6: Update Application Startup** (AC: 5)
  - [x] Create migration script `backend/run_migrations.py`:
    - Load database URL from config
    - Run `alembic upgrade head` programmatically
    - Handle errors and log migration status
  - [x] Update `backend/app/main.py` to run migrations on startup (optional)
  - [x] Add migration command to Docker entrypoint

- [x] **Task 7: Docker Integration** (AC: 5, 7)
  - [x] Update `backend/Dockerfile` (dev and prod):
    - Ensure `alembic.ini` and `alembic/` directory are copied
    - Add migration files to image
  - [x] Update `docker-compose.yml` backend service:
    - Add command to run migrations before starting app:
      ```yaml
      command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
      ```
  - [x] Update `docker-compose.prod.yml` similarly
  - [x] Test with fresh database: `docker-compose down -v && docker-compose up`

- [x] **Task 8: CI/Test Integration** (AC: 6)
  - [x] Update `backend/tests/conftest.py` or test setup:
    - Run migrations in test database setup
    - Replace manual table creation with `alembic upgrade head`
  - [x] Update CI workflow `.github/workflows/ci.yml`:
    - Ensure migrations run before tests
    - Verify test database is created via migrations
  - [x] Run tests locally to verify: `pytest`
  - [ ] Push to CI and verify tests pass

### Phase 4: Documentation & Migration Workflow

- [x] **Task 9: Create Migration Workflow Documentation**
  - [x] Create `docs/development/database-migrations.md` covering:
    - How to generate a migration after model changes
    - How to review and edit migrations
    - How to apply and rollback migrations
    - Common issues and troubleshooting
  - [x] Add migration commands to README.md
  - [x] Document migration best practices

- [x] **Task 10: Create Sample Migration** (AC: 1, 2, 4)
  - [x] Make a test model change (e.g., add a field to Task model)
  - [x] Generate migration: `alembic revision --autogenerate -m "Add test field"`
  - [x] Review generated migration for correctness
  - [x] Apply migration: `alembic upgrade head`
  - [x] Verify change in database
  - [x] Rollback: `alembic downgrade -1`
  - [x] Verify rollback worked
  - [x] Remove test change and migration file

### Phase 5: Production Readiness

- [x] **Task 11: Production Migration Strategy**
  - [x] Document production migration process in `docs/deployment/migrations.md`:
    - Pre-deployment: Review migrations, test rollback
    - During deployment: Run migrations before new code
    - Post-deployment: Verify migration success
    - Rollback procedure if deployment fails
  - [x] Create `scripts/deploy/run-migrations.sh` for manual migration execution
  - [x] Add migration checklist to deployment guide

- [x] **Task 12: Backup and Rollback Planning**
  - [x] Document database backup before migrations
  - [x] Create `scripts/backup/backup-db.sh` for pre-migration backups
  - [x] Test rollback with sample data
  - [x] Document recovery procedures

### Phase 6: Validation

- [x] **Task 13: End-to-End Migration Testing**
  - [x] Start with fresh database (no tables)
  - [x] Run migrations: `alembic upgrade head`
  - [x] Verify all tables created correctly
  - [x] Run application and create test data
  - [x] Make a model change and generate migration
  - [x] Apply new migration
  - [x] Verify schema updated without data loss
  - [x] Test rollback of last migration
  - [x] Verify data integrity after rollback

- [ ] **Task 14: CI/CD Validation**
  - [ ] Create test PR with a sample migration
  - [ ] Verify CI runs migrations before tests
  - [ ] Verify tests pass with migration-created schema
  - [ ] Merge PR and verify production deployment would work
  - [ ] Document that migrations run automatically in Docker

## Dev Notes

### Architecture Compliance

**New Files:**
- `backend/alembic.ini` - Alembic configuration
- `backend/alembic/env.py` - Migration environment (generated, then modified)
- `backend/alembic/script.py.mako` - Migration template
- `backend/alembic/versions/XXXX_initial_schema.py` - Initial migration
- `backend/run_migrations.py` (optional) - Programmatic migration runner
- `docs/development/database-migrations.md` - Migration workflow guide
- `docs/deployment/migrations.md` - Production migration guide
- `scripts/deploy/run-migrations.sh` - Manual migration script
- `scripts/backup/backup-db.sh` - Pre-migration backup script

**Modified Files:**
- `backend/requirements.txt` - Add alembic
- `backend/Dockerfile` - Copy alembic files
- `backend/Dockerfile.prod` - Copy alembic files
- `docker-compose.yml` - Run migrations on startup
- `docker-compose.prod.yml` - Run migrations on startup
- `backend/tests/conftest.py` - Use migrations for test DB setup
- `.github/workflows/ci.yml` - Ensure migrations run before tests
- `README.md` - Add migration commands

### Alembic Configuration

```ini
# alembic.ini (key sections)
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url =
# Leave empty - we'll set via env.py from DATABASE_URL

[post_write_hooks]
# Optional: format migrations with black/ruff
```

```python
# alembic/env.py (key changes)
from app.config import settings
from app.models import Base

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            render_as_batch=True,  # SQLite compatibility
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Docker Entrypoint Pattern

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations then start app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Migration Workflow

```bash
# 1. Make model changes
# Edit app/models/task.py, for example

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add description to Task"

# 3. Review migration file
# Check alembic/versions/XXXX_add_description_to_task.py

# 4. Edit if needed (Alembic doesn't catch everything)
# Manual edits for complex changes

# 5. Apply migration
alembic upgrade head

# 6. Test rollback
alembic downgrade -1

# 7. Re-apply
alembic upgrade head

# 8. Commit migration file to git
git add alembic/versions/XXXX_add_description_to_task.py
git commit -m "Add description field to Task model"
```

### Migration Best Practices

1. **Always review generated migrations** - Alembic autogenerate is good but not perfect
2. **Test rollback** - Every migration should have a working downgrade()
3. **Use descriptive messages** - Clear migration names aid debugging
4. **Backup before production migrations** - Always have a rollback plan
5. **One logical change per migration** - Easier to rollback specific changes
6. **Don't modify applied migrations** - Create a new migration to fix issues
7. **Keep migrations in version control** - Essential for team coordination

### Common Issues

**Issue: Alembic doesn't detect model changes**
- Ensure all models are imported in `app/models/__init__.py`
- Check that `target_metadata = Base.metadata` in `alembic/env.py`
- Some changes (renames) require manual migration edits

**Issue: Migration fails in production**
- Test migrations on production-like data first
- Use transactions (Alembic default) for atomic migrations
- Have rollback plan and database backup

**Issue: Test database not using migrations**
- Update `conftest.py` to run `alembic upgrade head` instead of `Base.metadata.create_all()`
- Ensure test database URL is set correctly

### Useful Commands

```bash
# Check current migration version
alembic current

# View migration history
alembic history --verbose

# Upgrade to specific version
alembic upgrade <revision_id>

# Downgrade to specific version
alembic downgrade <revision_id>

# Show SQL without executing
alembic upgrade head --sql

# Merge multiple heads (if branches exist)
alembic merge heads -m "Merge migrations"
```

## References

- Epic: [epics-post-mvp.md](../planning-artifacts/epics-post-mvp.md) - Epic 5: Production Deployment
- FR18: Database schema changes are managed via migrations
- Story 5.1: [5-1-oracle-cloud-setup.md](./5-1-oracle-cloud-setup.md) - Production deployment context
- Alembic docs: https://alembic.sqlalchemy.org/en/latest/
- SQLAlchemy docs: https://docs.sqlalchemy.org/

## Checklist

- [ ] Alembic installed and initialized
- [ ] alembic.ini configured with environment-based DB URL
- [ ] env.py configured with Base.metadata
- [ ] Initial migration generated and tested
- [ ] Migrations run automatically in Docker
- [ ] Test database uses migrations
- [ ] CI validates migrations before tests
- [ ] Migration workflow documented
- [ ] Production migration strategy documented
- [ ] Backup and rollback procedures documented
- [ ] Sample migration tested (apply + rollback)
- [ ] All acceptance criteria validated

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

- Add Alembic dependency to backend requirements.
- Initialize Alembic environment and add guard tests for generated artifacts.
- Configure Alembic config/env with app settings and metadata.
- Install dependencies and verify Alembic CLI availability.

### Completion Notes List

- Installed Alembic, verified CLI, and added a requirements guard test.
- Initialized Alembic environment and added a guard test for generated artifacts.
- Configured Alembic settings/env and verified `alembic current` against the dev DB.
- Generated initial migration with users/projects/tasks tables and verified contents.
- Applied, downgraded, and re-applied the initial migration; verified table creation and alembic_version tracking.
- Added a migration runner script and wired app startup to run migrations.
- Updated Docker images/compose to include migrations and verified fresh DB bootstrap.
- Updated test setup to use Alembic migrations and added CI migration step; ran targeted pytest validation.
- Ran full pytest suite; coverage passed (80%+).
- Documented migration workflows, deployment strategy, and backups; validated rollback with sample data.
- Sample migration was generated/applied/rolled back and removed; database revision reset to initial schema.
- Completed end-to-end migration test on fresh DB with sample data and verified rollback integrity.

### File List

- backend/requirements.txt
- backend/tests/unit/test_requirements_include_alembic.py
- backend/tests/unit/test_alembic_init_artifacts.py
- backend/tests/unit/test_alembic_config.py
- backend/tests/unit/test_alembic_initial_migration.py
- backend/tests/unit/test_run_migrations_script.py
- backend/tests/unit/test_docker_migration_commands.py
- backend/tests/utils/__init__.py
- backend/tests/utils/migrations.py
- backend/tests/api/test_auth_login_api.py
- backend/tests/api/test_auth_me_api.py
- backend/tests/api/test_auth_registration_api.py
- backend/tests/api/test_projects_api.py
- backend/tests/api/test_tasks_api.py
- backend/tests/unit/test_auth_dependency.py
- backend/tests/unit/test_auth_login.py
- backend/tests/unit/test_auth_registration.py
- backend/tests/unit/test_project_model.py
- backend/tests/unit/test_task_model.py
- backend/tests/unit/test_main.py
- backend/alembic.ini
- backend/alembic/env.py
- backend/alembic/script.py.mako
- backend/alembic/README
- backend/alembic/versions
- backend/alembic/versions/2026_02_04_757092c30fc9_initial_schema.py
- backend/run_migrations.py
- backend/app/main.py
- backend/Dockerfile.prod
- .env
- docker-compose.yml
- docker-compose.prod.yml
- .github/workflows/ci.yml
- docs/development/database-migrations.md
- docs/deployment/migrations.md
- scripts/deploy/run-migrations.sh
- scripts/backup/backup-db.sh
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-02-04: Story created with ready-for-dev status.
- 2026-02-04: Completed Task 1 (install Alembic dependency and verification).
- 2026-02-04: Completed Task 2 (initialize Alembic environment).
- 2026-02-04: Completed Task 3 (configure Alembic and verify configuration).
- 2026-02-04: Completed Task 4 (generate initial migration).
- 2026-02-04: Completed Task 5 (test initial migration upgrade/downgrade).
- 2026-02-04: Completed Task 6 (application startup migrations).
- 2026-02-04: Completed Task 7 (Docker migration integration).
- 2026-02-04: Completed Task 8 (test and CI migration integration).
- 2026-02-04: Completed Task 9 (migration docs).
- 2026-02-04: Completed Task 10 (sample migration apply/rollback).
- 2026-02-04: Completed Task 11 (production migration strategy).
- 2026-02-04: Completed Task 12 (backup and rollback planning).
- 2026-02-04: Completed Task 13 (end-to-end migration testing).
