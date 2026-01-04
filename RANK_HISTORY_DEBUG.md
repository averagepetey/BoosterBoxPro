# Rank History Debugging

## Issue
Rank history chart shows "No rank history available" even though ranks exist in database.

## Solution Applied
Changed the endpoint to **always return all available data** regardless of the `days` parameter. This is necessary because:

1. **Data is logged monthly** - Each box has one data point per month
2. **Graphs should start from first tracked date** - Each box's graph should start when that box was first tracked
3. **30-day filter excludes older monthly data** - If a box started tracking 3 months ago, a 30-day filter would exclude those monthly data points

## Changes Made

The endpoint now:
- Always returns all available rank history (ignores `days` parameter for monthly data)
- Starts from the first date the box has data
- Frontend can filter client-side if needed, but server returns full history

## Testing

To verify rank data exists and the endpoint works:

```bash
python scripts/debug_rank_endpoint.py
```

This will:
- Find boxes that have ranks
- Test the rank history service directly
- Show which boxes have rank data and their date ranges

## Next Steps

1. **Refresh the browser** - The endpoint should now return all rank history
2. **Check browser console** - Look for any API errors
3. **Check backend logs** - Look for the debug log: "Rank history endpoint: box_id=..., returned X entries"
4. **Verify ranks exist** - Run the debug script to confirm boxes have rank data

## If Still No Data

1. **Check if ranks exist**: Run `python scripts/check_rank_data.py`
2. **Backfill ranks if needed**: Run `python scripts/backfill_historical_ranks.py`
3. **Check specific box**: Run `python scripts/debug_rank_endpoint.py` to see which boxes have ranks
4. **Check browser console**: Look for API errors or network issues

