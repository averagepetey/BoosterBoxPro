# Phase 1 Roadmap & Next Steps

## ✅ Completed

1. ✅ Database setup, migrations, and SQLAlchemy models
2. ✅ Admin endpoints: box creation, metrics entry (single & bulk)
3. ✅ 13 One Piece booster boxes registered (OP-01 through OP-13)

---

## 🎯 Immediate Next Step (When Data Arrives)

**Enter Sample Metrics Data:**
- 7-14 days of metrics for each of the 13 boxes
- Use bulk endpoint: `POST /api/v1/admin/manual-metrics/bulk`
- Verify data in database (~91-182 metric records)

---

## 🔨 What to Build While Waiting for Data

### Priority 1: Metrics Calculation Service
**Build Now:** `app/services/ema_calculator.py` & `app/services/metrics_calculator.py`
- Calculate 7-day EMA, 30-day SMA
- Calculate liquidity score, absorption rate, expected days to sell
- **Can test with mock data**

### Priority 2: Public API Endpoints
**Build Now:** `app/routers/booster_boxes.py` + response schemas
- `GET /api/v1/booster-boxes` - Leaderboard
- `GET /api/v1/booster-boxes/{id}` - Box detail
- `GET /api/v1/booster-boxes/{id}/time-series` - Time-series
- `GET /api/v1/booster-boxes/{id}/sparkline` - Sparkline
- **Will return empty data until real data exists**

### Priority 3: Leaderboard Service
**Build Now:** `app/services/leaderboard_service.py`
- Ranking/sorting logic (volume, liquidity, price change)
- Rank change calculations
- Pagination support

### Priority 4: Repository Query Methods
**Build Now:** Add to existing repositories
- Get latest metrics for all boxes (leaderboard)
- Get metrics for box/date range
- Get time-series and sparkline data

---

## 📋 Build Order (12 Hours)

1. **EMA Calculator** (1-2 hours) → Metrics Service (2-3 hours)
2. **Response Schemas** (1 hour) - Match OpenAPI spec
3. **Repository Query Methods** (1-2 hours)
4. **Leaderboard Service** (1-2 hours)
5. **Public API Endpoints** (2-3 hours)

---

## 🎯 End Goal

When data arrives:
- ✅ Enter data via bulk endpoint
- ✅ Run metrics calculations
- ✅ Test public endpoints with real data
- ✅ Verify Phase 1 complete (13 boxes + sample metrics)
- ✅ Proceed to Phase 2

