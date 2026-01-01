# Marketplace Integration Strategy

## 🎯 Build Strategy: Manual-First Approach

**Current Phase:** We are building with **manual data entry first**. This document describes the **future marketplace API integration strategy** that will be implemented after MVP is complete and validated with manual data.

**Manual Entry:** See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for details on manual data entry workflow.

**Future API Integration:** The strategy below will be implemented in Phase 2B (TCGplayer) and Phase 4 (eBay) after the app is fully functional with manual data.

---

## Core Principle (Future API Integration)

**Each marketplace is treated as its own source of truth.**
- We do NOT merge raw listings or attempt to dedupe individual sales across marketplaces.
- All unification happens at the metric layer, never the listing layer.
- Separation-of-concerns architecture to avoid data corruption and complexity.

---

## Marketplace Roles

### TCGplayer (Primary / Canonical)

**Use for:**
- ✅ Floor price (authoritative)
- ✅ Active listings
- ✅ Quantity & supply
- ✅ Stable volume + long-term liquidity

**Trust level:** HIGH

TCGplayer data drives pricing, supply pressure, and base liquidity.

**Do NOT use:**
- ❌ Do not use eBay for floor price
- ❌ Do not mix with eBay raw listings

---

### eBay (Secondary / Demand Signal)

**Use ONLY sold/completed listings, NOT active listings.**

**Use for:**
- ✅ Sales velocity
- ✅ Demand spikes
- ✅ Median sold price
- ✅ Short-term momentum

**Ignore:**
- ❌ Active listings
- ❌ BIN relists
- ❌ Seller quantities

**Trust level:** MEDIUM

eBay is a leading indicator, not a pricing oracle.

---

## Architecture Requirements

### Marketplace Adapter Layer (Required)

Each marketplace must implement its own adapter and normalize into internal schemas:

```
adapters/
├── base.py              # Abstract base class
├── tcgplayer/
│   ├── adapter.py       # TCGplayer-specific implementation
│   ├── auth.py          # API authentication
│   └── normalizer.py    # Normalize to internal schema
└── ebay/
    ├── adapter.py       # eBay-specific implementation
    ├── auth.py          # API authentication
    └── normalizer.py    # Normalize to internal schema
```

**Each adapter handles:**
- Auth (API keys, OAuth, etc.)
- Rate limits
- Pagination
- Error handling
- Normalization to internal schemas

**No shared raw tables** - each marketplace has its own raw data tables.

---

## Database Schema (Updated)

### TCGplayer Raw Data

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
    INDEX idx_listing_id (listing_id)
);
```

### eBay Raw Data (Sold Listings Only)

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

**Note:** We do NOT store active eBay listings, only completed sales.

---

### Per-Marketplace Metrics

```sql
CREATE TABLE tcg_box_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- TCGplayer-specific metrics
    floor_price_usd DECIMAL(10, 2),
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

CREATE TABLE ebay_box_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- eBay-specific metrics (sold listings only)
    ebay_sales_count INT DEFAULT 0,  -- Number of completed sales
    ebay_volume_usd DECIMAL(12, 2) DEFAULT 0,  -- Total sales volume
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

---

### Unified Metrics (Final Layer)

```sql
CREATE TABLE box_metrics_unified (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- Floor price (TCGplayer ONLY - authoritative)
    floor_price_usd DECIMAL(10, 2),  -- From TCGplayer
    
    -- Unified Volume (Weighted)
    unified_volume_usd DECIMAL(12, 2) DEFAULT 0,
    -- Formula: (TCG Volume × 0.7) + (eBay Volume × 0.3)
    
    -- Liquidity Score (Blended)
    liquidity_score DECIMAL(8, 2),
    -- Formula: (~50% TCG absorption) + (~30% TCG velocity) + (~20% eBay consistency)
    
    -- Momentum (Influenced by eBay, smoothed with EMA)
    momentum_score DECIMAL(8, 2),
    
    -- Demand Velocity
    boxes_sold_per_day DECIMAL(8, 2),
    boxes_sold_30d_avg DECIMAL(8, 2),
    
    -- Supply Metrics (TCGplayer ONLY)
    active_listings_count INT DEFAULT 0,
    visible_market_cap_usd DECIMAL(12, 2),
    boxes_added_today INT DEFAULT 0,
    
    -- Time-to-Price-Pressure (uses TCGplayer supply, unified demand)
    days_to_20pct_increase DECIMAL(8, 2),
    
    -- Volume EMAs (for ranking)
    unified_volume_7d_ema DECIMAL(12, 2),  -- PRIMARY RANKING METRIC
    
    -- 1-day floor price change (TCGplayer)
    floor_price_1d_change_pct DECIMAL(6, 2),
    
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

**Leaderboard and rankings read ONLY from `box_metrics_unified`.**

---

## Metrics Strategy

### Floor Price
- **TCGplayer ONLY** - Authoritative source
- Do NOT use eBay for floor price
- eBay is not a pricing oracle

### Unified Volume (Weighted)

```
Unified Volume = (TCGplayer Volume × 0.7) + (eBay Volume × 0.3)
```

**Rationale:**
- TCGplayer is primary marketplace, more stable
- eBay provides demand signal but is noisier
- 70/30 split balances stability with momentum

**This is used for ranking** - `unified_volume_7d_ema` is the PRIMARY ranking metric.

### Liquidity Score (Blended) - LOCKED FORMULA

**Initial Formula (Tunable):**

```
Liquidity Score =
  (Boxes Sold / Boxes Listed) × 0.5
+ (7d Sales Velocity EMA) × 0.3
+ (eBay Sales Frequency) × 0.2
```

**Notes:**
- Liquidity is relative, not absolute
- Used for ranking & signals, not pricing
- Always smoothed (EMA)

**Purpose:** Measure overall market liquidity and stability.

### Momentum

- Influenced by eBay sales acceleration
- Smoothed with EMA
- Used for trend / spike detection, not raw rankings
- Helps identify demand surges

---

## Data Handling Rules (Non-Negotiable)

### ❌ Do NOT:
- ❌ Dedupe individual sales across marketplaces
- ❌ Mix raw listings from different sources
- ❌ Use eBay for floor price calculations
- ❌ Store eBay active listings

### ✅ Do:
- ✅ Combine marketplaces only at the aggregated metric level
- ✅ Smooth all cross-market metrics with EMA
- ✅ Conservative bias: undercount > overcount
- ✅ Calculate per-marketplace metrics first, then unify

---

## Polling Strategy

### TCGplayer
- **Listings & prices:** 1-2× daily
- **Time:** 02:00 UTC (recommended)
- **What:** Active listings, prices, quantities

### eBay
- **Sold listings:** Every 6-12 hours (rolling 24h window)
- **Time:** 02:00 UTC and 14:00 UTC (recommended)
- **What:** Completed sales only (last 24 hours)

**Note:** eBay polling frequency may need adjustment based on rate limits.

---

## Calculation Pipeline Flow

```
1. TCGplayer Ingestion
   ↓
2. TCGplayer Metrics Calculation
   ├─ Floor price
   ├─ Market cap
   ├─ Volume (from listing changes)
   ├─ Supply inflow
   └─ Store in: tcg_box_metrics_daily
   
3. eBay Ingestion (Sold Listings)
   ↓
4. eBay Metrics Calculation
   ├─ Sales count
   ├─ Sales volume
   ├─ Median sold price
   ├─ Sales acceleration (momentum)
   └─ Store in: ebay_box_metrics_daily
   
5. Unified Metrics Calculation
   ├─ Floor price = TCGplayer floor_price (authoritative)
   ├─ Unified volume = (TCG volume × 0.7) + (eBay volume × 0.3)
   ├─ Liquidity score = Blended formula
   ├─ Momentum = eBay acceleration (EMA smoothed)
   ├─ Demand velocity = Combined (weighted)
   ├─ Days to 20% = TCG supply / unified demand
   └─ Store in: box_metrics_unified
   
6. Ranking Calculation
   └─ Rank by unified_volume_7d_ema (from box_metrics_unified)
```

---

## Implementation Phases

> **See [BUILD_PHASES.md](./BUILD_PHASES.md) for complete, sequential build order (Phases 0-8).**

### High-Level Marketplace Integration Phases

**Phase 2 (BUILD_PHASES.md):** TCGplayer Ingestion (raw data)
- ✅ TCGplayer adapter implementation
- ✅ Daily listing snapshots ingestion
- ✅ Store raw data in `tcg_listings_raw`
- ✅ Listing change detection

**Phase 3 (BUILD_PHASES.md):** TCGplayer Metrics
- ✅ Daily aggregated metrics calculation
- ✅ EMA-smoothed volume
- ✅ Absorption rate
- ✅ Liquidity score (partial - TCGplayer only)

**Phase 4 (BUILD_PHASES.md):** eBay Demand Signal
- ✅ eBay adapter implementation (sold listings only)
- ✅ eBay raw data ingestion
- ✅ Sales metrics calculation
- ✅ Momentum indicators

**Phase 5 (BUILD_PHASES.md):** Unified Metrics Layer
- ✅ Weighted volume (TCG × 0.7 + eBay × 0.3)
- ✅ Final liquidity score (blended)
- ✅ All rankings read from unified metrics only

---

## API Response (Updated)

The API still returns unified metrics, but we understand the sources:

```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "product_name": "...",
      "metrics": {
        "floor_price_usd": 245.99,  // TCGplayer (authoritative)
        "unified_volume_usd": 45230.50,  // Weighted: (TCG × 0.7) + (eBay × 0.3)
        "unified_volume_7d_ema": 43890.25,  // PRIMARY RANKING METRIC
        "momentum_score": 12.5,  // eBay-influenced, EMA smoothed
        "liquidity_score": 85.3,  // Blended metric
        // ... other unified metrics
      }
    }
  ]
}
```

**Note:** API consumers don't need to know the sources - unified metrics hide the complexity.

---

## Guiding Philosophy

1. **TCGplayer = price + supply truth**
   - Authoritative for pricing and supply metrics

2. **eBay = demand + velocity signal**
   - Leading indicator for demand spikes
   - Not used for pricing

3. **Accuracy > completeness**
   - Better to have accurate partial data than corrupted merged data

4. **Start conservative, validate with real data, then scale**
   - Validate weights (70/30) with real data
   - Adjust based on observed patterns
   - Can add more marketplaces later using same pattern

5. **Separation of concerns**
   - Each marketplace adapter is independent
   - Metrics unification is explicit and testable
   - No hidden data mixing

---

## Future Considerations

- **Additional marketplaces:** Can follow same pattern (new adapter, new raw table, new metrics table, update unified)
- **Weight tuning:** 70/30 split may need adjustment based on real data
- **Liquidity score formula:** May refine based on observed market behavior
- **Momentum calculation:** May add more sophisticated indicators later

