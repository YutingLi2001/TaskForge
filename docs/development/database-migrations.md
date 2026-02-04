# Database Migrations (Alembic)

This project uses Alembic to version database schema changes.

## Prerequisites

- Ensure `DATABASE_URL` is set for your environment.
- For Docker dev, migrations run automatically on container startup.

## Generate a Migration

1. Update SQLAlchemy models in `backend/app/models/`.
2. Generate the migration:

```bash
cd backend
alembic revision --autogenerate -m "Describe change"
```

3. Review the generated file in `backend/alembic/versions/` and adjust if needed.

## Apply Migrations

```bash
cd backend
alembic upgrade head
```

## Roll Back Migrations

```bash
cd backend
alembic downgrade -1
```

## Review Checklist

- Verify new tables/columns are correct (types, nullability, indexes).
- Ensure foreign keys and cascade rules are correct.
- Confirm downgrade() reverses the upgrade() safely.

## Common Issues

### Autogenerate doesn't detect changes

- Confirm all models are imported in `backend/app/models/__init__.py`.
- Ensure `target_metadata = Base.metadata` in `backend/alembic/env.py`.

### SQLite dev/test quirks

- Some ALTER TABLE operations require batch mode (`render_as_batch=True`).
- Prefer new migrations over editing existing ones.
