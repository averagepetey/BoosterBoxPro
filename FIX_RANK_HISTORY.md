# Fix Rank History - Checklist

## Current Status
Frontend shows "No rank history available" even though ranks exist in database.

## Steps to Debug

### 1. Check Backend Logs
When you view a box detail page, check your backend terminal/logs. You should see:
```
Rank history endpoint: box_id=..., returned X entries
```

If you see:
```
Box has X total metrics, 0 with ranks
```
Then ranks haven't been calculated for that box yet.

### 2. Run Diagnostic Script
```bash
python scripts/check_rank_data.py
```

This shows:
- How many metrics have ranks (64 out of 100 = 64%)
- Which boxes have ranks

### 3. Test Specific Box
```bash
python scripts/debug_rank_endpoint.py
```

This will:
- Find a box that has ranks
- Test the rank history service directly
- Show what data is returned

### 4. Backfill Ranks (if needed)
If boxes don't have ranks:
```bash
python scripts/backfill_historical_ranks.py
```

### 5. Check Browser Console
Open browser DevTools (F12) and check:
- Console tab for errors
- Network tab to see the API call to `/booster-boxes/{id}/rank-history`
- Check the response - is it returning data or empty array?

### 6. Common Issues

**Issue**: Endpoint returns empty array `{"data": []}`
- **Cause**: Box doesn't have ranks calculated yet
- **Fix**: Run backfill script

**Issue**: Network error or 404
- **Cause**: Backend not running or endpoint not found
- **Fix**: Check backend is running on port 8000

**Issue**: Data returned but frontend shows "No rank history available"
- **Cause**: Frontend parsing issue or data format mismatch
- **Fix**: Check browser console for errors, verify data format matches `[{date: string, rank: number}]`

## Expected Behavior

For monthly data:
- Each box's rank history starts from its first tracked month
- Romance Dawn: starts from earliest date
- OP-13: starts from October/November when first tracked
- One rank per month per box

The endpoint now:
- ✅ Always returns all available data (no date filtering)
- ✅ Starts from first date box has data
- ✅ Includes detailed logging for debugging

