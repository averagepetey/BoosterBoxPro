# Run Migration 002

## Issue
The database is missing columns from migration 002 (`unified_volume_30d_sma`, `volume_mom_change_pct`, `avg_boxes_added_per_day`), but the model expects them.

Migration 002 has been updated to check if columns exist before adding them, so it's safe to run.

## Solution

Since you're currently at migration 003, you need to:

1. **Downgrade to 001:**
   ```bash
   alembic downgrade 001
   ```

2. **Then upgrade to head (will run 002, then 003):**
   ```bash
   alembic upgrade head
   ```

This will:
- Run migration 002 (adds the missing columns)
- Run migration 003 (adds ranking fields, which should skip if they already exist)

## Alternative: Direct Approach

If you prefer, you can manually add the columns via SQL first, then run migrations:

```sql
ALTER TABLE box_metrics_unified 
ADD COLUMN IF NOT EXISTS unified_volume_30d_sma NUMERIC(12, 2),
ADD COLUMN IF NOT EXISTS volume_mom_change_pct NUMERIC(6, 2),
ADD COLUMN IF NOT EXISTS avg_boxes_added_per_day NUMERIC(8, 2);
```

Then:
```bash
alembic stamp 002
alembic upgrade head
```

## Recommended Approach

**Option 1 (Downgrade/Upgrade)** is recommended as it ensures all migrations run properly.

