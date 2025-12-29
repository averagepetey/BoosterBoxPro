# Test Migration Setup

Run this to verify everything is configured correctly:

```bash
source venv/bin/activate
python scripts/test_migration_setup.py
```

This will check:
- ✅ Settings import works
- ✅ Database URL conversion for Alembic
- ✅ Models can be imported
- ✅ psycopg2 (sync driver) is available
- ✅ env.py has correct configuration

If all tests pass, you can proceed with:
```bash
alembic upgrade head
```

