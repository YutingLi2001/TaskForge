# Production Migrations

This guide describes how to run migrations safely in production.

## Pre-deployment Checklist

- Review pending migrations in `backend/alembic/versions/`.
- Verify downgrade() is safe for each migration.
- Test migrations on a staging environment.
- Take a backup before applying migrations.

## Run Migrations During Deployment

Use the deploy script (recommended):

```bash
scripts/deploy/run-migrations.sh
```

Or run Alembic directly:

```bash
cd backend
alembic upgrade head
```

## Post-deployment Verification

- Confirm `alembic_version` shows the expected revision.
- Run a health check: `GET /api/health`.
- Validate critical workflows (login, create project, create task).

## Rollback Procedure

If a migration introduces issues:

1. Downgrade one step:
   ```bash
   cd backend
   alembic downgrade -1
   ```
2. Restore the application to a compatible version.
3. Verify data integrity and application health.

## Backup and Recovery

Before running migrations, take a database backup:

```bash
scripts/backup/backup-db.sh
```

To recover:

1. Restore from the latest backup.
2. Re-run migrations to the target version if needed.
3. Validate data and application health checks.
