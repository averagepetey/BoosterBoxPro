# Fix Migration 002 Issue

## Problem
The database is missing columns from migration 002 (`unified_volume_30d_sma`, `volume_mom_change_pct`, `avg_boxes_added_per_day`), but the model expects them.

## Solution

You need to run migration 002. However, since migration 003 was already stamped, you may need to:

### Option 1: Run Migration 002 (Recommended)
Downgrade to 001, then upgrade through all migrations:

```bash
# Check current state
alembic current

# If at 003, downgrade to 001
alembic downgrade 001

# Then upgrade to head (will run 002, then 003)
alembic upgrade head
```

### Option 2: Manually Add Columns
If migrations are complex, you can manually add the columns via SQL:

```sql
ALTER TABLE box_metrics_unified 
ADD COLUMN IF NOT EXISTS unified_volume_30d_sma NUMERIC(12, 2),
ADD COLUMN IF NOT EXISTS volume_mom_change_pct NUMERIC(6, 2),
ADD COLUMN IF NOT EXISTS avg_boxes_added_per_day NUMERIC(8, 2);
```

Then stamp migration 002:
```bash
alembic stamp 002
```

Then upgrade to 003 (should skip since columns already exist):
```bash
alembic upgrade head
```

### Option 3: Check Migration Status
First check what's actually in the database vs what migrations say:

```bash
alembic current
alembic history
```

Then decide the best approach.

