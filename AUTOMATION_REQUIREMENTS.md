# Screenshot Automation System - Integration Requirements

## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions


## CORE REQUIREMENT: FULL AUTOMATION

**The ENTIRE purpose of this system is FULL AUTOMATION - zero manual intervention required.**

User sends screenshot → System automatically processes everything → All data automatically appears in all applicable fields.

See `CORE_REQUIREMENT.md` for complete automation requirements.

## Overview

The screenshot automation system must **automatically and accurately** populate all metrics fields that are displayed in:
1. **Main Leaderboard Table** (`/dashboard`)
2. **Box Detail Pages** (`/boxes/[id]`)

All data extracted from screenshots must flow automatically into the database and be immediately available in both views.

**NO manual data entry. NO manual calculations. NO manual updates. Everything must be AUTOMATIC.**

## Critical: Volume Metrics Automation

**ALL volume metrics MUST be automatically calculated and populated** - no manual input required:
- Daily volume (`unified_volume_usd`)
- 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
- 30-day volume SMA (`unified_volume_30d_sma`)
- Month-over-month volume change (`volume_mom_change_pct`)

All volume calculations run automatically from sales data extracted from screenshots.

---

## Fields Required for Leaderboard Table

Based on `frontend/components/leaderboard/LeaderboardTable.tsx`, the leaderboard displays:

### Core Metrics (Always Visible)
- `floor_price_usd` - Current floor price
- `floor_price_30d_change_pct` - 30-day price change percentage
- `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
- `active_listings_count` - Total active listings
- `boxes_sold_per_day` - Boxes sold per day
- `liquidity_score` - Liquidity score

### Ranking System
- Rankings calculated based on `unified_volume_7d_ema` (primary)
- Rankings must update automatically when data changes
- Daily, weekly, and monthly rankings must be maintained

---

## Fields Required for Box Detail Pages

Based on `frontend/app/(dashboard)/boxes/[id]/page.tsx`, box detail pages display:

### Primary Price Metrics
- `floor_price_usd` - Current floor price
- `floor_price_1d_change_pct` - 24-hour price change percentage
- `days_to_20pct_increase` - Days to +20% price increase
- `expected_time_to_sale_days` - Expected time to sale (uses `expected_days_to_sell`)

### Market Cap and Liquidity
- `visible_market_cap_usd` - Visible market cap
- `boxes_added_7d_ema` OR `boxes_added_30d_ema` - Avg added per day
- `active_listings_count` - Boxes listed
- `liquidity_score` - Liquidity score

### Supply & Demand Metrics
- `boxes_sold_per_day` - Sold per day
- `top_10_value_usd` - Top 10 cards value (if applicable)
- `boxes_added_today` - Added today

### Charts and Time Series
- Price history over time (`floor_price_usd` over dates)
- Volume history over time (`unified_volume_usd` over dates)
- All metrics must support time series data

---

## Automation Flow Requirements

### 1. Data Extraction from Screenshots
When user sends screenshot with "This is data for [BOX NAME]":

```
Screenshot → AI Extraction → Structured Data
```

**Extracted Fields:**
- Floor price (price + shipping) - TCGPlayer only
- Active listings (count + price ladder data) - eBay + TCGPlayer
- Sales data (price, quantity, date) - eBay + TCGPlayer
- New listings detected (for boxes_added_today)

### 2. Data Processing & Calculation
All calculations must run automatically:

```
Raw Data → Calculations → Derived Metrics → Database
```

**Calculations Required:**
1. Floor price (direct from screenshot)
2. Floor price 1d change (compare to previous day)
3. Floor price 30d change (compare to 30 days ago)
4. **Volume Metrics (ALL MUST AUTO-CALCULATE)**:
   - Daily volume (`unified_volume_usd`) - Sum of sales for current day
   - 7-day volume EMA (`unified_volume_7d_ema`) - PRIMARY RANKING METRIC
   - 30-day volume SMA (`unified_volume_30d_sma`) - 30-day simple moving average
   - Month-over-month volume change (`volume_mom_change_pct`) - MoM percentage change
5. Boxes sold per day (current + 30d avg)
6. Boxes added per day (current + 30d avg + 7d/30d EMA)
7. Active listings count
8. Days to 20% increase (T₊ / net_burn_rate)
9. Expected days to sell
10. Liquidity score
11. Visible market cap
12. Rankings (daily, weekly, monthly)

### 3. Database Update
All metrics must be automatically saved to:

**Primary Table:** `box_metrics_unified` (UnifiedBoxMetrics model)

**Fields to Update:**
- All extracted fields
- All calculated fields
- Timestamps (created_at, updated_at)
- Date (metric_date)

### 4. API Data Flow
Data must flow automatically from database to API:

```
Database → API Endpoints → Frontend
```

**Required API Endpoints:**
- `GET /api/v1/leaderboard` - Returns all boxes with metrics for leaderboard
- `GET /api/v1/boxes/[id]` - Returns single box with all metrics for detail page
- `GET /api/v1/boxes/[id]/time-series` - Returns time series data for charts

### 5. Frontend Display
All metrics must be immediately visible in:

**Leaderboard Table:**
- All metrics update automatically
- Rankings recalculate automatically
- Sorting works on all metrics

**Box Detail Pages:**
- All metrics display correctly
- Charts update with new data points
- Time series data includes new entries

---

## Critical Requirements

### 1. Real-Time Updates
- Data must be available immediately after screenshot processing
- No manual refresh required (or automatic refresh after processing)
- Rankings update automatically

### 1a. Volume Metrics Automation (CRITICAL)
**ALL volume metrics MUST be automatically calculated and populated:**
- `unified_volume_usd` (Daily volume) - Automatically calculated from sales data
- `unified_volume_7d_ema` (7-day EMA) - Automatically calculated (PRIMARY RANKING METRIC)
- `unified_volume_30d_sma` (30-day SMA) - Automatically calculated
- `volume_mom_change_pct` (MoM change) - Automatically calculated
- **No manual calculation or input required for any volume metrics**
- All volume metrics must update automatically when new sales data is added

### 2. Data Accuracy
- All calculations must follow `CALCULATION_SPECIFICATION.md` exactly
- No manual intervention required
- Duplicate detection must prevent data corruption
- Filtering rules must be applied (JP filter, 25% below floor filter)

### 3. Complete Field Coverage
Every field displayed in the UI must be:
- Extracted from screenshots OR
- Calculated from extracted data OR
- Derived from historical data

**No manual data entry should be required** for metrics displayed in:
- Leaderboard table
- Box detail pages

### 4. Price Ladder Data
For "Days to 20% Increase" calculation:
- Must extract individual listing prices and quantities from screenshots
- Calculate T₊ (inventory below +20% tier) automatically
- Store temporarily during processing (not permanently)
- Use for calculation, then discard

### 5. Historical Data Integration
- All new data must integrate with historical data
- Averages and EMAs must recalculate with new data
- Time series must include new data points
- Rankings must recalculate with new metrics

---

## Implementation Checklist

### Data Extraction
- [ ] Extract floor price (price + shipping) from TCGPlayer
- [ ] Extract individual listings with: price, quantity, seller, title, platform
- [ ] Extract individual sales with: price, quantity, date, seller, title, platform
- [ ] Apply eBay filtering: Only count listings/sales where title matches booster box name (use best judgment)
- [ ] Apply general filtering: Exclude "JP" in title, exclude 25%+ below floor price
- [ ] Detect duplicates: Compare seller + price + quantity + date/platform - skip exact matches
- [ ] Extract price ladder data (prices + quantities from filtered listings) for T₊ calculation
- [ ] Detect new listings (compare seller + quantity + platform to previous data)
- [ ] Calculate active listings count from filtered, non-duplicate listings
- [ ] Aggregate sales data from filtered, non-duplicate sales

### Calculations
- [ ] Calculate all direct metrics (floor_price, listings_count, etc.)
- [ ] Calculate derived metrics (1d change, 30d change, EMAs, SMAs)
- [ ] **Calculate ALL Volume Metrics (REQUIRED)**:
  - [ ] Daily volume (`unified_volume_usd`) - Sum of sales for current day
  - [ ] 7-day volume EMA (`unified_volume_7d_ema`) - Exponential moving average (alpha=0.3)
  - [ ] 30-day volume SMA (`unified_volume_30d_sma`) - Simple moving average
  - [ ] Month-over-month volume change (`volume_mom_change_pct`) - Percentage change
- [ ] Calculate Days to 20% Increase (T₊ / net_burn_rate)
- [ ] Calculate Expected Days to Sell
- [ ] Calculate Liquidity Score
- [ ] Calculate Visible Market Cap
- [ ] Calculate Rankings (daily, weekly, monthly)

### Database Integration
- [ ] Save all metrics to `box_metrics_unified` table
- [ ] Update existing records or create new ones
- [ ] Handle date-based records correctly
- [ ] Update timestamps
- [ ] Ensure data integrity (no duplicates)

### API Integration
- [ ] Leaderboard API returns all required fields
- [ ] Box detail API returns all required fields
- [ ] Time series API includes new data points
- [ ] Rankings are included in API responses
- [ ] All metrics are formatted correctly

### Frontend Integration
- [ ] Leaderboard table displays all metrics
- [ ] Box detail pages display all metrics
- [ ] Charts update with new data
- [ ] Rankings update automatically
- [ ] All fields show correct data types (currency, percentage, numbers)

---

## Field Mapping: Screenshot Data → UI Fields

### Leaderboard Table Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction (price + shipping) |
| 30d Change | `floor_price_30d_change_pct` | Historical data | Compare to 30 days ago |
| Volume | `unified_volume_7d_ema` | Sales data | **7-day EMA of daily volumes (AUTO-CALCULATED)** |
| Listings | `active_listings_count` | Screenshot (eBay + TCGPlayer) | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Liquidity | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Note**: Volume metric (`unified_volume_7d_ema`) is the PRIMARY RANKING METRIC and must be automatically calculated from aggregated sales data.

### Box Detail Page Fields
| UI Field | Database Field | Source | Calculation |
|----------|---------------|--------|-------------|
| Floor Price | `floor_price_usd` | Screenshot (TCGPlayer) | Direct extraction |
| 24h Change | `floor_price_1d_change_pct` | Historical data | Compare to previous day |
| Days to +20% | `days_to_20pct_increase` | Price ladder + sales | T₊ / net_burn_rate |
| Expected Time to Sale | `expected_days_to_sell` | Listings + sales | listings / sold_per_day |
| Market Cap | `visible_market_cap_usd` | Floor price + supply | floor_price × estimated_supply |
| Avg Added/Day | `avg_boxes_added_per_day` | New listings | 30d average (capped) |
| Boxes Listed | `active_listings_count` | Screenshot | Count all listings |
| Sold/Day | `boxes_sold_per_day` | Sales data | Current or 30d avg |
| Added Today | `boxes_added_today` | New listings detected | Count new listings |
| Liquidity Score | `liquidity_score` | Calculated | MIN(1.0, listings / (sold_per_day × 7)) |

**Volume Metrics (ALL AUTO-CALCULATED):**
- `unified_volume_usd` - Daily volume (used in charts/time series)
- `unified_volume_7d_ema` - 7-day EMA volume (used for rankings)
- `unified_volume_30d_sma` - 30-day SMA volume (used for monthly rankings)
- `volume_mom_change_pct` - Month-over-month volume change (trend analysis)

**All volume metrics are automatically calculated from sales data - no manual input required.**

---

## Testing Requirements

### Automated Testing
- [ ] Screenshot data extraction works correctly
- [ ] All calculations match specification
- [ ] Database updates correctly
- [ ] API returns correct data
- [ ] Frontend displays correct data
- [ ] Rankings update correctly
- [ ] Time series data includes new points

### Manual Testing
- [ ] Send screenshot → verify data appears in leaderboard
- [ ] Send screenshot → verify data appears in box detail page
- [ ] Verify all metrics are accurate
- [ ] Verify rankings update correctly
- [ ] Verify charts update with new data
- [ ] Verify no duplicate data
- [ ] Verify filtering works (JP, 25% below floor)

---

## Success Criteria

The automation system is successful when:

1. ✅ User sends screenshot with box name
2. ✅ System extracts all data automatically
3. ✅ All calculations run automatically
4. ✅ **ALL volume metrics calculate automatically** (daily, 7d EMA, 30d SMA, MoM change)
5. ✅ Data saves to database automatically
6. ✅ Leaderboard table updates automatically
7. ✅ Box detail page updates automatically
8. ✅ Rankings recalculate automatically (based on volume metrics)
9. ✅ Charts include new data points (including volume data)
10. ✅ No manual intervention required
11. ✅ All fields display accurately
12. ✅ **Volume metrics are primary ranking driver and update in real-time**

---

## Extensibility Requirements

**The system must be designed for future extensibility:**

- **Modular Calculations**: Each metric calculation should be a separate, pluggable module
- **Easy to Add Metrics**: New metrics can be added without refactoring existing code
- **Database Extensible**: Schema supports adding new metric fields via migrations
- **API Extensible**: New metrics automatically included in API responses
- **Configuration-Driven**: Metric definitions and calculations can be extended via configuration
- **Backward Compatible**: Adding new metrics doesn't break existing functionality

When new metrics are needed in the future, they should be:
1. Defined in calculation specification
2. Added to database schema (migration)
3. Implemented as modular calculation function
4. Registered in calculation system
5. Automatically included in API responses
6. Optionally displayed in frontend

---

## Notes

- Price ladder data (T₊) must be extracted but not stored permanently
- All calculations must follow `CALCULATION_SPECIFICATION.md`
- Duplicate detection is critical - must prevent duplicate data entry
- Filtering rules must be applied consistently (JP filter, 25% below floor)
- Rankings must update in real-time as data changes
- Time series data must be maintained for charts
- System must be extensible for future metric additions

