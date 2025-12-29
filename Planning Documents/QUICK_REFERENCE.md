# BoosterBoxPro - Quick Reference Guide

## Core Metrics Formulas

### 1. Visible Market Cap
```
visible_market_cap = Σ(listing.price × listing.quantity) for all active listings
floor_price = MIN(listing.price) for all active listings
```

### 2. Daily Volume USD (PRIMARY SIGNAL)
```
For each listing change of type DELISTED or QUANTITY_DECREASED:
  units_sold = previous_quantity - new_quantity (or previous_quantity if DELISTED)
  sale_amount = units_sold × price_at_time_of_sale

daily_volume_usd = Σ(sale_amount) for all sales on that day
```

**EMA Calculation:**
```
EMA(today) = (daily_volume_today × multiplier) + (EMA(yesterday) × (1 - multiplier))
where multiplier = 2 / (period + 1)
For 7-day EMA: multiplier = 2 / 8 = 0.25
```

**SMA Calculation:**
```
SMA(30) = Σ(daily_volume) for last 30 days / 30
```

### 3. Boxes Sold Per Day
```
boxes_sold_per_day = total_units_sold_today
boxes_sold_30d_avg = Σ(units_sold) for last 30 days / 30
```

### 4. Supply Inflow
```
boxes_added_today = 
  Σ(new_listing.quantity) + 
  Σ(quantity_increase.new_quantity - quantity_increase.previous_quantity)

EMA calculated same as volume EMA
```

### 5. Days to +20% Price Increase
```
active_boxes = Σ(listing.quantity) for all active listings
boxes_needed_to_clear = active_boxes × 0.85
boxes_sold_per_day = boxes_sold_30d_avg  (use 30-day average)

days_to_20pct = boxes_needed_to_clear / boxes_sold_per_day
  (if boxes_sold_per_day == 0, return NULL)
```

---

## Ranking Logic

### Primary Sort: Volume 7-Day EMA
```
Rank = ORDER BY volume_7d_ema DESC
```

### Secondary Sort: Market Cap (alternative)
```
Rank = ORDER BY visible_market_cap_usd DESC
```

### Tie-Breaking (in order):
1. Higher `boxes_sold_per_day` → higher rank
2. Lower `days_to_20pct` → higher rank  
3. Lower `reprint_risk` (LOW < MEDIUM < HIGH) → higher rank

### Rank Change Calculation
```
rank_change = previous_rank - current_rank
  +1 = moved up
  0  = same
  -1 = moved down
```

---

## Listing Change Detection

### Change Types & Logic

| Change Type | Detection Criteria | Counts as Sale? | Counts as Supply? |
|------------|-------------------|-----------------|-------------------|
| `LISTED` | listing_id not in previous snapshot | No | Yes (add quantity) |
| `DELISTED` | listing_id in previous, not in current | Yes (full quantity) | No |
| `QUANTITY_DECREASED` | listing_id exists, quantity decreased | Yes (delta) | No |
| `QUANTITY_INCREASED` | listing_id exists, quantity increased | No | Yes (delta) |
| `PRICE_CHANGED` | listing_id exists, price different | No | No |
| `RELISTED` | listing_id disappeared, reappeared after >24h | Depends (see below) | Yes (add quantity) |

### Relist Detection Logic
```
IF listing_id disappeared AND reappeared within 24 hours:
  IF same seller_id:
    → Mark as RELISTED, DON'T count as sale
  ELSE:
    → Mark as RELISTED, count as sale (likely legitimate transfer)
ELSE:
  → Mark as new LISTED (gap > 24h)
```

---

## Data Quality Thresholds

### Minimum Requirements for Display
- `active_listings_count >= 3` (below this, show liquidity warning)
- At least 7 days of data for `days_to_20pct` calculation
- If `active_listings_count < 5`, `days_to_20pct` may be unreliable → return NULL

### Floor Price Calculation
```
Option 1 (recommended): 
  floor_price = 5th_percentile of all listing prices
  
Option 2:
  floor_price = average of bottom 3 listing prices
  
Option 3 (simplest):
  floor_price = MIN(listing.price)
```

---

## API Endpoints Summary

**Note:** All endpoints work for both mobile app and website. Mobile-first design.

### Public Endpoints

| Endpoint | Method | Purpose | Sort Options | Auth Required |
|----------|--------|---------|--------------|---------------|
| `/api/v1/booster-boxes` | GET | List top boxes | `volume`, `market_cap`, `floor_price`, etc. | No (favorite status if auth) |
| `/api/v1/booster-boxes/{id}` | GET | Single box details | N/A | No (favorite status if auth) |
| `/api/v1/booster-boxes/{id}/time-series` | GET | Historical metrics | N/A | No |

### Authentication Endpoints

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/v1/auth/register` | POST | Register new user | No |
| `/api/v1/auth/login` | POST | Login (get JWT token) | No |
| `/api/v1/users/me` | GET | Get current user info | Yes |

### Favorites Endpoints (Authenticated)

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/v1/users/me/favorites` | GET | Get my list of favorited boxes | Yes |
| `/api/v1/users/me/favorites/{id}` | POST | Add favorite | Yes |
| `/api/v1/users/me/favorites/{id}` | DELETE | Remove favorite | Yes |
| `/api/v1/users/me/favorites/{id}` | GET | Check favorite status | Yes |

### Query Parameters

**List Endpoint:**
- `sort`: `volume` (default) or `market_cap`
- `limit`: number of results (default: 10, max: 100)
- `date`: specific date to query (default: latest)

**Time Series Endpoint:**
- `metric`: `volume`, `market_cap`, `boxes_sold`, etc.
- `days`: number of days (default: 30, max: 365)

---

## Ingestion Job Schedule

```
Daily at 02:00 UTC:
  1. For each tracked booster_box:
     a. Fetch current listings from marketplace API
     b. Load previous day's snapshot
     c. Compare and detect changes
     d. Store new snapshot
     e. Store listing_changes
  2. Trigger metrics calculation job
  3. Calculate metrics for all boxes with new snapshots
  4. Update rankings
```

---

## Database Index Strategy

### Critical Indexes
1. `listing_snapshots(booster_box_id, snapshot_date)` - Fast snapshot lookups
2. `daily_derived_metrics(volume_7d_ema DESC)` - Ranking queries
3. `daily_derived_metrics(visible_market_cap_usd DESC)` - Market cap ranking
4. `listing_changes(booster_box_id, change_date)` - Volume calculations
5. `booster_boxes(external_product_id)` - Marketplace ID lookups

### Partitioning (Future)
Consider partitioning `listing_snapshots` and `listing_changes` by `snapshot_date` / `change_date` after 90 days to manage storage.

---

## Testing Scenarios

### Unit Test Cases Needed

1. **Volume Calculation:**
   - Single sale (DELISTED)
   - Partial sale (QUANTITY_DECREASED)
   - Multiple sales same day
   - No sales (zero volume)

2. **EMA Calculation:**
   - First day (no previous EMA)
   - Normal progression
   - Zero volume days

3. **Days to 20%:**
   - Normal case
   - Zero demand (infinite days → NULL)
   - Very high demand (days < 1)

4. **Ranking:**
   - Tie-breaking logic
   - Rank change calculation
   - New boxes (no previous rank)

5. **Edge Cases:**
   - Relist detection
   - Low liquidity sets
   - Missing historical data
   - Price floor with single listing

---

## Key Decision Points

Before coding, confirm:

1. ✅ **Marketplace Integration:** Which API(s) first?
2. ✅ **Floor Price Method:** Percentile vs min vs average?
3. ✅ **Relist Window:** 24 hours? Different threshold?
4. ✅ **Data Retention:** How long to keep raw snapshots?
5. ✅ **Reprint Risk:** Manual admin or community-driven?
6. ✅ **Multi-Marketplace:** Aggregate or separate?

---

## Performance Considerations

### Query Optimization
- Use window functions for ranking (efficient)
- Pre-calculate EMAs (don't calculate on-the-fly)
- Cache top 10 results (update after daily job)

### Scalability
- Batch processing for metrics calculation
- Consider materialized views for rankings
- Partition large tables by date

### Monitoring
- Track ingestion job duration
- Alert on API failures
- Monitor calculation job performance
- Track data quality metrics (missing days, gaps)


