# Rank History Setup Guide

## Issue: "No rank history available"

The rank history graph shows "No rank history available" because:

1. **Ranks haven't been calculated yet** - The `current_rank` field in the database needs to be populated
2. **Historical ranks need to be backfilled** - For each date where a box has metrics data, we need to calculate and store the rank

## Solution: Backfill Historical Ranks

### Step 1: Calculate ranks for all historical dates

Run the backfill script to calculate ranks for all dates that have metrics data:

```bash
python scripts/backfill_historical_ranks.py
```

This script will:
- Find all dates that have metrics data in the database
- Calculate ranks for each date based on `unified_volume_7d_ema`
- Update the `current_rank` field in `UnifiedBoxMetrics` for each date
- Only rank boxes that have data for that date (boxes don't appear in rankings until they have data)

### Step 2: Verify ranks were calculated

Check if ranks exist for a specific box:

```bash
python scripts/backfill_historical_ranks.py --box-id <box-uuid>
```

Or query the database directly:
```sql
SELECT metric_date, current_rank 
FROM box_metrics_unified 
WHERE booster_box_id = '<box-uuid>' 
  AND current_rank IS NOT NULL
ORDER BY metric_date;
```

### Step 3: The API endpoint behavior

The endpoint `/booster-boxes/{box_id}/rank-history` now:
- Returns **all available rank history** by default (starting from first date with data)
- The `days` parameter is optional - if not provided, returns all data
- Only includes dates where `current_rank` is not NULL (box has data)
- Automatically starts from the first date the box has data (no fixed start date)

### How it works

1. **Rank Calculation**: Ranks are based on `unified_volume_7d_ema` (higher volume = better rank = lower number)
2. **Data Availability**: Only boxes with metrics data are ranked
3. **Historical Data**: Each date's rank is stored in `current_rank` field
4. **Graph Display**: Frontend displays rank history starting from the first date with data

### Example Response

```json
{
  "data": [
    {"date": "2024-12-01", "rank": 5},
    {"date": "2024-12-02", "rank": 4},
    {"date": "2024-12-03", "rank": 3},
    ...
  ]
}
```

The graph will show ranks starting from "2024-12-01" (the first date this box had data), not from a fixed date like "30 days ago".

---

## Next Steps

1. Run the backfill script to calculate all historical ranks
2. Refresh the frontend - the rank history graph should now show data
3. The graph will automatically start from the first date the box has data

