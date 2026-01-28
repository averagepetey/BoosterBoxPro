# Data Flow Analysis: Scraper → Calculations → Frontend

## ✅ What's Working

### 1. Data Collection
- **Listings Scraper**: Saves `floor_price_usd` and `active_listings_count` (boxes within 20% of floor) → `box_metrics_unified` table ✅
- **Apify Service**: Saves `boxes_sold_per_day`, `unified_volume_usd`, `floor_price_usd` → `box_metrics_unified` table ✅
- **ID Mapping**: Fixed - scraper now writes using leaderboard UUID (matches `booster_boxes.id`) ✅

### 2. Data Reading
- **Box Detail Endpoint**: Reads from `get_box_price_history()` → `get_box_historical_data()` → `box_metrics_unified` ✅
- **Historical Data Service**: Queries DB by box_id (both leaderboard and TCGPlayer UUIDs) ✅

### 3. Frontend Display
- **Box Detail Page**: Displays all metrics from API response ✅
- **Components**: `PriceChart`, `AdvancedMetricsTable` show metrics ✅

## ⚠️ Potential Issues / Gaps

### 1. Missing Calculated Metrics in DB

**Problem**: Some metrics needed for calculations are NOT saved to DB:

- **`boxes_sold_30d_avg`**: 
  - ❌ Apify doesn't save this (only saves `boxes_sold_per_day`)
  - ✅ Box detail endpoint calculates on-the-fly using `get_box_30d_avg_sales()` (averages last 30 days of `boxes_sold_per_day`)
  - **Status**: Should work, but depends on having 30 days of historical data

- **`unified_volume_7d_ema`**:
  - ❌ Apify doesn't save this (only saves `unified_volume_usd` = 30-day volume)
  - ⚠️ Box detail endpoint uses `latest.get("unified_volume_7d_ema")` - will be None if not in DB
  - **Status**: May be missing from frontend display

- **`avg_boxes_added_per_day`**:
  - ❌ Neither Apify nor scraper saves this
  - ⚠️ Box detail endpoint uses `latest.get("avg_boxes_added_per_day") or 0` - defaults to 0
  - **Impact**: `days_to_20pct` calculation uses `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
  - If `avg_boxes_added_per_day` is always 0, `days_to_20pct` may be inaccurate (too optimistic)

### 2. Calculation Dependencies

**Box Detail Endpoint Calculations** (`main.py` lines 722-790):

1. **`days_to_20pct_increase`**:
   - ✅ Uses `active_listings` (from scraper) ✅
   - ✅ Uses `boxes_sold_30d_avg` (calculated on-the-fly) ✅
   - ⚠️ Uses `avg_boxes_added_per_day` (defaults to 0 if not present) ⚠️
   - **Formula**: `active_listings / (boxes_sold_30d_avg - avg_boxes_added_per_day)`
   - **Status**: Will calculate, but may be inaccurate if `avg_boxes_added_per_day` is missing

2. **`liquidity_score`**:
   - ✅ Uses `boxes_sold_30d_avg` (calculated on-the-fly) ✅
   - ✅ Uses `active_listings` (from scraper) ✅
   - **Formula**: `(boxes_sold_30d_avg / active_listings) * 100`
   - **Status**: Should work correctly

3. **`volume_7d`**:
   - ⚠️ Uses `daily_vol = latest.get("daily_volume_usd") or 0`
   - ⚠️ Falls back to `daily_vol * 7` if `volume_7d` not in latest
   - **Status**: May be calculated from daily, not actual 7-day sum

4. **`unified_volume_7d_ema`**:
   - ⚠️ Uses `latest.get("unified_volume_7d_ema")` - will be None if not saved
   - **Status**: May be missing from response

### 3. Data Sources

**What Each Service Saves**:

| Metric | Listings Scraper | Apify | Calculated On-The-Fly |
|--------|------------------|-------|----------------------|
| `floor_price_usd` | ✅ | ✅ | - |
| `active_listings_count` | ✅ | ❌ | - |
| `boxes_sold_per_day` | ❌ | ✅ | - |
| `boxes_sold_30d_avg` | ❌ | ❌ | ✅ (`get_box_30d_avg_sales()`) |
| `unified_volume_usd` | ❌ | ✅ | - |
| `unified_volume_7d_ema` | ❌ | ❌ | ❌ (not calculated) |
| `boxes_added_today` | ❌ | ❌ | - |
| `avg_boxes_added_per_day` | ❌ | ❌ | ❌ (defaults to 0) |

## 🔧 What Needs to Be Done

### Option 1: Calculate Metrics On-The-Fly (Current Approach)
- ✅ `boxes_sold_30d_avg` - Already calculated via `get_box_30d_avg_sales()`
- ⚠️ `unified_volume_7d_ema` - Need to add calculation in box detail endpoint
- ⚠️ `avg_boxes_added_per_day` - Need to add calculation (or accept 0 as default)

### Option 2: Save Calculated Metrics to DB (Better for Performance)
- Add `boxes_sold_30d_avg` calculation to Apify service and save to DB
- Add `unified_volume_7d_ema` calculation to Apify service and save to DB
- Add `avg_boxes_added_per_day` calculation (requires tracking `boxes_added_today`)

## 📋 Recommended Fixes

### Immediate (Ensure Calculations Work):

1. **Add `unified_volume_7d_ema` calculation to box detail endpoint**:
   ```python
   # Calculate 7-day EMA from historical volumes
   if not latest.get("unified_volume_7d_ema"):
       recent_entries = historical_data[-7:] if len(historical_data) >= 7 else historical_data
       volumes = [e.get("unified_volume_usd") or e.get("daily_volume_usd", 0) * 30 
                  for e in recent_entries if e.get("unified_volume_usd") or e.get("daily_volume_usd")]
       if volumes:
           # Calculate EMA
           unified_volume_7d_ema = calculate_ema(volumes, alpha=0.3)
   ```

2. **Add `avg_boxes_added_per_day` calculation**:
   ```python
   # Calculate from historical boxes_added_today
   recent_entries = historical_data[-30:] if len(historical_data) >= 30 else historical_data
   boxes_added_values = [e.get("boxes_added_today", 0) for e in recent_entries 
                         if e.get("boxes_added_today") is not None]
   avg_boxes_added_per_day = sum(boxes_added_values) / len(boxes_added_values) if boxes_added_values else 0
   ```

### Future (Performance Optimization):

3. **Save calculated metrics to DB** (via Apify or separate metrics calculator):
   - Calculate `boxes_sold_30d_avg` and save
   - Calculate `unified_volume_7d_ema` and save
   - Track `boxes_added_today` and calculate `avg_boxes_added_per_day`

## ✅ Verification Checklist

After scraper runs, verify:

- [ ] `active_listings_count` appears in box detail (from scraper)
- [ ] `floor_price_usd` appears in box detail (from scraper)
- [ ] `days_to_20pct_increase` calculates correctly (needs `boxes_sold_30d_avg` and `avg_boxes_added_per_day`)
- [ ] `liquidity_score` calculates correctly (needs `boxes_sold_30d_avg` and `active_listings_count`)
- [ ] `unified_volume_7d_ema` appears in box detail (currently may be None)
- [ ] `volume_7d` appears in box detail (calculated from daily)
- [ ] `unified_volume_usd` appears in box detail (from Apify)

## 🎯 Next Steps

1. **Test current flow**: Run scraper → check box detail page → verify all metrics display
2. **Add missing calculations**: Implement `unified_volume_7d_ema` and `avg_boxes_added_per_day` calculations
3. **Verify frontend**: Ensure all calculated metrics are displayed correctly
4. **Optimize later**: Consider saving calculated metrics to DB for better performance
