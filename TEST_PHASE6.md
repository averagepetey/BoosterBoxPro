# Testing Phase 6: Rankings & Caching

## Quick Test

Run the comprehensive test script:

```bash
python scripts/test_phase6.py
```

This will test:
1. ✅ Database connection
2. ✅ Metrics data availability
3. ✅ Ranking calculation
4. ✅ Rank updates in database
5. ✅ Rank change detection
6. ✅ Cache service (if Redis is available)

## Individual Tests

### Test Ranking Calculation
```bash
python scripts/calculate_ranks.py
```

### Test Ranking Script (Alternative)
```bash
python scripts/test_ranking.py
```

## Expected Results

If you have metrics data:
- ✅ Ranks calculated successfully
- ✅ Ranks updated in database
- ✅ Rank changes calculated (may be 0 if no previous data)

If no metrics data:
- ⚠️  Will show message that no data found
- Add metrics data first using screenshot system

## Cache Service

The cache service will:
- ✅ Work with Redis if available
- ✅ Continue without cache if Redis unavailable (graceful fallback)
- ✅ Print status in test output

