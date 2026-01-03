# Box Detail Page - Complete Metrics & Details Mapping

> **Purpose:** Comprehensive mapping of ALL metrics, data fields, and details needed for the box detail page based on all planning documents.

---

## 📋 Table of Contents

1. [Header Section](#header-section)
2. [Key Metrics Card](#key-metrics-card)
3. [Price Chart](#price-chart)
4. [Advanced Metrics Table](#advanced-metrics-table)
5. [Rank History](#rank-history)
6. [Additional Context](#additional-context)
7. [Time-Series Data](#time-series-data)
8. [Marketplace-Specific Metrics](#marketplace-specific-metrics)

---

## 1. Header Section

### Visual Elements
- **Box Image/Avatar** (`image_url`)
  - Large display image
  - Source: `booster_boxes.image_url`

### Text Information
- **Product Name** (`product_name`)
  - Source: `booster_boxes.product_name`
  - Display: Full product name

- **Set Name** (`set_name`)
  - Source: `booster_boxes.set_name`
  - Display: Set name (if available)

- **Current Rank** (`current_rank_by_volume`)
  - Source: Calculated from `box_metrics_unified.unified_volume_7d_ema` (PRIMARY RANKING)
  - Display: Rank number (e.g., "#1", "#5")
  - Alternative ranks:
    - `current_rank_by_market_cap` (from `visible_market_cap_usd`)

- **Rank Change Indicator** (`rank_change_direction`, `rank_change_amount`)
  - Source: Compare today's rank vs yesterday's rank
  - Values: `"up"`, `"down"`, `"same"`
  - Display: Arrow indicator (↑ green, ↓ red, or no indicator)
  - Optional: Show amount moved (e.g., "+2", "-3")

### Interactive Elements
- **Favorite/Unfavorite Button** (`is_favorited`)
  - Source: `user_favorites` table (if authenticated)
  - Display: Heart icon or star icon
  - State: Favorited / Not favorited

---

## 2. Key Metrics Card

### Primary Metrics (Prominent Display)

#### Floor Price
- **Current Floor Price** (`floor_price_usd`)
  - Source: `box_metrics_unified.floor_price_usd` (TCGplayer authoritative)
  - Display: Large, prominent (e.g., "$245.99")
  - Format: Currency (USD)

- **Floor Price 24h Change %** (`floor_price_1d_change_pct`)
  - Source: `box_metrics_unified.floor_price_1d_change_pct`
  - Calculation: `((today_floor - yesterday_floor) / yesterday_floor) * 100`
  - Display: Percentage with arrow (e.g., "▼1.3%" red, "▲4.7%" green)
  - Color: Red for negative, green for positive

#### Volume Metrics
- **Daily Volume USD** (`unified_volume_usd`)
  - Source: `box_metrics_unified.unified_volume_usd`
  - Calculation: Weighted `(TCG × 0.7) + (eBay × 0.3)`
  - Display: Currency format (e.g., "$45,230.50")
  - Label: "Daily Volume"

- **Volume 7-Day EMA** (`unified_volume_7d_ema`)
  - Source: `box_metrics_unified.unified_volume_7d_ema`
  - **PRIMARY RANKING METRIC**
  - Display: Currency format (e.g., "$43,890.25")
  - Label: "7-Day EMA Volume"

- **Volume 30-Day SMA** (`volume_30d_sma`)
  - Source: `tcg_box_metrics_daily.tcg_volume_30d_sma` (or unified equivalent)
  - Display: Currency format
  - Label: "30-Day Average Volume"

#### Liquidity & Supply Metrics
- **Liquidity Score** (`liquidity_score`)
  - Source: `box_metrics_unified.liquidity_score`
  - Calculation: Blended formula (50% TCG + 30% TCG velocity + 20% eBay)
  - Display: Numeric score (e.g., "85.3")
  - Label: "Liquidity Score" 

- **Visible Market Cap** (`visible_market_cap_usd`)
  - Source: `box_metrics_unified.visible_market_cap_usd` (TCGplayer)
  - Calculation: `Σ(listing.price × listing.quantity)` for all active listings
  - Display: Currency format (e.g., "$1,250,000.00")
  - Label: "Market Cap"

#### Time-to-Price-Pressure Metrics
- **Days to +20% Increase** (`days_to_20pct_increase`)
  - Source: `box_metrics_unified.days_to_20pct_increase`
  - Calculation: `(active_boxes × 0.85) / boxes_sold_per_day`
  - Display: Decimal number (e.g., "12.5 days")
  - Label: "Days to +20%"
  - Note: Returns `NULL` if `boxes_sold_per_day == 0` or insufficient data

- **Expected Days to Sell** (Alternative label for above)
  - Same as `days_to_20pct_increase`
  - Display: "Expected Days to Sell"

#### Demand Velocity
- **Boxes Sold Per Day** (`boxes_sold_per_day`)
  - Source: `box_metrics_unified.boxes_sold_per_day`
  - Display: Decimal (e.g., "18.2 boxes/day")
  - Label: "Daily Sales Rate"

- **Boxes Sold 30-Day Average** (`boxes_sold_30d_avg`)
  - Source: `box_metrics_unified.boxes_sold_30d_avg`
  - Display: Decimal (e.g., "16.8 boxes/day")
  - Label: "30-Day Average Sales"

#### Supply Inflow
- **Boxes Added Today** (`boxes_added_today`)
  - Source: `box_metrics_unified.boxes_added_today` (TCGplayer)
  - Calculation: New listings + quantity increases
  - Display: Integer (e.g., "8 boxes")
  - Label: "Supply Added Today"

- **Boxes Added 7-Day EMA** (`boxes_added_7d_ema`)
  - Source: `tcg_box_metrics_daily.boxes_added_7d_ema`
  - Display: Decimal (e.g., "5.3 boxes/day")
  - Label: "7-Day Average Supply"

- **Boxes Added 30-Day EMA** (`boxes_added_30d_ema`)
  - Source: `tcg_box_metrics_daily.boxes_added_30d_ema`
  - Display: Decimal (e.g., "4.8 boxes/day")
  - Label: "30-Day Average Supply"

#### Sales Count
- **Units Sold Count** (`units_sold_count`)
  - Source: `box_metrics_unified.units_sold_count` (combined TCG + eBay)
  - Display: Integer (e.g., "18 boxes")
  - Label: "Units Sold"

---

## 3. Price Chart

### Chart Data Requirements
- **Metric**: Floor Price Trend
- **Default Time Range**: Last 30 days
- **Time Range Selector**: Allow user to select (7d, 30d, 90d, 1y, all)

### Data Points
- **Date** (`date`)
  - Source: `box_metrics_unified.metric_date`
  - Format: Date (YYYY-MM-DD)

- **Floor Price** (`floor_price_usd`)
  - Source: `box_metrics_unified.floor_price_usd`
  - Format: Decimal (USD)

### Chart Features
- **Interactive Tooltips**
  - Show exact price and date on hover
  - Format: "$245.99 on Jan 15, 2024"

- **Visual Elements**
  - Line chart
  - Color: Green for upward trend, red for downward trend
  - Grid lines for readability

### Data Source Endpoint
- **Endpoint**: `GET /api/v1/booster-boxes/{id}/time-series?metric=floor_price&days=30`
- **Response**: Array of `{date, floor_price_usd}` objects

---

## 4. Advanced Metrics Table

### Table Columns (Time-Series Data)

#### Date
- **Date** (`metric_date`)
  - Source: `box_metrics_unified.metric_date`
  - Format: Date (MM/DD/YYYY or YYYY-MM-DD)
  - Sortable: Yes

#### Pricing Metrics
- **Floor Price** (`floor_price_usd`)
  - Source: `box_metrics_unified.floor_price_usd`
  - Format: Currency (USD)
  - Sortable: Yes

- **Floor Price Change %** (`floor_price_1d_change_pct`)
  - Source: `box_metrics_unified.floor_price_1d_change_pct`
  - Format: Percentage with sign (e.g., "-1.3%", "+4.7%")
  - Sortable: Yes

#### Volume Metrics
- **Daily Volume** (`unified_volume_usd`)
  - Source: `box_metrics_unified.unified_volume_usd`
  - Format: Currency (USD)
  - Sortable: Yes

- **Volume 7d EMA** (`unified_volume_7d_ema`)
  - Source: `box_metrics_unified.unified_volume_7d_ema`
  - Format: Currency (USD)
  - Sortable: Yes

#### Supply Metrics
- **Active Listings** (`active_listings_count`)
  - Source: `box_metrics_unified.active_listings_count`
  - Format: Integer
  - Sortable: Yes

- **Market Cap** (`visible_market_cap_usd`)
  - Source: `box_metrics_unified.visible_market_cap_usd`
  - Format: Currency (USD)
  - Sortable: Yes

#### Sales Metrics
- **Units Sold** (`units_sold_count`)
  - Source: `box_metrics_unified.units_sold_count`
  - Format: Integer
  - Sortable: Yes

- **Boxes Sold Per Day** (`boxes_sold_per_day`)
  - Source: `box_metrics_unified.boxes_sold_per_day`
  - Format: Decimal
  - Sortable: Yes

#### Supply Inflow
- **Boxes Added** (`boxes_added_today`)
  - Source: `box_metrics_unified.boxes_added_today`
  - Format: Integer
  - Sortable: Yes

#### Time-to-Price-Pressure
- **Days to +20%** (`days_to_20pct_increase`)
  - Source: `box_metrics_unified.days_to_20pct_increase`
  - Format: Decimal (or "N/A" if NULL)
  - Sortable: Yes

### Table Features
- **Sortable Columns**: All columns sortable
- **Default Sort**: Date (descending - newest first)
- **Export to CSV**: Future enhancement
- **Pagination**: If > 30 days of data

### Data Source
- **Endpoint**: `GET /api/v1/booster-boxes/{id}/time-series?metric=all&days=30`
- **Response**: Array of daily metric objects

---

## 5. Rank History

### Chart Data
- **X-Axis**: Date (time series)
- **Y-Axis**: Rank position (lower = better rank)
- **Metric**: Rank by volume (PRIMARY)

### Data Points
- **Date** (`date`)
  - Source: `box_metrics_unified.metric_date`

- **Volume Rank** (`volume_rank`)
  - Source: Calculated from `box_metrics_unified.unified_volume_7d_ema`
  - Calculation: `ROW_NUMBER() OVER (ORDER BY unified_volume_7d_ema DESC)`

- **Market Cap Rank** (`market_cap_rank`) - Optional
  - Source: Calculated from `box_metrics_unified.visible_market_cap_usd`
  - Calculation: `ROW_NUMBER() OVER (ORDER BY visible_market_cap_usd DESC)`

### Chart Features
- **Line Chart**: Show rank position over time
- **Inverted Y-Axis**: Lower rank number = higher position on chart
- **Highlight Changes**: Mark rank changes with visual indicators
- **Time Range**: Last 30 days default, with selector

### Data Source
- **Endpoint**: `GET /api/v1/booster-boxes/{id}/rank-history?days=30`
- **Response**: Array of `{date, volume_rank, market_cap_rank}` objects

---

## 6. Additional Context

### Box Information
- **Game Type** (`game_type`)
  - Source: `booster_boxes.game_type`
  - Display: Text (e.g., "One Piece", "MTG", "Pokemon")

- **Release Date** (`release_date`)
  - Source: `booster_boxes.release_date`
  - Format: Date (MM/DD/YYYY)
  - Display: "Released: January 15, 2024"

- **Reprint Risk** (`reprint_risk`)
  - Source: `booster_boxes.reprint_risk`
  - Values: `"LOW"`, `"MEDIUM"`, `"HIGH"`
  - Display: Badge with color coding
  - Color: Green (LOW), Yellow (MEDIUM), Red (HIGH)

- **Estimated Total Supply** (`estimated_total_supply`)
  - Source: `booster_boxes.estimated_total_supply`
  - Display: Number with formatting (e.g., "36,600" or "36.6K")
  - Optional: Used for listed percentage calculation

- **External Product ID** (`external_product_id`)
  - Source: `booster_boxes.external_product_id`
  - Display: Hidden or in metadata (for debugging/admin)

### Market Context
- **Absorption Rate** (Calculated)
  - Calculation: `boxes_sold_per_day / boxes_added_today` (if boxes_added_today > 0)
  - Display: Ratio (e.g., "2.3x" means selling 2.3x faster than supply added)
  - Label: "Absorption Rate"

- **Liquidity Warning** (Calculated)
  - Condition: `active_listings_count < 3`
  - Display: Warning badge "Low Liquidity"
  - Color: Yellow/Orange

- **Insufficient Data Badge** (Calculated)
  - Condition: Less than 7 days of historical data
  - Display: Badge "Insufficient Data"
  - Color: Gray

### Marketplace Attribution
- **Floor Price Source**: "TCGplayer" (authoritative)
- **Volume Source**: "Unified (TCGplayer 70% + eBay 30%)"
- **Supply Source**: "TCGplayer"

---

## 7. Time-Series Data

### Available Time-Series Metrics

#### Volume Metrics
- **Daily Volume** (`unified_volume_usd`)
- **Volume 7d EMA** (`unified_volume_7d_ema`)
- **Volume 30d SMA** (`volume_30d_sma`)

#### Price Metrics
- **Floor Price** (`floor_price_usd`)
- **Floor Price 1d Change %** (`floor_price_1d_change_pct`)

#### Supply Metrics
- **Active Listings** (`active_listings_count`)
- **Market Cap** (`visible_market_cap_usd`)
- **Boxes Added** (`boxes_added_today`)

#### Demand Metrics
- **Units Sold** (`units_sold_count`)
- **Boxes Sold Per Day** (`boxes_sold_per_day`)

#### Calculated Metrics
- **Days to +20%** (`days_to_20pct_increase`)
- **Liquidity Score** (`liquidity_score`)
- **Momentum Score** (`momentum_score`)

### Time-Series Endpoint
- **Endpoint**: `GET /api/v1/booster-boxes/{id}/time-series?metric={metric}&days={days}`
- **Parameters**:
  - `metric`: `volume`, `floor_price`, `market_cap`, `listings`, `sales`, `all`
  - `days`: Number of days (default: 30, max: 365)

---

## 8. Marketplace-Specific Metrics

### TCGplayer Metrics (Primary Marketplace)

#### Raw Data Available
- **TCG Volume USD** (`tcg_volume_usd`)
  - Source: `tcg_box_metrics_daily.tcg_volume_usd`
  - Display: Currency format

- **TCG Units Sold** (`tcg_units_sold_count`)
  - Source: `tcg_box_metrics_daily.tcg_units_sold_count`
  - Display: Integer

- **TCG Volume 7d EMA** (`tcg_volume_7d_ema`)
  - Source: `tcg_box_metrics_daily.tcg_volume_7d_ema`
  - Display: Currency format

- **TCG Volume 30d SMA** (`tcg_volume_30d_sma`)
  - Source: `tcg_box_metrics_daily.tcg_volume_30d_sma`
  - Display: Currency format

#### Supply Metrics
- **Boxes Added Today** (`boxes_added_today`)
  - Source: `tcg_box_metrics_daily.boxes_added_today`
  - Display: Integer

### eBay Metrics (Secondary Marketplace)

#### Raw Data Available
- **eBay Sales Count** (`ebay_sales_count`)
  - Source: `ebay_box_metrics_daily.ebay_sales_count`
  - Display: Integer

- **eBay Volume USD** (`ebay_volume_usd`)
  - Source: `ebay_box_metrics_daily.ebay_volume_usd`
  - Display: Currency format

- **eBay Median Sold Price** (`ebay_median_sold_price_usd`)
  - Source: `ebay_box_metrics_daily.ebay_median_sold_price_usd`
  - Display: Currency format

- **eBay Units Sold** (`ebay_units_sold_count`)
  - Source: `ebay_box_metrics_daily.ebay_units_sold_count`
  - Display: Integer

- **eBay Sales Acceleration** (`ebay_sales_acceleration`)
  - Source: `ebay_box_metrics_daily.ebay_sales_acceleration`
  - Display: Decimal (momentum indicator)

- **eBay Volume 7d EMA** (`ebay_volume_7d_ema`)
  - Source: `ebay_box_metrics_daily.ebay_volume_7d_ema`
  - Display: Currency format

### Unified Metrics (Combined)

#### Primary Metrics
- **Unified Volume USD** (`unified_volume_usd`)
  - Calculation: `(TCG × 0.7) + (eBay × 0.3)`
  - Source: `box_metrics_unified.unified_volume_usd`

- **Unified Volume 7d EMA** (`unified_volume_7d_ema`)
  - **PRIMARY RANKING METRIC**
  - Source: `box_metrics_unified.unified_volume_7d_ema`

#### Blended Metrics
- **Liquidity Score** (`liquidity_score`)
  - Calculation: Blended (50% TCG + 30% TCG velocity + 20% eBay)
  - Source: `box_metrics_unified.liquidity_score`

- **Momentum Score** (`momentum_score`)
  - Source: eBay-influenced, EMA smoothed
  - Source: `box_metrics_unified.momentum_score`

---

## 9. API Response Structure

### Detail Endpoint Response

**Endpoint**: `GET /api/v1/booster-boxes/{id}`

**Full Response Shape**:
```json
{
  "data": {
    "id": "uuid",
    "external_product_id": "tcgplayer-12345",
    "product_name": "One Piece - OP-05 Awakening of the New Era",
    "set_name": "OP-05",
    "game_type": "One Piece",
    "release_date": "2024-06-14",
    "image_url": "https://cdn.example.com/op-05-box.jpg",
    "estimated_total_supply": 36600,
    "reprint_risk": "LOW",
    
    "current_rank_by_volume": 1,
    "current_rank_by_market_cap": 3,
    "rank_change_direction": "up",
    "rank_change_amount": 2,
    
    "is_favorited": false,
    "favorited_at": null,
    
    "metrics": {
      "metric_date": "2024-01-15",
      
      "floor_price_usd": 245.99,
      "floor_price_1d_change_pct": -1.3,
      
      "unified_volume_usd": 45230.50,
      "unified_volume_7d_ema": 43890.25,
      "volume_30d_sma": 41200.00,
      
      "visible_market_cap_usd": 1250000.00,
      "active_listings_count": 3044,
      "listed_percentage": 8.3,
      
      "units_sold_count": 18,
      "boxes_sold_per_day": 18.2,
      "boxes_sold_30d_avg": 16.8,
      
      "boxes_added_today": 8,
      "boxes_added_7d_ema": 5.3,
      "boxes_added_30d_ema": 4.8,
      
      "days_to_20pct_increase": 12.5,
      "liquidity_score": 85.3,
      "momentum_score": 12.5
    },
    
    "marketplace_breakdown": {
      "tcgplayer": {
        "tcg_volume_usd": 42000.00,
        "tcg_units_sold_count": 15,
        "tcg_volume_7d_ema": 41000.00,
        "tcg_volume_30d_sma": 39000.00,
        "boxes_added_today": 8
      },
      "ebay": {
        "ebay_sales_count": 3,
        "ebay_volume_usd": 10770.00,
        "ebay_median_sold_price_usd": 3590.00,
        "ebay_units_sold_count": 3,
        "ebay_sales_acceleration": 0.5,
        "ebay_volume_7d_ema": 10000.00
      }
    }
  }
}
```

---

## 10. Display Priorities

### High Priority (Must Display)
1. **Floor Price** (large, prominent)
2. **Floor Price 24h Change %** (with arrow/color)
3. **Volume 7d EMA** (PRIMARY RANKING)
4. **Active Listings Count**
5. **Days to +20%**
6. **Price Chart** (30-day default)

### Medium Priority (Should Display)
7. **Liquidity Score**
8. **Market Cap**
9. **Boxes Sold Per Day**
10. **Listed Percentage**
11. **Rank History Chart**

### Low Priority (Nice to Have)
12. **Marketplace Breakdown** (TCG vs eBay)
13. **Supply Inflow Metrics**
14. **Advanced Metrics Table** (full time-series)
15. **Absorption Rate**

---

## 11. Data Quality Indicators

### Warnings to Display
- **Low Liquidity Warning**: `active_listings_count < 3`
- **Insufficient Data**: Less than 7 days of history
- **Unreliable Days to +20%**: `active_listings_count < 5`
- **No Sales Detected**: `units_sold_count == 0` for current day

### Null Handling
- Display "N/A" or "--" for NULL values
- Don't show calculations that require NULL inputs
- Show "Insufficient Data" badge when needed

---

## 12. Summary

### Total Metrics Count
- **Header Section**: 5 fields
- **Key Metrics Card**: 15+ metrics
- **Price Chart**: 1 metric (floor_price) with time-series
- **Advanced Metrics Table**: 10+ columns
- **Rank History**: 1-2 metrics (volume rank, market cap rank)
- **Additional Context**: 6+ fields
- **Marketplace Breakdown**: 10+ metrics

### Total Data Points Needed
- **Current State**: ~40+ individual metrics
- **Time-Series Data**: 30+ days × 10+ metrics = 300+ data points
- **Rank History**: 30+ days × 1-2 metrics = 30-60 data points

### API Endpoints Required
1. `GET /api/v1/booster-boxes/{id}` - Main detail data
2. `GET /api/v1/booster-boxes/{id}/time-series?metric=floor_price&days=30` - Price chart
3. `GET /api/v1/booster-boxes/{id}/time-series?metric=all&days=30` - Advanced table
4. `GET /api/v1/booster-boxes/{id}/rank-history?days=30` - Rank history
5. `POST /api/v1/users/me/favorites/{id}` - Add favorite (if authenticated)
6. `DELETE /api/v1/users/me/favorites/{id}` - Remove favorite (if authenticated)

---

**Last Updated**: 2025-01-01
**Status**: Complete mapping based on all planning documents


