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

- [ ] **Task 1: Install Alembic** (AC: 1, 2)
  - [ ] Add `alembic` to `backend/requirements.txt`
  - [ ] Run `pip install -r backend/requirements.txt` to install
  - [ ] Verify Alembic CLI is available: `alembic --version`

- [ ] **Task 2: Initialize Alembic** (AC: 1, 3)
  - [ ] Navigate to `backend/` directory
  - [ ] Run `alembic init alembic` to create migration environment
  - [ ] Verify directory structure created:
    ```
    backend/
    ├── alembic/
    │   ├── versions/         # Migration files go here
    │   ├── env.py            # Migration runtime config
    │   ├── script.py.mako    # Migration template
    │   └── README
    └── alembic.ini           # Alembic configuration
    ```

- [ ] **Task 3: Configure Alembic** (AC: 1, 2)
  - [ ] Update `alembic.ini`:
    - Set `sqlalchemy.url` to use environment variable
    - Configure file template location
    - Set timezone handling
  - [ ] Update `alembic/env.py`:
    - Import app configuration and database URL from `app/config.py`
    - Import Base metadata from `app/models/__init__.py`
    - Configure `target_metadata = Base.metadata`
    - Set `compare_type=True` for type checking
    - Add `render_as_batch=True` for SQLite compatibility (dev/test)
  - [ ] Verify configuration by running `alembic current` (should show no version yet)

### Phase 2: Initial Migration

- [ ] **Task 4: Generate Initial Migration** (AC: 1, 2, 3)
  - [ ] Ensure all models are imported in `app/models/__init__.py`
  - [ ] Generate initial migration capturing current schema:
    ```bash
    alembic revision --autogenerate -m "Initial schema"
    ```
  - [ ] Review generated migration file in `alembic/versions/`
  - [ ] Verify it includes tables: users, projects, tasks
  - [ ] Check for correct column types, constraints, and indexes

- [ ] **Task 5: Test Initial Migration** (AC: 2, 3, 4)
  - [ ] Apply migration to development database:
    ```bash
    alembic upgrade head
    ```
  - [ ] Verify tables are created correctly
  - [ ] Check `alembic_version` table shows current revision
  - [ ] Test downgrade:
    ```bash
    alembic downgrade -1
    ```
  - [ ] Verify tables are dropped and version is updated
  - [ ] Re-apply migration: `alembic upgrade head`

### Phase 3: Integration with Application

- [ ] **Task 6: Update Application Startup** (AC: 5)
  - [ ] Create migration script `backend/run_migrations.py`:
    - Load database URL from config
    - Run `alembic upgrade head` programmatically
    - Handle errors and log migration status
  - [ ] Update `backend/app/main.py` to run migrations on startup (optional)
  - [ ] Add migration command to Docker entrypoint

- [ ] **Task 7: Docker Integration** (AC: 5, 7)
  - [ ] Update `backend/Dockerfile` (dev and prod):
    - Ensure `alembic.ini` and `alembic/` directory are copied
    - Add migration files to image
  - [ ] Update `docker-compose.yml` backend service:
    - Add command to run migrations before starting app:
      ```yaml
      command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
      ```
  - [ ] Update `docker-compose.prod.yml` similarly
  - [ ] Test with fresh database: `docker-compose down -v && docker-compose up`

- [ ] **Task 8: CI/Test Integration** (AC: 6)
  - [ ] Update `backend/tests/conftest.py` or test setup:
    - Run migrations in test database setup
    - Replace manual table creation with `alembic upgrade head`
  - [ ] Update CI workflow `.github/workflows/ci.yml`:
    - Ensure migrations run before tests
    - Verify test database is created via migrations
  - [ ] Run tests locally to verify: `pytest`
  - [ ] Push to CI and verify tests pass

### Phase 4: Documentation & Migration Workflow

- [ ] **Task 9: Create Migration Workflow Documentation**
  - [ ] Create `docs/development/database-migrations.md` covering:
    - How to generate a migration after model changes
    - How to review and edit migrations
    - How to apply and rollback migrations
    - Common issues and troubleshooting
  - [ ] Add migration commands to README.md
  - [ ] Document migration best practices

- [ ] **Task 10: Create Sample Migration** (AC: 1, 2, 4)
  - [ ] Make a test model change (e.g., add a field to Task model)
  - [ ] Generate migration: `alembic revision --autogenerate -m "Add test field"`
  - [ ] Review generated migration for correctness
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify change in database
  - [ ] Rollback: `alembic downgrade -1`
  - [ ] Verify rollback worked
  - [ ] Remove test change and migration file

### Phase 5: Production Readiness

- [ ] **Task 11: Production Migration Strategy**
  - [ ] Document production migration process in `docs/deployment/migrations.md`:
    - Pre-deployment: Review migrations, test rollback
    - During deployment: Run migrations before new code
    - Post-deployment: Verify migration success
    - Rollback procedure if deployment fails
  - [ ] Create `scripts/deploy/run-migrations.sh` for manual migration execution
  - [ ] Add migration checklist to deployment guide

- [ ] **Task 12: Backup and Rollback Planning**
  - [ ] Document database backup before migrations
  - [ ] Create `scripts/backup/backup-db.sh` for pre-migration backups
  - [ ] Test rollback with sample data
  - [ ] Document recovery procedures

### Phase 6: Validation

- [ ] **Task 13: End-to-End Migration Testing**
  - [ ] Start with fresh database (no tables)
  - [ ] Run migrations: `alembic upgrade head`
  - [ ] Verify all tables created correctly
  - [ ] Run application and create test data
  - [ ] Make a model change and generate migration
  - [ ] Apply new migration
  - [ ] Verify schema updated without data loss
  - [ ] Test rollback of last migration
  - [ ] Verify data integrity after rollback

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

_To be filled during implementation_

### Implementation Plan

_To be filled during implementation_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_

### Change Log

- 2026-02-04: Story created with ready-for-dev status.
