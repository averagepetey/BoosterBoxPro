# Step 3: Database Schema Setup - Instructions

## Initial Alembic Setup

Alembic has been initialized manually. You need to run these commands to complete the setup:

### 1. Initialize Alembic (if not already done)

```bash
source venv/bin/activate
alembic init migrations
```

**Note:** If you get an error that migrations already exists, that's fine - we've created it manually.

### 2. Verify Alembic Setup

```bash
# Check Alembic can find your configuration
alembic current
```

You should see: `INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.`

### 3. Create Initial Migration

The migration files will be created in the next step. For now, verify everything is working:

```bash
# Check Alembic can connect to database
alembic current
```

---

## Next: Create Migration Files

After verifying Alembic is working, we'll create the actual migration files for all tables.

