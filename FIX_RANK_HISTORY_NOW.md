# Fix Rank History - Action Plan

## Current Issue
No boxes are showing rank history in the frontend.

## Root Cause
Ranks haven't been calculated for the historical dates. The diagnostic showed:
- Ranks exist for 24 dates (December 7-30, 2025)
- But you mentioned data goes back to April
- This means ranks need to be calculated for ALL historical dates

## Solution: Run Backfill Script

**Step 1: Check which boxes have ranks**
```bash
python scripts/check_all_boxes_ranks.py
```

This will show:
- Which boxes have ranks calculated
- Which boxes don't have ranks
- How many rank history entries each box has

**Step 2: Calculate ranks for all historical dates**
```bash
python scripts/backfill_historical_ranks.py
```

This will:
- Find ALL dates that have metrics data (from April onwards)
- Calculate ranks for each date
- Store ranks in the database
- Process all boxes that have volume data

**Step 3: Verify ranks were calculated**
```bash
python scripts/check_all_boxes_ranks.py
```

You should now see all boxes with ranks.

**Step 4: Refresh the frontend**
- The rank history graphs should now show data
- Each box will show ranks starting from when it was first tracked

## Expected Result

After backfilling:
- Romance Dawn: Rank history from April (when tracking started)
- OP-13: Rank history from October/November (when first tracked)
- All boxes: Rank history from their first tracked date

## If Still Not Working

1. **Check backend logs** - Look for:
   ```
   Rank history endpoint: box_id=..., returned X entries
   ```
   
2. **Check browser console** - Look for errors or the logs we added:
   ```
   useBoxRankHistory: Rank history received: ...
   ```

3. **Check Network tab** - Look at the `/rank-history` request:
   - Status code should be 200
   - Response should have `{"data": [...]}` format
   - Check if data array is empty or has entries

4. **Verify endpoint is registered** - The endpoint should be at:
   ```
   GET /booster-boxes/{box_id}/rank-history
   ```

## Quick Test

Test a specific box:
```bash
python scripts/check_endpoint_response.py
```

This simulates what the endpoint returns for Romance Dawn.

