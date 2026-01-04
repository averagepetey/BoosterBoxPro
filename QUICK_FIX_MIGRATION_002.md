# Quick Fix: Add Migration 002 Columns

## Problem
Database is missing columns from migration 002, but model expects them.

## Solution

Run this Python script to add the columns:

```bash
python scripts/add_migration_002_columns.py
```

Then mark migration 002 as complete:

```bash
alembic stamp 002
```

Then upgrade to head (will run migration 003):

```bash
alembic upgrade head
```

## What This Does

1. Adds missing columns:
   - `unified_volume_30d_sma`
   - `volume_mom_change_pct`
   - `avg_boxes_added_per_day`

2. Marks migration 002 as complete

3. Runs migration 003 (adds ranking fields)

This is the simplest approach - no downgrade needed!

