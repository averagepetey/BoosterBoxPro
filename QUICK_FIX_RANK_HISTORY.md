# Quick Fix: Rank History Showing "No Data Available"

## Problem
The rank history chart shows "No rank history available" even though metrics data exists.

## Root Cause
The `current_rank` field in the `box_metrics_unified` table is NULL for all rows because ranks haven't been calculated yet.

## Solution

### Step 1: Check if ranks exist
```bash
python scripts/check_rank_data.py
```

This will show:
- How many metrics records exist
- How many have ranks calculated
- Whether ranks need to be backfilled

### Step 2: Calculate ranks (if needed)
If the diagnostic shows 0 ranks, run:

```bash
python scripts/backfill_historical_ranks.py
```

This will:
- Calculate ranks for all dates that have metrics data
- Store ranks in the `current_rank` field
- Take a few minutes depending on data volume

### Step 3: Verify
After backfilling, check again:
```bash
python scripts/check_rank_data.py
```

You should see ranks populated.

### Step 4: Refresh frontend
Refresh the browser - the rank history chart should now show data starting from the first date the box has data.

## How It Works

1. **Rank Calculation**: Ranks are based on `unified_volume_7d_ema` (higher volume = better rank = lower number)
2. **Data Availability**: Only boxes with metrics data are ranked
3. **Historical Data**: Each date's rank is stored in `current_rank` field
4. **Graph Display**: Frontend displays rank history starting from the first date with data

## Troubleshooting

### Still showing "No rank history available"?

1. **Check backend logs**: Look for errors when calling the endpoint
2. **Check browser console**: Look for API errors
3. **Verify endpoint**: Test the endpoint directly:
   ```bash
   curl http://localhost:8000/booster-boxes/<box-id>/rank-history
   ```
4. **Check database**: Verify ranks exist:
   ```sql
   SELECT COUNT(*) FROM box_metrics_unified WHERE current_rank IS NOT NULL;
   ```

### No metrics data at all?

If the diagnostic shows 0 total metrics, you need to:
1. Add metrics data to the database (via screenshot processing or manual entry)
2. Then run the backfill script

