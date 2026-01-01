# BoosterBoxPro - Architecture & Design Plan

> **Implementation Decisions:** See **[IMPLEMENTATION_DECISIONS.md](./IMPLEMENTATION_DECISIONS.md)** for all authoritative engineering decisions, locked phases, and scope control.
>
> **Build Strategy:** We are building with **manual data entry first**, then adding marketplace API integration later. See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for manual entry workflow details.
>
> **Marketplace Strategy (Future):** This architecture will implement a dual-marketplace strategy with strict separation when APIs are integrated. See **[MARKETPLACE_STRATEGY.md](./MARKETPLACE_STRATEGY.md)** for detailed marketplace integration requirements.
> 
> **Key Principle:** Each marketplace is its own source of truth. Unification happens at the metric layer only. (Manual data currently populates unified metrics directly.)

## 1. DATABASE SCHEMA

### Core Tables

#### `booster_boxes`
Primary entity representing a unique sealed TCG booster box product.

```sql
CREATE TABLE booster_boxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_product_id VARCHAR(255) UNIQUE NOT NULL, -- e.g., TCGplayer product ID
    product_name VARCHAR(500) NOT NULL,
    set_name VARCHAR(255),
    game_type VARCHAR(100), -- e.g., "MTG", "Pokemon", "Yu-Gi-Oh"
    release_date DATE,
    image_url VARCHAR(500), -- Avatar/logo URL for UI display
    estimated_total_supply INT, -- Optional: for listed percentage calculation
    reprint_risk VARCHAR(20) CHECK (reprint_risk IN ('LOW', 'MEDIUM', 'HIGH')) DEFAULT 'LOW',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_external_product_id (external_product_id),
    INDEX idx_game_type (game_type)
);
```

#### Marketplace Raw Data Tables

**TCGplayer Listings (Primary Marketplace)**

```sql
CREATE TABLE tcg_listings_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    listing_id VARCHAR(255) NOT NULL,  -- TCGplayer listing ID
    seller_id VARCHAR(255),
    listed_price_usd DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    snapshot_timestamp TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    raw_data JSONB,  -- Store full API response for debugging
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (booster_box_id, listing_id, snapshot_date),
    INDEX idx_booster_box_date (booster_box_id, snapshot_date),
    INDEX idx_listing_id (listing_id),
    INDEX idx_snapshot_date (snapshot_date)
);
```

**eBay Sales (Secondary Marketplace - Sold Listings Only)**

```sql
CREATE TABLE ebay_sales_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    sale_date DATE NOT NULL,
    sale_timestamp TIMESTAMP NOT NULL,
    ebay_item_id VARCHAR(255) NOT NULL,
    sold_price_usd DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    seller_id VARCHAR(255),
    listing_type VARCHAR(50),  -- 'AUCTION', 'BIN', etc.
    raw_data JSONB,  -- Store full API response
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (booster_box_id, ebay_item_id),  -- One sale per item ID
    INDEX idx_booster_box_date (booster_box_id, sale_date),
    INDEX idx_sale_date (sale_date),
    INDEX idx_ebay_item_id (ebay_item_id)
);
```

**Design Notes:**
- **TCGplayer:** Store full snapshot every day (authoritative for pricing/supply)
- **eBay:** Store only completed sales, NOT active listings (used for demand signals only)
- Each marketplace has separate raw tables (no mixing)
- `raw_data` JSONB field stores full API response for debugging/audit

#### Per-Marketplace Metrics Tables

**TCGplayer Metrics (Primary Marketplace)**

```sql
CREATE TABLE tcg_box_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- TCGplayer-specific metrics
    floor_price_usd DECIMAL(10, 2),  -- Authoritative floor price
    visible_market_cap_usd DECIMAL(12, 2),
    active_listings_count INT DEFAULT 0,
    tcg_volume_usd DECIMAL(12, 2) DEFAULT 0,
    tcg_units_sold_count INT DEFAULT 0,
    boxes_added_today INT DEFAULT 0,
    
    -- EMAs/SMAs for TCGplayer
    tcg_volume_7d_ema DECIMAL(12, 2),
    tcg_volume_30d_sma DECIMAL(12, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (booster_box_id, metric_date),
    INDEX idx_booster_box_date (booster_box_id, metric_date DESC)
);
```

**eBay Metrics (Secondary Marketplace - Sold Listings Only)**

```sql
CREATE TABLE ebay_box_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- eBay-specific metrics (sold listings only)
    ebay_sales_count INT DEFAULT 0,
    ebay_volume_usd DECIMAL(12, 2) DEFAULT 0,
    ebay_median_sold_price_usd DECIMAL(10, 2),
    ebay_units_sold_count INT DEFAULT 0,
    
    -- Momentum indicators
    ebay_sales_acceleration DECIMAL(8, 2),  -- Change in sales velocity
    ebay_volume_7d_ema DECIMAL(12, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (booster_box_id, metric_date),
    INDEX idx_booster_box_date (booster_box_id, metric_date DESC)
);
```

#### Unified Metrics Table (Final Layer)

**Leaderboard and rankings read ONLY from this table.**

```sql
CREATE TABLE box_metrics_unified (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- Floor price (TCGplayer ONLY - authoritative)
    floor_price_usd DECIMAL(10, 2),
    floor_price_1d_change_pct DECIMAL(6, 2),
    
    -- Unified Volume (Weighted: TCG × 0.7 + eBay × 0.3)
    unified_volume_usd DECIMAL(12, 2) DEFAULT 0,
    unified_volume_7d_ema DECIMAL(12, 2),  -- PRIMARY RANKING METRIC
    
    -- Liquidity Score (Blended metric)
    liquidity_score DECIMAL(8, 2),
    
    -- Momentum (eBay-influenced, EMA smoothed)
    momentum_score DECIMAL(8, 2),
    
    -- Demand Velocity (combined)
    boxes_sold_per_day DECIMAL(8, 2),
    boxes_sold_30d_avg DECIMAL(8, 2),
    
    -- Supply Metrics (TCGplayer ONLY)
    active_listings_count INT DEFAULT 0,
    visible_market_cap_usd DECIMAL(12, 2),
    boxes_added_today INT DEFAULT 0,
    
    -- Time-to-Price-Pressure (TCG supply / unified demand)
    days_to_20pct_increase DECIMAL(8, 2),
    
    -- Listed percentage (TCGplayer)
    listed_percentage DECIMAL(5, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (booster_box_id, metric_date),
    INDEX idx_booster_box_date (booster_box_id, metric_date DESC),
    INDEX idx_unified_volume_7d_ema (unified_volume_7d_ema DESC NULLS LAST),
    INDEX idx_metric_date (metric_date DESC)
);
```

**Design Notes:**
- Metrics calculated per marketplace first, then unified
- Floor price comes ONLY from TCGplayer (authoritative)
- Unified volume uses weighted formula: (TCG × 0.7) + (eBay × 0.3)
- All rankings use `unified_volume_7d_ema` as primary metric

#### TCGplayer Listing Changes (Audit Log)

```sql
CREATE TABLE tcg_listing_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    listing_id VARCHAR(255) NOT NULL,
    change_date DATE NOT NULL,
    change_type VARCHAR(50) NOT NULL CHECK (change_type IN (
        'LISTED', 'DELISTED', 'QUANTITY_DECREASED', 
        'QUANTITY_INCREASED', 'PRICE_CHANGED', 'RELISTED'
    )),
    previous_quantity INT,
    new_quantity INT,
    previous_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2),
    detected_at TIMESTAMP NOT NULL,
    INDEX idx_booster_box_date (booster_box_id, change_date),
    INDEX idx_listing_id (listing_id),
    INDEX idx_change_date (change_date)
);
```

**Note:** eBay does not have a listing_changes table because we only track completed sales, not active listings.

#### `users`
User accounts for favoriting/tracking feature.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt/argon2 hash
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

#### `user_favorites`
Many-to-many relationship between users and booster boxes they want to track.

```sql
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, booster_box_id),  -- Prevent duplicate favorites
    INDEX idx_user_id (user_id),
    INDEX idx_booster_box_id (booster_box_id),
    INDEX idx_user_created (user_id, created_at DESC)  -- For "my list" sorted by favorited date
);
```

---

## 2. INGESTION JOB ARCHITECTURE

### Overview
Separate ingestion jobs for each marketplace:

**TCGplayer Ingestion (1-2× daily):**
1. Fetches current listings from TCGplayer API
2. Compares against previous day's snapshot
3. Detects changes (new listings, delistings, quantity/price changes)
4. Stores new snapshot in `tcg_listings_raw`
5. Stores changes in `tcg_listing_changes`
6. Triggers TCGplayer metrics calculation

**eBay Ingestion (Every 6-12 hours):**
1. Fetches completed sales (last 24h window) from eBay API
2. Stores sales in `ebay_sales_raw`
3. Triggers eBay metrics calculation

### Job Structure

```
ingestion/
├── scheduler.py              # Cron/task scheduler entry point
├── adapters/
│   ├── base.py              # Abstract base class for adapters
│   ├── tcgplayer/
│   │   ├── adapter.py       # TCGplayer adapter implementation
│   │   ├── auth.py          # TCGplayer API authentication
│   │   ├── fetcher.py       # Fetch listings from API
│   │   └── normalizer.py    # Normalize to internal schema
│   └── ebay/
│       ├── adapter.py       # eBay adapter implementation
│       ├── auth.py          # eBay API authentication
│       ├── fetcher.py       # Fetch completed sales from API
│       └── normalizer.py    # Normalize to internal schema
├── comparators/
│   └── tcg_snapshot_diff.py # Compares TCGplayer snapshots, detects changes
├── processors/
│   ├── tcg_processor.py     # Stores TCGplayer snapshots and changes
│   └── ebay_processor.py    # Stores eBay sales
└── utils/
    └── date_utils.py        # Date handling helpers
```

### TCGplayer Ingestion Flow

```
1. Fetch Current Listings from TCGplayer API (per booster_box)
   ↓
2. Load Previous Day Snapshot from tcg_listings_raw (if exists)
   ↓
3. Diff Engine: Compare current vs previous
   ├─ New listings → LISTED change
   ├─ Missing listings → DELISTED change (potential sale)
   ├─ Quantity decreased → QUANTITY_DECREASED change (potential sale)
   ├─ Quantity increased → QUANTITY_INCREASED change (supply add)
   ├─ Price changed → PRICE_CHANGED change
   └─ Reappeared listings → RELISTED change
   ↓
4. Store New Snapshot in tcg_listings_raw
   ↓
5. Store Listing Changes in tcg_listing_changes
   ↓
6. Trigger TCGplayer Metrics Calculation Job
```

### eBay Ingestion Flow

```
1. Fetch Completed Sales from eBay API (rolling 24h window)
   ↓
2. Filter: Only completed sales (ignore active listings, BIN relists)
   ↓
3. Normalize: Convert eBay format to internal schema
   ↓
4. Store Sales in ebay_sales_raw (dedupe by ebay_item_id)
   ↓
5. Trigger eBay Metrics Calculation Job
```

**Key Differences:**
- TCGplayer: Tracks active listings and changes
- eBay: Only tracks completed sales (no active listings)

### Edge Cases Handled in Ingestion

**Relisting Detection:**
- If a `listing_id` disappears for > 1 day, then reappears → mark as `RELISTED`
- Don't count as sale if it was `DELISTED` explicitly

**Partial Sales:**
- If `quantity` decreases but listing still exists → count delta as sale
- Formula: `units_sold = previous_quantity - new_quantity`

**Price Changes:**
- Track but don't count as sale
- Use for floor price calculation

**Missing Previous Snapshot:**
- First ingestion for a box → all listings marked as `LISTED`
- No volume calculation on first day

---

## 3. CALCULATION PIPELINE

### Overview
After ingestion completes, calculate all derived metrics for the snapshot date.

### Pipeline Stages

```
calculate_daily_metrics/
├── calculators/
│   ├── market_cap.py       # Visible market cap
│   ├── volume.py           # Daily volume, EMAs
│   ├── demand_velocity.py  # Boxes sold per day
│   ├── supply_inflow.py    # Boxes added per day
│   └── liquidity.py        # Days to 20% increase
├── aggregators/
│   └── metrics_aggregator.py # Orchestrates all calculators
└── utils/
    └── ema_calculator.py   # Exponential moving average helper
```

### Calculation Logic (Per Booster Box, Per Day)

#### Step 1: Visible Market Cap & Floor Price
```python
current_listings = get_active_listings(booster_box_id, snapshot_date)
floor_price = min([listing.price for listing in current_listings])
visible_market_cap = sum([listing.price * listing.quantity 
                         for listing in current_listings])

# Calculate 1-day floor price change %
previous_day_floor = get_floor_price(booster_box_id, date=snapshot_date - 1_day)
if previous_day_floor and floor_price:
    floor_price_1d_change_pct = ((floor_price - previous_day_floor) / previous_day_floor) * 100
else:
    floor_price_1d_change_pct = None
```

#### Step 2: Daily Volume USD
```python
listing_changes = get_listing_changes(booster_box_id, snapshot_date)
sales = [c for c in listing_changes 
         if c.change_type in ['DELISTED', 'QUANTITY_DECREASED']]

daily_volume = 0
for sale in sales:
    units_sold = sale.previous_quantity - (sale.new_quantity or 0)
    price_at_sale = sale.previous_price  # Price at time of sale
    daily_volume += units_sold * price_at_sale
```

#### Step 3: Volume EMAs/SMAs
```python
# Get previous 30 days of daily_volume_usd
historical_volumes = get_historical_volumes(booster_box_id, days=30)

volume_7d_ema = calculate_ema(historical_volumes, period=7, latest_date=snapshot_date)
volume_30d_sma = calculate_sma(historical_volumes, period=30)
```

#### Step 4: Boxes Sold Per Day
```python
total_units_sold_today = sum([sale.previous_quantity - (sale.new_quantity or 0)
                              for sale in sales])

# 30-day average
historical_units_sold = get_historical_units_sold(booster_box_id, days=30)
boxes_sold_30d_avg = sum(historical_units_sold) / len(historical_units_sold)
```

#### Step 5: Supply Inflow
```python
new_listings = [c for c in listing_changes 
                if c.change_type == 'LISTED']
quantity_increases = [c for c in listing_changes 
                     if c.change_type == 'QUANTITY_DECREASED' and c.new_quantity > c.previous_quantity]

boxes_added_today = (
    sum([c.new_quantity for c in new_listings]) +
    sum([c.new_quantity - c.previous_quantity for c in quantity_increases])
)

# EMAs calculated from historical boxes_added_today values
```

#### Step 6: Days to +20% Increase
```python
active_listings = get_active_listings(booster_box_id, snapshot_date)
active_boxes = sum([l.quantity for l in active_listings])

boxes_needed_to_clear = active_boxes * 0.85
boxes_sold_per_day = boxes_sold_30d_avg  # Use 30-day average

if boxes_sold_per_day > 0:
    days_to_20pct = boxes_needed_to_clear / boxes_sold_per_day
else:
    days_to_20pct = None  # No demand, infinite time
```

### Calculation Job Flow (3-Phase Pipeline)

```
Phase 1: TCGplayer Metrics Calculation
For each booster_box with new TCGplayer snapshot:
  1. Calculate floor_price_usd (MIN of all active listings)
  2. Calculate visible_market_cap_usd
  3. Calculate tcg_volume_usd (from tcg_listing_changes)
  4. Calculate tcg_units_sold_count
  5. Calculate supply metrics (boxes_added_today, etc.)
  6. Fetch historical data for EMAs/SMAs
  7. Calculate tcg_volume_7d_ema, tcg_volume_30d_sma
  8. Upsert into tcg_box_metrics_daily
  9. Update booster_boxes.updated_at

Phase 2: eBay Metrics Calculation
For each booster_box with new eBay sales:
  1. Aggregate sales from ebay_sales_raw (last 24h)
  2. Calculate ebay_sales_count, ebay_volume_usd
  3. Calculate ebay_median_sold_price_usd
  4. Calculate ebay_sales_acceleration (momentum indicator)
  5. Fetch historical data for EMAs
  6. Calculate ebay_volume_7d_ema
  7. Upsert into ebay_box_metrics_daily

Phase 3: Unified Metrics Calculation
For each booster_box (combines TCGplayer + eBay):
  1. Floor price = tcg_box_metrics_daily.floor_price_usd (authoritative)
  2. Unified volume = (tcg_volume_usd × 0.7) + (ebay_volume_usd × 0.3)
  3. Unified volume 7d EMA = weighted combination
  4. Liquidity score = blended formula (50% TCG + 30% TCG velocity + 20% eBay)
  5. Momentum score = ebay_sales_acceleration (EMA smoothed)
  6. Demand velocity = combined boxes_sold (weighted)
  7. Days to 20% = tcg supply / unified demand
  8. Listed percentage = from TCGplayer
  9. Upsert into box_metrics_unified
```

---

## 4. API RESPONSE SHAPES

> **Note:** All endpoints work for both mobile app and website. Mobile-first design ensures efficient payloads suitable for mobile consumption, while web can request larger result sets via pagination parameters.

### Home Screen: Top 10 by Volume (Default)

**Endpoint:** `GET /api/v1/booster-boxes?sort=volume&limit=10`

**Used by:**
- Mobile app home screen (default view)
- Website home page (same view)

**Data Source:** Reads from `box_metrics_unified` table (unified metrics from TCGplayer + eBay)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "rank_change_direction": "up",  // "up", "down", "same" - for UI arrow indicator
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      "set_name": "Modern Horizons 3",
      "game_type": "MTG",
      "image_url": "https://cdn.example.com/mh3-box.jpg",
      "metrics": {
        "floor_price_usd": 245.99,  // TCGplayer (authoritative)
        "floor_price_1d_change_pct": -1.3,  // 1-day % change (for "▼1.3%" display)
        "unified_volume_usd": 45230.50,  // Weighted: (TCG × 0.7) + (eBay × 0.3)
        "unified_volume_7d_ema": 43890.25,  // PRIMARY RANKING METRIC
        "visible_market_cap_usd": 1250000.00,  // TCGplayer
        "units_sold_count": 18,  // Combined sales count
        "active_listings_count": 3044,  // TCGplayer
        "listed_percentage": 8.3,  // For "3,044 / 36.6K (8.3%)" display
        "estimated_total_supply": 36600,
        "days_to_20pct_increase": 12.5,
        "liquidity_score": 85.3,  // Blended metric
        "momentum_score": 12.5,  // eBay-influenced
        "price_sparkline_1d": [  // Mini chart data (last 24h price trend)
          {"timestamp": "2024-01-14T00:00:00Z", "price": 249.99},
          {"timestamp": "2024-01-14T04:00:00Z", "price": 248.50},
          {"timestamp": "2024-01-14T08:00:00Z", "price": 247.25},
          {"timestamp": "2024-01-14T12:00:00Z", "price": 246.00},
          {"timestamp": "2024-01-14T16:00:00Z", "price": 245.50},
          {"timestamp": "2024-01-14T20:00:00Z", "price": 245.99}
        ]
      },
      "reprint_risk": "LOW",
      "metric_date": "2024-01-15"
    }
  ],
  "meta": {
    "total": 150,
    "sort": "volume",
    "sort_direction": "desc",
    "date": "2024-01-15"
  }
}
```

**UI Mapping:**
- `rank` → "#" column (rank number)
- `product_name` + `image_url` → "Collection" column (name + avatar)
- `rank_change_direction` → Up/down arrow on avatar
- `metrics.floor_price_usd` → "Floor" column
- `metrics.floor_price_1d_change_pct` → "Floor 1d %" column (with ▲/▼ indicator)
- `metrics.daily_volume_usd` → "Volume" column (PRIMARY - most prominent)
- `metrics.units_sold_count` → "Sales" column
- `metrics.listed_percentage` + `active_listings_count` + `estimated_total_supply` → "Listed" column
- `metrics.price_sparkline_1d` → "Last 1d" column (mini chart)

### Sorting Options (All Columns Sortable)

**Supported sort parameters:**
- `sort=volume` (default) - Sort by `unified_volume_7d_ema` DESC (PRIMARY RANKING)
- `sort=market_cap` - Sort by `visible_market_cap_usd` DESC (TCGplayer)
- `sort=floor_price` - Sort by `floor_price_usd` DESC (TCGplayer)
- `sort=floor_change_1d` - Sort by `floor_price_1d_change_pct` DESC
- `sort=sales` - Sort by `units_sold_count` DESC
- `sort=listed` - Sort by `active_listings_count` DESC (TCGplayer)
- `sort=momentum` - Sort by `momentum_score` DESC (eBay-influenced)

**All support:** `order=asc` or `order=desc` (default: desc)

**Examples:**
```
GET /api/v1/booster-boxes?sort=volume&limit=10  # Default
GET /api/v1/booster-boxes?sort=market_cap&limit=10
GET /api/v1/booster-boxes?sort=floor_price&order=asc&limit=10
GET /api/v1/booster-boxes?sort=sales&limit=10
```

**Response:** Same shape as default, sorted by requested field

### Favorites: My List

**Endpoint:** `GET /api/v1/users/me/favorites?sort=volume&limit=50`

**Authentication:** Required (Bearer token in Authorization header)

**Response:** Same shape as leaderboard endpoint, but only includes favorited boxes. Includes `is_favorited: true` field.

```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "is_favorited": true,  // Always true in favorites endpoint
      "favorited_at": "2024-01-10T12:30:00Z",  // When user favorited this box
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      // ... rest of fields same as leaderboard response
    }
  ],
  "meta": {
    "total": 15,  // Total favorited boxes for this user
    "sort": "volume",
    "date": "2024-01-15"
  }
}
```

**Sorting:** Supports all same sort options as leaderboard endpoint.

### Favorites: Add/Remove

**Add Favorite:**
```
POST /api/v1/users/me/favorites/{booster_box_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Booster box added to favorites",
  "data": {
    "booster_box_id": "uuid",
    "favorited_at": "2024-01-15T10:30:00Z"
  }
}
```

**Remove Favorite:**
```
DELETE /api/v1/users/me/favorites/{booster_box_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Booster box removed from favorites"
}
```

### Leaderboard with Favorite Status

**When authenticated, leaderboard responses include favorite status:**

**Endpoint:** `GET /api/v1/booster-boxes?sort=volume&limit=10`
**Headers:** `Authorization: Bearer {token}` (optional - only needed for favorite status)

**Updated Response (with auth):**
```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "is_favorited": false,  // User's favorite status (only if authenticated)
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      // ... rest of fields
    }
  ]
}
```

**Note:** If not authenticated, `is_favorited` field is omitted or always `false`.

### Detail View: Single Booster Box

**Endpoint:** `GET /api/v1/booster-boxes/{id}`

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "external_product_id": "tcgplayer-12345",
    "product_name": "Magic: The Gathering - Modern Horizons 3",
    "set_name": "Modern Horizons 3",
    "game_type": "MTG",
    "release_date": "2024-06-14",
    "reprint_risk": "LOW",
    "current_rank_by_volume": 1,
    "current_rank_by_market_cap": 3,
    "rank_history_7d": [
      { "date": "2024-01-09", "volume_rank": 2 },
      { "date": "2024-01-10", "volume_rank": 1 },
      // ...
    ],
    "metrics": {
      "daily_volume_usd": 45230.50,
      "volume_7d_ema": 43890.25,
      "volume_30d_sma": 41200.00,
      "visible_market_cap_usd": 1250000.00,
      "active_listings_count": 125,
      "floor_price_usd": 245.99,
      "days_to_20pct_increase": 12.5,
      "boxes_sold_per_day": 18.2,
      "boxes_sold_30d_avg": 16.8,
      "boxes_added_today": 8,
      "boxes_added_7d_ema": 5.3,
      "boxes_added_30d_ema": 4.8
    },
    "metric_date": "2024-01-15"
  }
}
```

### Time Series: Volume Chart Data

**Endpoint:** `GET /api/v1/booster-boxes/{id}/time-series?metric=volume&days=30`

**Response:**
```json
{
  "data": {
    "booster_box_id": "uuid",
    "metric": "volume",
    "series": [
      {
        "date": "2023-12-16",
        "daily_volume_usd": 32000.00,
        "volume_7d_ema": 31500.00
      },
      // ... 30 days
    ]
  }
}
```

### Mobile vs Web API Considerations

**Shared API Design:**
- Both mobile app and website use the **same REST API endpoints**
- No platform-specific endpoints needed
- Mobile-first means API is optimized for mobile consumption (efficient payloads, minimal nested data)

**Pagination Differences:**
- **Mobile:** Default `limit=10` (home screen), supports infinite scroll with cursor pagination
- **Web:** Can request larger limits (`limit=50` or `limit=100`) for table views, supports traditional pagination

**Optional Platform Header:**
- Request header: `X-Platform: mobile` or `X-Platform: web` (optional, for analytics/monitoring)
- API can use this for optimization hints (e.g., include more metadata for web)

**Response Optimization:**
- Mobile responses keep nested data minimal (metrics object is fine)
- Web can request additional fields via `?fields=` query param if needed later
- No performance difference - same database queries, just different limit/pagination

**Example Usage:**

**Mobile App (Home Screen):**
```http
GET /api/v1/booster-boxes?sort=volume&limit=10
X-Platform: mobile
```

**Web (Home Page - Top 10):**
```http
GET /api/v1/booster-boxes?sort=volume&limit=10
X-Platform: web
```

**Web (Full List View - if needed later):**
```http
GET /api/v1/booster-boxes?sort=volume&limit=50&offset=0
X-Platform: web
```

### Rank Movement Calculation (for UI arrow indicators)

**Logic:**
- Compare `unified_volume_7d_ema` rank today vs yesterday (from `box_metrics_unified`)
- Calculate rank_change = `previous_rank - current_rank`
- Map to `rank_change_direction`:
  - `rank_change > 0` → `"up"` (moved up in ranking)
  - `rank_change < 0` → `"down"` (moved down in ranking)
  - `rank_change == 0` → `"same"` (no change)
  - `previous_rank == NULL` → `"same"` (new box, no previous rank)

**For UI:**
- `"up"` → Show ↑ arrow on avatar (green/positive)
- `"down"` → Show ↓ arrow on avatar (red/negative)
- `"same"` → No indicator

**Note:** Rankings use `unified_volume_7d_ema` as the primary metric (weighted combination of TCGplayer + eBay).

### Sparkline Data (Price Trend Chart)

**For "Last 1d" column mini chart:**
- Need price snapshots over last 24 hours
- Options:
  1. **Simple (Phase 1):** Use daily floor_price for last 7 days (weekly view)
  2. **Enhanced (Phase 2):** Store hourly snapshots in separate table
  3. **Best (Phase 3):** Store 4-hour intervals (6 data points for 24h)

**Initial Implementation:**
- Use existing daily_derived_metrics.floor_price_usd for last 7 days
- Frontend can interpolate between daily points for sparkline
- Later: Add hourly_price_snapshots table if needed for smoother charts

**Implementation:**
```sql
WITH current_ranks AS (
  SELECT 
    booster_box_id,
    ROW_NUMBER() OVER (ORDER BY volume_7d_ema DESC) as current_rank
  FROM daily_derived_metrics
  WHERE metric_date = CURRENT_DATE
),
previous_ranks AS (
  SELECT 
    booster_box_id,
    ROW_NUMBER() OVER (ORDER BY volume_7d_ema DESC) as previous_rank
  FROM daily_derived_metrics
  WHERE metric_date = CURRENT_DATE - INTERVAL '1 day'
)
SELECT 
  c.booster_box_id,
  c.current_rank,
  COALESCE(p.previous_rank, NULL) as previous_rank,
  COALESCE(p.previous_rank - c.current_rank, 0) as rank_change
FROM current_ranks c
LEFT JOIN previous_ranks p ON c.booster_box_id = p.booster_box_id
```

---

## 5. EDGE CASES & HANDLING

### Listing Churn (High Turnover)

**Problem:** Listings appear and disappear rapidly, creating noise in volume calculations.

**Handling:**
- Only count sales if listing existed for > 1 hour (track `first_seen_at` in snapshots)
- Filter out listings that appear/disappear same day (likely data quality issues)
- Use EMA smoothing to dampen noise

### Relists

**Problem:** Seller delists and immediately relists same product (not a true sale).

**Handling:**
- If `listing_id` disappears and reappears within 24 hours with same seller_id → don't count as sale
- If reappears with different seller_id → likely legitimate transfer, count as sale
- Track "relist windows" in `listing_changes` table

### Low-Liquidity Sets

**Problem:** Some boxes have very few listings (e.g., 1-2 active), making metrics unreliable.

**Handling:**
- Minimum threshold: Only show metrics if `active_listings_count >= 3`
- Flag low-liquidity sets in API response: `"liquidity_warning": true`
- Days to 20% calculation: If `active_listings_count < 5`, return `null` (too volatile)

### Price Floors with Single Listing

**Problem:** Floor price driven by one outlier low listing.

**Handling:**
- Use 5th percentile price instead of absolute min for "floor" in calculations
- Or: Floor price = average of bottom 3 listings
- Display actual min separately: `"lowest_listing_price"` vs `"calculated_floor_price"`

### Missing Historical Data

**Problem:** New booster box added, no 30-day history for averages.

**Handling:**
- EMAs/SMAs: Use available data, don't require full period
- `days_to_20pct`: Return `null` until at least 7 days of data
- Show "Insufficient Data" badge in UI for new boxes

### Zero Sales Days

**Problem:** Day with no detected sales (could be true zero or data gap).

**Handling:**
- Store `0` for `daily_volume_usd` (don't skip day)
- EMA calculation handles zeros naturally
- In UI, show "No sales detected" vs "No listings" (different states)

### Marketplace API Failures

**Problem:** TCGplayer API down, can't fetch snapshot.

**Handling:**
- Retry logic (3 attempts with exponential backoff)
- If still failing, mark ingestion job as failed
- Don't calculate metrics for that day (leave gap in time series)
- Alert monitoring system

### Quantity Increases

**Problem:** Seller adds more units to existing listing (not a sale, but affects supply).

**Handling:**
- Track as `QUANTITY_INCREASED` change type (different from DECREASED)
- Count increase as supply inflow in `boxes_added_today`
- Don't count as sale

### Stale Snapshots

**Problem:** Previous snapshot is > 2 days old (gap in ingestion).

**Handling:**
- When gap detected, mark all previous listings as potentially stale
- On next snapshot, treat all reappearances as new listings (conservative)
- Log gap as data quality issue

---

## 6. TECHNOLOGY STACK

> **See [TECH_STACK.md](./TECH_STACK.md) for complete technology stack decisions, package versions, and hosting recommendations.**

### Backend (Locked)
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, auto docs, type hints)
- **Database:** PostgreSQL 15+ (managed: Supabase/Neon recommended)
- **Cache:** Redis 7+ (managed: Redis Cloud/Upstash recommended)
- **Task Queue:** Celery + Redis
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic

### Data Processing
- **Libraries:** pandas, numpy (for EMAs, aggregations)
- **Date Handling:** pendulum (timezone-aware)

### Authentication & Security
- **JWT Library:** python-jose[cryptography]
- **Password Hashing:** passlib[bcrypt]
- **CORS:** Enabled for mobile app and website domains
- **Rate Limiting:** slowapi (FastAPI rate limiting)

### Frontend (Recommended)
- **Mobile App:** React Native + TypeScript (recommended for MVP)
- **Website:** Next.js 14+ (React) + TypeScript
- **State Management:** React Query / TanStack Query
- **Styling:** Tailwind CSS (web)

### Infrastructure (Recommended for MVP)
- **Backend Hosting:** Railway or Render
- **Database:** Supabase or Neon (managed Postgres)
- **Redis:** Redis Cloud or Upstash
- **CI/CD:** GitHub Actions
- **Containerization:** Docker + Docker Compose

---

## 7. OPEN QUESTIONS FOR DECISION

1. **Marketplace APIs:** ✅ DECIDED
   - ✅ TCGplayer (primary) + eBay (secondary)
   - ✅ See MARKETPLACE_STRATEGY.md for detailed architecture
   - Still need: API keys, rate limits, API documentation

2. **Ingestion Frequency:**
   - Daily is specified, but what time of day?
   - Should we support multiple snapshots per day later?

3. **Data Retention:**
   - How long to keep raw `listing_snapshots`? (affects storage costs)
   - Partition by date after 90 days?

4. **Reprint Risk:**
   - Who sets this? Manual admin panel? Community voting?
   - Need a separate table for reprint risk history?

5. **Multi-Marketplace:**
   - Aggregate listings from multiple sources?
   - How to handle duplicate listings across marketplaces?

6. **Frontend Platforms:**
   - **Mobile App:** Native (iOS/Android) or React Native/Flutter? (decided: mobile-first)
   - **Website:** Will reuse same API, responsive web design
   - **Authentication:** ✅ Required for favorites feature (JWT tokens)
   - **User Registration:** Email/password? Social auth (Google/Apple)? Both?

---

## 8. UI DESIGN REQUIREMENTS

See **[UI_REQUIREMENTS.md](./UI_REQUIREMENTS.md)** for detailed UI specifications based on the leaderboard table mockup.

**Key UI Elements:**
- Dark-themed leaderboard/table view
- Rank column with change indicators (↑↓ arrows)
- Collection name + avatar/image
- Floor price with 1-day % change (color-coded)
- Volume (PRIMARY metric - most prominent)
- Sales count
- Listed percentage + absolute numbers
- Sparkline charts for price trends

**UI Requirements Impact:**
- Added `image_url` to booster_boxes table
- Added `floor_price_1d_change_pct` calculation
- Added `listed_percentage` calculation
- Updated API response shape to match table structure
- Support multiple sortable columns

---

## 9. FRONTEND ARCHITECTURE (MOBILE-FIRST)

### Approach
- **Mobile App:** Primary platform, built first
- **Website:** Secondary platform, built after mobile, uses same API
- **Shared API:** Both platforms consume identical REST endpoints
- **API Design:** Optimized for mobile consumption (efficient payloads, minimal nesting)

### Mobile App Considerations
- **Infinite Scroll:** Home screen loads top 10, then loads more on scroll
- **Pull-to-Refresh:** Refresh latest metrics
- **Offline Support:** Cache last fetched data, show stale indicator
- **Performance:** Minimize API calls, use efficient pagination

### Website Considerations
- **Responsive Design:** Mobile-first CSS, adapts to larger screens
- **Larger Result Sets:** Can request more items per page (50-100) for table views
- **Same API:** No special endpoints, just different pagination parameters
- **Additional Features:** Can add filters, search, or advanced sorting later

### Frontend Technology (TBD - Decision Needed)
**Mobile App Options:**
- React Native (cross-platform iOS + Android)
- Flutter (cross-platform iOS + Android)
- Native (separate Swift/Kotlin codebases)

**Website Options:**
- Next.js (React-based, SSR/SSG support)
- React (SPA)
- Vue.js (alternative to React)

### API Client Strategy
- Mobile and web can share API client code if both use React/TypeScript
- Or separate implementations in React Native / Web framework
- Type-safe API clients recommended (generate from OpenAPI/Swagger spec)

---

## NEXT STEPS

Once we align on these questions, we can:
1. **Review UI mockups** (helps finalize API response shapes)
2. Create database migration files
3. Set up backend project structure
4. Implement ingestion pipeline skeleton
5. Build calculation pipeline
6. Create API endpoints (mobile-optimized)
7. **Phase 2:** Build mobile app
8. **Phase 3:** Build website (uses same API)

Let's discuss and refine this plan before coding!


