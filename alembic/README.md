# Alembic Migrations

Use the Alembic CLI to create and run database migrations.

```bash
alembic revision -m "create users table"
alembic upgrade head
```

The configuration pulls the database URL from the `DATABASE_URL` environment variable (falling back to the default defined in `src/shared/main/config/database.py`).
