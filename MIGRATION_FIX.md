# Migration Fix: Revision '004' Not Found

## Problem
The database is looking for revision '004', but only migrations '001' and '002' exist.

## Solution Options

### Option 1: Check Current Database State
Run this to see what revision the database thinks it's at:
```bash
alembic current
```

### Option 2: If Database is at '003'
If the database is at revision '003', we need to create migration '003' or update the database state.

Check if there's a migration '003' file that was deleted, or if the database state is incorrect.

### Option 3: Reset Database State (if safe)
If you're in development and can reset the database:

1. Check current state:
   ```bash
   alembic current
   ```

2. If it's safe to reset, stamp the database to revision '002':
   ```bash
   alembic stamp 002
   ```

3. Then run upgrade:
   ```bash
   alembic upgrade head
   ```

### Option 4: Create Missing Migration
If revision '003' and '004' should exist but are missing, we need to create them. However, since we only created '002', this is unlikely.

## Recommended Action
1. First, check what revision the database is currently at: `alembic current`
2. Check if there are any other migration files that might have been deleted
3. If the database is at an unexpected state, use `alembic stamp` to correct it

## Current Migration Chain
- 001: Initial schema (down_revision: None)
- 002: Add missing metrics (down_revision: 001)

The database expects '004', which suggests there might have been migrations '003' and '004' that were removed, or the database state is incorrect.

