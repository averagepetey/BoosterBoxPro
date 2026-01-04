# Fix Migration Error: Can't locate revision '004'

## Error
```
ERROR [alembic.util.messaging] Can't locate revision identified by '004'
  FAILED: Can't locate revision identified by '004'
```

## Problem
The database is looking for revision '004', but only migrations '001' and '002' exist in the codebase.

## Solution Steps

### Step 1: Check Current Database State
```bash
alembic current
```

This will show what revision the database thinks it's at.

### Step 2: Fix Based on Current State

#### If database is at '003' (expects '004'):
The database thinks there should be a migration '004' after '003', but it doesn't exist.

**Option A: Stamp to '002' (if safe to do so)**
```bash
alembic stamp 002
alembic upgrade head
```

**Option B: Create stub migration '003' and '004'**
This is only needed if migrations '003' and '004' actually existed and were deleted.

#### If database is at '004':
The database thinks it's already at '004', but the migration file doesn't exist.

**Solution: Stamp to '002'**
```bash
alembic stamp 002
alembic upgrade head
```

#### If database is at '002' or earlier:
This shouldn't cause the error, but if it does, just run:
```bash
alembic upgrade head
```

## Current Migration Files
- `001_initial_schema.py` (revision: '001', down_revision: None)
- `002_add_missing_metrics.py` (revision: '002', down_revision: '001')

## Recommended Action

1. Run `alembic current` to see the current state
2. If the database is at an unexpected revision, use `alembic stamp 002` to set it to revision '002'
3. Then run `alembic upgrade head` to apply any pending migrations

## Note
If you're in development and the database state is incorrect, using `alembic stamp` is safe. This just tells Alembic what revision the database schema matches, without running migrations.

