# Fix: Alembic Database URL

## Issue

Alembic requires a synchronous database connection, but our database URL uses `postgresql+asyncpg://` (async driver).

## Solution

I've updated `migrations/env.py` to automatically convert the async URL to sync URL for Alembic migrations.

However, you need to install `psycopg2-binary` (the sync PostgreSQL driver):

```bash
source venv/bin/activate
pip install psycopg2-binary
```

## Then Run Migration

```bash
alembic upgrade head
```

---

**The `requirements.txt` has been updated to include `psycopg2-binary`, so you may need to install it if it wasn't installed before.**

