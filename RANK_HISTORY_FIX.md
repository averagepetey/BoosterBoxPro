# Fix Rank History Display - Step by Step

## Problem
No boxes are showing rank history in the frontend. The chart shows "No rank history available".

## Root Cause
Ranks haven't been calculated for historical dates. The database has metrics data going back to April, but ranks are only calculated for December 2025.

## Solution

### Step 1: Check Current State
Run this to see if ranks exist:
```bash
python scripts/quick_rank_check.py
```

This will show:
- How many metrics have ranks
- How many boxes have ranks
- Whether you need to run the backfill

### Step 2: Calculate Ranks for All Historical Dates
Run the backfill script to calculate ranks for ALL dates that have metrics data:
```bash
python scripts/backfill_historical_ranks.py
```

This will:
- Find all dates with metrics data (from April onwards)
- Calculate ranks for each date
- Store ranks in the database
- Process all boxes that have volume data

**Expected output:**
```
Processing X dates from 2025-04-01 to 2025-12-30
[1/X] Processing 2025-04-01... Ranked Y boxes, updated Y
[2/X] Processing 2025-04-02... Ranked Y boxes, updated Y
...
✅ Historical ranks backfilled successfully!
```

### Step 3: Verify Ranks Were Calculated
Run the check again:
```bash
python scripts/quick_rank_check.py
```

You should now see:
- ✅ Ranks are calculated!
- All boxes should have ranks

### Step 4: Test a Specific Box
Test if a box has rank history:
```bash
python scripts/backfill_historical_ranks.py --box-id <BOX_UUID>
```

Replace `<BOX_UUID>` with an actual box ID. This will show the rank history for that box.

### Step 5: Refresh Frontend
1. Make sure your backend server is running
2. Refresh your browser
3. Navigate to any box detail page
4. The rank history chart should now show data

## Debugging

If ranks are calculated but still not showing:

### Check Browser Console
Open browser DevTools (F12) and look for:
- `useBoxRankHistory: Fetching rank history for ID: ...`
- `getBoxRankHistory: Response data: ...`
- Any errors in red

### Check Network Tab
1. Open DevTools → Network tab
2. Navigate to a box detail page
3. Look for request to `/booster-boxes/{id}/rank-history`
4. Check:
   - Status code (should be 200)
   - Response body (should have `{"data": [...]}`)
   - Response size (should be > 0 if data exists)

### Check Backend Logs
Look for these log messages in your backend terminal:
```
Rank history endpoint: box_id=... returned X entries
  First entry: {'date': '...', 'rank': ...}
  Last entry: {'date': '...', 'rank': ...}
```

If you see `Box has X total metrics, 0 with ranks`, ranks haven't been calculated for that box.

## Expected Result

After running the backfill:
- **Romance Dawn**: Rank history from April (when tracking started)
- **OP-13**: Rank history from October/November (when first tracked)
- **All boxes**: Rank history from their first tracked date

Each box's rank history graph will show:
- X-axis: Dates (from first tracked date to present)
- Y-axis: Rank (lower = better)
- Line chart showing rank changes over time

## Common Issues

### Issue: "No metrics data found in database"
**Solution**: Make sure you have metrics data. Check with:
```bash
python scripts/check_rank_data.py
```

### Issue: Backfill script runs but no ranks appear
**Solution**: Check if boxes have `unified_volume_7d_ema` data (required for ranking). Ranks are only calculated for boxes with volume data.

### Issue: Frontend shows "No rank history" even after backfill
**Solution**: 
1. Check browser console for errors
2. Verify backend is running
3. Check Network tab for API response
4. Verify the response format matches `{"data": [{"date": "...", "rank": ...}]}`

