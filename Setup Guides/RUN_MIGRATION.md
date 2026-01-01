# Run Database Migration

## Quick Run

```bash
# Option 1: Use the script
./run_migration.sh

# Option 2: Run manually
source venv/bin/activate
alembic upgrade head
```

## What This Does

This will create all 9 database tables:
1. booster_boxes
2. tcg_listings_raw
3. tcg_box_metrics_daily
4. ebay_sales_raw
5. ebay_box_metrics_daily
6. box_metrics_unified
7. tcg_listing_changes
8. users
9. user_favorites

## Verify Success

After running, verify:

```bash
# Check current migration version
alembic current

# Should show: 001 (head)
```

---

**Run the migration, then we'll proceed to Step 4!**

