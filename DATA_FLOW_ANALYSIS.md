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

---

## Scraper → Box Detail flow (as soon as updated)

**Goal**: Scraped data (listings, floor price) appears on the box detail page as soon as the daily refresh runs.

### 1. Scraper run (`scripts/listings_scraper.py`)

- For each box (TCGPlayer UUID), scrapes TCGplayer and gets `listings_within_20pct` and `floor_price`.
- **`save_results()`**:
  - **JSON**: Appends/updates an entry for **today** under `hist[box_id]` (TCG UUID) with `date`, `source: 'tcgplayer_scraper'`, `floor_price_usd`, `active_listings_count` (= listings within 20%).
  - **DB**: Calls `upsert_daily_metrics(booster_box_id=leaderboard_uuid, metric_date=today, floor_price_usd=..., active_listings_count=...)`. Uses `DB_TO_LEADERBOARD_UUID_MAP` so the row is written under the **leaderboard UUID** (same as `booster_boxes.id`).

### 2. Box detail read path

- **Endpoint**: `GET /booster-boxes/{box_id}` uses `db_box.id` (leaderboard UUID).
- **Data**: `get_box_price_history(str(db_box.id), days=90)`:
  - Calls `get_box_historical_data(box_id)` with `prefer_db=True`.
- **`get_box_historical_data(leaderboard_uuid)`**:
  - **DB**: Loads rows from `box_metrics_unified` for **leaderboard UUID** and for **TCG UUID** (via `LEADERBOARD_TO_DB_UUID_MAP`), then **merges same-date entries** so one calendar day can combine scraper (listings, floor) and Apify (sales, volume).
  - **JSON fallback**: Loads `historical_entries.json` for both leaderboard and TCG keys, merges same-date entries. Merge treats `active_listings_count`, `listings_count`, and `listings_count_in_range` so scraper data is used.
- **Box detail logic**:
  - Uses `historical_data[-1]` as “latest”.
  - **Active listings**: If latest has no `active_listings_count`, uses the **most recent prior entry** that has it (so scraper-only or merged scraper data still shows).
  - **30d avg sold**: `get_box_30d_avg_sales(box_id)` uses the same merged history (DB or JSON).
  - **Days to 20%**: `active_listings / (boxes_sold_30d_avg - avg_boxes_added_per_day)`.

### 3. When data shows up

- **DB path**: Scraper writes to `box_metrics_unified`; the next request to box detail reads from the DB (no JSON cache). So **scraped data is visible on the next box detail request** after the run.
- **JSON path**: Scraper overwrites/append for today in `historical_entries.json`; the JSON cache TTL is 60s, so within about a minute the next request will see the new data.
