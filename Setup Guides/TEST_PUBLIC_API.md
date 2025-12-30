# Testing Public API Endpoints

## Quick Test Guide

The FastAPI server is running and endpoints are ready to test!

### 1. Interactive API Documentation

Visit the auto-generated Swagger UI:
```
http://localhost:8000/docs
```

This provides an interactive interface to test all endpoints.

### 2. Test Endpoints Manually

#### Leaderboard Endpoint
```bash
# Get top 10 boxes (default sort by volume)
curl "http://localhost:8000/api/v1/booster-boxes?limit=10"

# Sort by liquidity score
curl "http://localhost:8000/api/v1/booster-boxes?sort=liquidity_score&limit=5"

# Sort by floor price
curl "http://localhost:8000/api/v1/booster-boxes?sort=floor_price_usd&limit=5"

# Get for specific date
curl "http://localhost:8000/api/v1/booster-boxes?date=2024-01-15&limit=10"
```

#### Box Detail Endpoint
```bash
# Get detail for a specific box (replace {box_id} with actual UUID)
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}"

# With specific date
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}?date=2024-01-15"
```

#### Time-Series Endpoint
```bash
# Get last 30 days of data
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}/time-series"

# Custom date range
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}/time-series?start_date=2024-01-01&end_date=2024-01-31"
```

#### Sparkline Endpoint
```bash
# Get 7-day sparkline (default)
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}/sparkline"

# Get 30-day sparkline
curl "http://localhost:8000/api/v1/booster-boxes/{box_id}/sparkline?days=30"
```

### 3. Using Python Script

Run the test script:
```bash
source venv/bin/activate
python scripts/test_public_endpoints.py
```

### 4. Expected Behavior

#### Before Data Entry
- Endpoints return valid responses (status 200)
- Leaderboard returns empty array or boxes without metrics
- Detail endpoints may return 404 if no metrics exist
- This is expected behavior - endpoints are working correctly

#### After Data Entry
- Leaderboard returns ranked boxes
- Box detail shows full analytics
- Time-series and sparkline data available
- Rank changes calculated correctly

### 5. Testing Checklist

- [x] Server is running (`/health` returns 200)
- [ ] Leaderboard endpoint responds (`/api/v1/booster-boxes`)
- [ ] Leaderboard supports sorting (volume, liquidity, price)
- [ ] Box detail endpoint responds (`/api/v1/booster-boxes/{id}`)
- [ ] Time-series endpoint responds (`/api/v1/booster-boxes/{id}/time-series`)
- [ ] Sparkline endpoint responds (`/api/v1/booster-boxes/{id}/sparkline`)
- [ ] All endpoints return valid JSON
- [ ] Error handling works (404 for missing boxes)

### 6. Getting a Box ID

To get a box ID for testing detail endpoints:

```bash
# Get list of boxes
curl "http://localhost:8000/api/v1/admin/boxes" \
  -H "X-API-Key: your-admin-key"

# Or from leaderboard
curl "http://localhost:8000/api/v1/booster-boxes?limit=1" | jq '.data[0].id'
```

### 7. Example Response

**Leaderboard Response:**
```json
{
  "data": [
    {
      "id": "uuid-here",
      "rank": 1,
      "rank_change_direction": "up",
      "rank_change_amount": 2,
      "product_name": "One Piece - OP-01 Romance Dawn Booster Box",
      "set_name": "Romance Dawn",
      "metrics": {
        "floor_price_usd": 245.99,
        "unified_volume_7d_ema": 45230.50,
        "liquidity_score": 0.75
      }
    }
  ],
  "meta": {
    "total": 13,
    "sort": "unified_volume_7d_ema",
    "sort_direction": "desc"
  }
}
```

### 8. Troubleshooting

**Server not running?**
```bash
python scripts/run_server.py
# or
uvicorn app.main:app --reload
```

**404 on box detail?**
- Box may not have metrics yet
- Verify box ID is correct
- Check that metrics have been entered for that box

**Empty leaderboard?**
- This is expected if no metrics data has been entered
- Use admin endpoints to add metrics first

### 9. Next Steps

1. ✅ Endpoints are built and responding
2. ⏭️ Enter metrics data (via Excel import or bulk endpoint)
3. ⏭️ Verify ranking and calculations work correctly
4. ⏭️ Test with frontend integration

