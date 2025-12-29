# BoosterBoxPro - Data Flow Diagrams

## System Overview

```
┌─────────────────┐
│  Marketplace    │
│    APIs         │
│  (TCGplayer)    │
└────────┬────────┘
         │
         │ [Fetch Listings]
         │
         ▼
┌─────────────────────────────────────┐
│      Ingestion Job                  │
│  ┌───────────────────────────────┐  │
│  │ 1. Fetch Current Listings     │  │
│  │ 2. Load Previous Snapshot     │  │
│  │ 3. Diff Engine                │  │
│  │ 4. Store Snapshot             │  │
│  │ 5. Store Listing Changes      │  │
│  └───────────────────────────────┘  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Calculation Pipeline              │
│  ┌───────────────────────────────┐  │
│  │ 1. Calculate Market Cap       │  │
│  │ 2. Calculate Daily Volume     │  │
│  │ 3. Calculate EMAs/SMAs        │  │
│  │ 4. Calculate Demand Velocity  │  │
│  │ 5. Calculate Supply Inflow    │  │
│  │ 6. Calculate Days to 20%      │  │
│  │ 7. Store Metrics              │  │
│  └───────────────────────────────┘  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      PostgreSQL Database            │
│  • booster_boxes                    │
│  • listing_snapshots                │
│  • listing_changes                  │
│  • daily_derived_metrics            │
└────────────┬────────────────────────┘
             │
             │ [Query]
             ▼
┌─────────────────────────────────────┐
│        FastAPI Backend              │
│  ┌───────────────────────────────┐  │
│  │ GET /booster-boxes            │  │
│  │ GET /booster-boxes/{id}       │  │
│  │ GET /booster-boxes/{id}/      │  │
│  │     time-series               │  │
│  └───────────────────────────────┘  │
└────────────┬────────────────────────┘
             │
             │ [JSON Response]
             ▼
┌─────────────────────────────────────┐
│   Mobile App (Primary)              │
│   Website (Secondary)               │
│   └─ Both consume same API          │
└─────────────────────────────────────┘
```

---

## Ingestion Flow (Detailed)

```
Daily Ingestion Job (02:00 UTC)
│
├─ For each tracked booster_box:
│  │
│  ├─ [Step 1] Fetch Current Listings
│  │  └─ API Call: GET /products/{external_product_id}/listings
│  │     Returns: [{listing_id, price, quantity, seller_id, timestamp}]
│  │
│  ├─ [Step 2] Load Previous Snapshot
│  │  └─ Query: SELECT * FROM listing_snapshots 
│  │            WHERE booster_box_id = ? 
│  │            AND snapshot_date = YESTERDAY
│  │     Returns: [{listing_id, price, quantity, ...}]
│  │
│  ├─ [Step 3] Diff Engine
│  │  │
│  │  ├─ Compare Current vs Previous
│  │  │  │
│  │  │  ├─ New Listings
│  │  │  │  └─ listing_id in current, NOT in previous
│  │  │  │     → Change Type: LISTED
│  │  │  │
│  │  │  ├─ Delisted
│  │  │  │  └─ listing_id in previous, NOT in current
│  │  │  │     → Change Type: DELISTED (potential sale)
│  │  │  │
│  │  │  ├─ Quantity Decreased
│  │  │  │  └─ listing_id exists, quantity decreased
│  │  │  │     → Change Type: QUANTITY_DECREASED (partial sale)
│  │  │  │
│  │  │  ├─ Quantity Increased
│  │  │  │  └─ listing_id exists, quantity increased
│  │  │  │     → Change Type: QUANTITY_INCREASED (supply add)
│  │  │  │
│  │  │  ├─ Price Changed
│  │  │  │  └─ listing_id exists, price different
│  │  │  │     → Change Type: PRICE_CHANGED
│  │  │  │
│  │  │  └─ Relisted Detection
│  │  │     └─ listing_id disappeared >24h ago, now reappeared
│  │  │        → Change Type: RELISTED
│  │  │
│  │  └─ Output: List of listing_changes
│  │
│  ├─ [Step 4] Store New Snapshot
│  │  └─ INSERT INTO listing_snapshots 
│  │     VALUES (current_listings with snapshot_date = TODAY)
│  │
│  └─ [Step 5] Store Listing Changes
│     └─ INSERT INTO listing_changes 
│        VALUES (all detected changes)
│
└─ [Step 6] Trigger Calculation Pipeline
```

---

## Calculation Pipeline Flow

```
Calculation Pipeline (triggered after ingestion)
│
├─ For each booster_box with new snapshot_date:
│  │
│  ├─ [Step 1] Calculate Visible Market Cap
│  │  │
│  │  ├─ Load active listings for TODAY
│  │  │  SELECT * FROM listing_snapshots 
│  │  │  WHERE booster_box_id = ? AND snapshot_date = TODAY
│  │  │
│  │  ├─ Calculate floor_price = MIN(price)
│  │  ├─ Calculate visible_market_cap = Σ(price × quantity)
│  │  └─ Store: active_listings_count, floor_price, visible_market_cap
│  │
│  ├─ [Step 2] Calculate Daily Volume USD
│  │  │
│  │  ├─ Load listing changes for TODAY
│  │  │  SELECT * FROM listing_changes 
│  │  │  WHERE booster_box_id = ? 
│  │  │  AND change_date = TODAY
│  │  │  AND change_type IN ('DELISTED', 'QUANTITY_DECREASED')
│  │  │
│  │  ├─ For each sale:
│  │  │  units_sold = previous_quantity - new_quantity
│  │  │  sale_amount = units_sold × previous_price
│  │  │
│  │  ├─ daily_volume_usd = Σ(sale_amount)
│  │  └─ Store: daily_volume_usd, units_sold_count
│  │
│  ├─ [Step 3] Calculate Volume EMAs/SMAs
│  │  │
│  │  ├─ Load last 30 days of daily_volume_usd
│  │  │  SELECT daily_volume_usd, metric_date 
│  │  │  FROM daily_derived_metrics
│  │  │  WHERE booster_box_id = ? 
│  │  │  ORDER BY metric_date DESC LIMIT 30
│  │  │
│  │  ├─ Calculate volume_7d_ema (using EMA formula)
│  │  ├─ Calculate volume_30d_sma (simple average)
│  │  └─ Store: volume_7d_ema, volume_30d_sma
│  │
│  ├─ [Step 4] Calculate Demand Velocity
│  │  │
│  │  ├─ boxes_sold_per_day = units_sold_count (from Step 2)
│  │  │
│  │  ├─ Load last 30 days of units_sold_count
│  │  │  SELECT units_sold_count FROM daily_derived_metrics
│  │  │  WHERE booster_box_id = ? ORDER BY metric_date DESC LIMIT 30
│  │  │
│  │  ├─ boxes_sold_30d_avg = Σ(units_sold_count) / 30
│  │  └─ Store: boxes_sold_per_day, boxes_sold_30d_avg
│  │
│  ├─ [Step 5] Calculate Supply Inflow
│  │  │
│  │  ├─ Load listing changes for TODAY (LISTED, QUANTITY_INCREASED)
│  │  │  SELECT * FROM listing_changes
│  │  │  WHERE booster_box_id = ? AND change_date = TODAY
│  │  │  AND change_type IN ('LISTED', 'QUANTITY_INCREASED')
│  │  │
│  │  ├─ boxes_added_today = 
│  │  │    Σ(new_listing.quantity) + 
│  │  │    Σ(quantity_increase.new_quantity - previous_quantity)
│  │  │
│  │  ├─ Calculate boxes_added_7d_ema (using EMA formula)
│  │  ├─ Calculate boxes_added_30d_ema (using EMA formula)
│  │  └─ Store: boxes_added_today, boxes_added_7d_ema, boxes_added_30d_ema
│  │
│  ├─ [Step 6] Calculate Days to 20% Increase
│  │  │
│  │  ├─ active_boxes = Σ(quantity) from active listings
│  │  ├─ boxes_needed_to_clear = active_boxes × 0.85
│  │  ├─ boxes_sold_per_day = boxes_sold_30d_avg (from Step 4)
│  │  │
│  │  ├─ IF boxes_sold_per_day > 0:
│  │  │  days_to_20pct = boxes_needed_to_clear / boxes_sold_per_day
│  │  │ ELSE:
│  │  │  days_to_20pct = NULL
│  │  │
│  │  └─ Store: days_to_20pct_increase
│  │
│  └─ [Step 7] Store All Metrics
│     └─ INSERT INTO daily_derived_metrics 
│        VALUES (all calculated metrics for TODAY)
│
└─ [Step 8] Update Rankings (if needed)
   └─ Rankings computed on-the-fly via SQL window functions
```

---

## Listing Change Detection Logic (Decision Tree)

```
For each listing_id in current snapshot:
│
├─ Does listing_id exist in previous snapshot?
│  │
│  ├─ NO → New Listing
│  │  └─ Check: Did it disappear <24h ago?
│  │     ├─ YES → RELISTED (same listing_id)
│  │     └─ NO → LISTED (brand new)
│  │
│  └─ YES → Existing Listing
│     │
│     ├─ Compare quantity
│     │  │
│     │  ├─ quantity < previous_quantity
│     │  │  └─ QUANTITY_DECREASED (partial sale)
│     │  │
│     │  ├─ quantity > previous_quantity
│     │  │  └─ QUANTITY_INCREASED (supply add)
│     │  │
│     │  └─ quantity == previous_quantity
│     │     │
│     │     └─ Compare price
│     │        │
│     │        ├─ price != previous_price
│     │        │  └─ PRICE_CHANGED
│     │        │
│     │        └─ price == previous_price
│     │           └─ No change (skip)
│     │
│     └─ (quantity comparison handles this branch)

For each listing_id in previous snapshot:
│
├─ Does listing_id exist in current snapshot?
│  │
│  ├─ NO → Missing Listing
│  │  └─ DELISTED (potential sale)
│  │
│  └─ YES → Already handled above
```

---

## API Request/Response Flow

```
Mobile App (Primary) or Website (Secondary)
│
└─ GET /api/v1/booster-boxes?sort=volume&limit=10
   │ (Optional: X-Platform: mobile|web header)
   │
   ▼
FastAPI Endpoint
│
├─ [Step 1] Determine sort order
│  └─ sort=volume → ORDER BY volume_7d_ema DESC
│     sort=market_cap → ORDER BY visible_market_cap_usd DESC
│
├─ [Step 2] Query Database
│  └─ SELECT 
│       bb.*,
│       ddm.*,
│       ROW_NUMBER() OVER (ORDER BY ddm.volume_7d_ema DESC) as current_rank
│     FROM booster_boxes bb
│     JOIN daily_derived_metrics ddm 
│       ON bb.id = ddm.booster_box_id
│     WHERE ddm.metric_date = (SELECT MAX(metric_date) FROM daily_derived_metrics)
│     ORDER BY [sort_field] DESC
│     LIMIT 10
│
├─ [Step 3] Calculate Rank Changes
│  └─ LEFT JOIN with previous day's ranks
│     rank_change = previous_rank - current_rank
│
├─ [Step 4] Transform to API Response
│  └─ Map database rows to JSON schema
│
└─ Return JSON Response
   └─ {data: [...], meta: {...}}
```

---

## Data Relationships

```
booster_boxes (1) ──┐
                     │
                     ├─→ (1:N) listing_snapshots
                     │          • Stores daily snapshots of all listings
                     │
                     ├─→ (1:N) listing_changes
                     │          • Audit log of listing state changes
                     │
                     └─→ (1:N) daily_derived_metrics
                                • Pre-computed metrics per day
                                • Indexed for fast ranking queries
```

**Key Relationships:**
- `booster_boxes.id` → `listing_snapshots.booster_box_id`
- `booster_boxes.id` → `listing_changes.booster_box_id`
- `booster_boxes.id` → `daily_derived_metrics.booster_box_id`
- `listing_snapshots.listing_id` + `snapshot_date` → unique constraint
- `daily_derived_metrics.booster_box_id` + `metric_date` → unique constraint

---

## Error Handling Flow

```
Ingestion Job Error
│
├─ API Failure
│  └─ Retry 3 times with exponential backoff
│     ├─ Success → Continue
│     └─ Failure → Mark job as failed, alert, skip this day
│
├─ Database Error
│  └─ Rollback transaction, log error, alert
│
└─ Data Quality Issue
   └─ Log warning, continue with best-effort processing
      (e.g., missing previous snapshot → treat all as new listings)

Calculation Pipeline Error
│
├─ Missing Historical Data
│  └─ Use available data, set missing fields to NULL
│
├─ Division by Zero
│  └─ Return NULL (e.g., days_to_20pct when no sales)
│
└─ Calculation Error
   └─ Log error, skip this box, continue with others
```

---

## Time-based Data Flow

```
Timeline View:

Day 0 (Initial)
│
├─ Booster box added to system
├─ No historical data
└─ First snapshot stored

Day 1
│
├─ Ingestion: Fetch listings, compare to Day 0
├─ Calculate metrics (limited history available)
└─ Store metrics (some fields may be NULL)

Day 2-6
│
├─ Building up history
├─ EMAs start stabilizing
└─ Some metrics still unavailable (need 7+ days)

Day 7+
│
├─ Full metrics available
├─ EMAs/SMAs calculated with full periods
└─ days_to_20pct can be calculated reliably

Ongoing
│
├─ Daily ingestion at 02:00 UTC
├─ Metrics calculated immediately after
└─ Rankings updated automatically
```


