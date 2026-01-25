# Calculation Specification

This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements


This document defines the exact calculation rules for all metrics in the BoosterBoxPro system. All calculations must follow these specifications precisely.

## Data Entry Workflow

The system starts with the user declaring: **"This is data for [BOX NAME]"**

Example: "This is data for OP-01"

---

## 1. Floor Price

### Source
- **Platform**: TCGPlayer ONLY (authoritative source - NOT eBay)
- **Extraction**: From screenshot
- **Calculation**: Price + Shipping = Total Floor Price

### Rules
- Extract the lowest listing price visible from TCGPlayer
- **MUST add shipping cost** to the listing price
- If shipping is free, use listing price as-is
- If multiple listings show same price, use the one with lowest total (price + shipping)
- **Filtering**: Exclude listings with "JP" in title or description
- **Filtering**: Exclude listings that are 25% or more below current floor price
- Store as `floor_price_usd` (Decimal, 2 decimal places)

### Example
- Listing price: $120.00
- Shipping: $5.50
- **Floor Price = $125.50**

---

## 2. Active Listings

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms)
- **Data to Extract from Screenshots**: 
  - **Individual listings** with:
    - Price of each listing (price + shipping)
    - Quantity available for each listing
    - Listing title/description
    - Seller identifier (internal use only - NOT disclosed/stored)
    - Platform identifier (eBay or TCGPlayer)
    - Date/listing ID (for duplicate detection)

### Filtering Rules
- **Exclude**: Listings with "JP" in title or description
- **Exclude**: Listings that are 25% or more below current floor price
- **eBay-Specific**: Only count listings where title matches the booster box name (use best judgment to identify legitimate matches)
- **Very Important**: Do NOT input duplicate data - check carefully before adding

### Duplicate Detection for Listings
- Compare seller + price + quantity + platform + listing ID/date
- If exact match found in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

### Storage Rules
- **Public Data** (stored and displayed):
  - `active_listings_count`: Total count of listings from both platforms (integer)

- **Internal Data** (used for calculations and duplicate detection, NOT stored permanently):
  - Individual listing prices (price + shipping) - **REQUIRED for price ladder calculations**
  - Individual listing quantities - **REQUIRED for price ladder calculations (T₊)**
  - Seller identifiers - used for duplicate detection
  - Individual listing details - used to detect if listing is new or existing
  - Platform identifiers
  - **Price ladder data**: Must be maintained in memory/processing to calculate T₊ for "Days to 20% Increase"

### Duplicate Detection
- Use seller info + price + quantity + platform to determine if a listing is:
  - **New**: First time seeing this seller+price+quantity+platform combination
  - **Existing/Updated**: Same seller+quantity+platform but price changed (count as UPDATE, not new listing)
  - **Duplicate**: Exact same seller+price+quantity+platform (skip, do not count)
- Track listings internally to calculate `boxes_added_today` (new listings only, not price updates)

### Calculation
- Count all listings visible in screenshot
- Store total count as `active_listings_count`
- Use individual listing data internally to determine new vs existing listings

---

## 3. Sales Data

### Source
- **Platforms**: TCGPlayer and eBay (treated equally)
- **Extraction**: From sales screenshots
- **Data Points**: Individual sale records with price, quantity, date

### Sales Data Structure
Each sale should include:
- `price_usd`: Sale price (price + shipping if applicable)
- `quantity`: Number of boxes sold in this transaction
- `date`: Date of sale (ISO format: YYYY-MM-DD)
- `platform`: "tcgplayer" or "ebay" (for tracking, but treated equally)

### Volume Calculations

#### Daily Volume (`daily_volume_usd`)
- Sum of all sales for the current day
- Formula: `SUM(price_usd × quantity)` for all sales where `date = today`
- Store as `unified_volume_usd` (Decimal, 2 decimal places)

#### 7-Day Volume (`unified_volume_7d_ema`)
- Exponential Moving Average (EMA) of daily volumes over last 7 days
- Alpha (smoothing factor): 0.3
- Formula: `EMA(volumes[-7:], alpha=0.3)`
- Store as `unified_volume_7d_ema` (Decimal, 2 decimal places)

#### 30-Day Volume (`unified_volume_30d_sma`)
- Simple Moving Average (SMA) of daily volumes over last 30 days
- Formula: `SUM(volumes[-30:]) / 30`
- Store as `unified_volume_30d_sma` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Sales Count Calculations

#### Boxes Sold Today (`boxes_sold_today`)
- Count of boxes sold on current day
- Formula: `SUM(quantity)` for all sales where `date = today`
- Store as `boxes_sold_per_day` (current day value, Decimal, 2 decimal places)

#### Daily Sales Average (`boxes_sold_30d_avg`)
- Average boxes sold per day over last 30 days
- Formula: `SUM(quantities[-30:]) / 30` (if 30 days available) or `SUM(quantities) / days_available` (if less than 30 days)
- Store as `boxes_sold_30d_avg` (Decimal, 2 decimal places)

### Sales Data Aggregation
- Congregate (combine) all sales from screenshots (eBay and TCGPlayer)
- Each screenshot may contain multiple sales
- Aggregate sales by date
- Use aggregated totals for volume and sales calculations
- **Very Important**: Do NOT input duplicate sales - check carefully before adding

### Filtering Rules
- **Exclude**: Sales with "JP" in title or description
- **Exclude**: Sales that are 25% or more below current floor price (filter "super low sales")
- **eBay-Specific**: Only count sales where title/description matches the booster box name (use best judgment for legitimate matches)
- **Duplicate Detection**: Check seller + price + quantity + date + platform - if exact match exists, SKIP (duplicate)

### Implementation Notes
- Treat eBay and TCGPlayer sales equally (no weighting)
- Filter out anomalously low sales (25% below floor price threshold)

---

## 4. Average New Listings Per Day

### Source
- **Platforms**: eBay AND TCGPlayer (both platforms combined)
- **Data**: New listings detected from screenshots

### Calculation
- Track new listings (first time seeing a seller+quantity+platform combination)
- Count new listings per day from both platforms: `boxes_added_today`
- Calculate 30-day moving average of new listings per day
- Formula: `SUM(boxes_added_today[-30:]) / 30`
- **Cap at 30-day average**: The ongoing average cannot exceed the 30-day average
- Store as `avg_boxes_added_per_day` (Decimal, 2 decimal places)
- If less than 30 days of data: `SUM(boxes_added_today) / days_available`
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Detection Logic
- Compare current screenshot listings to previous listings (by seller identifier + platform + quantity)
- If seller+quantity+platform is new → count as new listing
- If seller+quantity+platform exists but price changed → count as UPDATE (not new listing)
- If seller+quantity+platform exists in previous data with same price → duplicate (skip)
- **eBay listings**: Only process if title matches booster box name (use best judgment)
- Track internally (seller info not stored, only used for detection)

---

## 5. Month Over Month Volume

### Calculation
- Compare total volume of current month to previous month
- Formula: `((current_month_volume - previous_month_volume) / previous_month_volume) × 100`
- Store as `volume_mom_change_pct` (Decimal, 2 decimal places)
- **Status**: ❌ NEEDS TO BE ADDED to database model

### Implementation
- Aggregate daily volumes by month
- Use first day of month entries or monthly totals
- Calculate percentage change between consecutive months
- Update automatically when new month data is available

### Example
- Previous month total volume: $10,000
- Current month total volume: $12,000
- **MoM Change = ((12000 - 10000) / 10000) × 100 = +20.00%**

---

## 6. Days to 20% Floor Price Increase

### Purpose
Calculate how many days until the market clears enough inventory below the +20% price tier to cause the floor price to increase by 20%. This is a **net supply tightening model**.

**Important**: We are NOT estimating days until total listings drop by 20%. We are estimating days until the market clears the "price ladder" up to the +20% tier (i.e., all listings priced below 1.2× the current floor), adjusted for new supply entering daily.

### Variables
- **P₀** = current floor price
- **P₊** = target price = 1.2 × P₀ (20% increase from current floor)
- **T₊** = "inventory to clear until +20%" = total quantity listed at prices BELOW P₊ (price ladder depth)
- **S** = average boxes sold per day (30-day average)
- **A** = average boxes added to listings per day (30-day average)
- **Net burn rate** = S - A (key addition: new listings slow down the clearance)

### Formula
```
P₊ = floor_price_usd × 1.2
T₊ = SUM(quantities of listings where price < P₊)
net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
days_to_20pct_increase = T₊ / net_burn_rate
```

### Components
1. **Target price (P₊)**: 20% above current floor
   - `P₊ = floor_price_usd × 1.2`

2. **Inventory to clear (T₊)**: Total quantity of boxes listed below target price
   - `T₊ = SUM(quantity)` for all listings where `(price + shipping) < P₊`
   - This requires price ladder data (individual listing prices and quantities)
   - Only count listings priced below the +20% tier

3. **Net burn rate**: Net daily reduction in supply
   - `net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day`
   - If `net_burn_rate <= 0`, supply is NOT tightening → return `None` (or show "Not tightening")
   - New listings slow down the clearance process

4. **Days calculation**: How many days at current net burn rate to clear inventory below +20% tier
   - `days_to_20pct_increase = T₊ / net_burn_rate`
   - Only calculate if `net_burn_rate > 0`
   - If `net_burn_rate <= 0`, return `None` (supply not tightening)

### Logic
- As listings below the +20% price tier are sold, the floor price will eventually increase to that tier
- New listings added daily slow down this process (reduce net burn rate)
- Uses 30-day moving averages for boxes sold and boxes added to smooth out daily fluctuations
- Requires price ladder data (listing prices and quantities) to calculate T₊

### Example
- Current floor price (P₀): $100
- Target price (P₊): $120 (1.2 × $100)
- Inventory below $120 (T₊): 10 boxes (sum of quantities for all listings priced < $120)
- Average boxes sold/day (S): 1.0
- Average boxes added/day (A): 0.2
- Net burn rate: 1.0 - 0.2 = 0.8 boxes/day
- **Days to +20% = 10 / 0.8 = 12.5 days**

### Guardrails (UI Safety)
- If `net_burn_rate < 0.05` (very small): Return `None` or show "Not tightening"
- Clamp maximum days at 180 (if result > 180, show 180 or ">180 days")
- Require minimum history (7-14 days) before showing the metric
- If `net_burn_rate <= 0`: Return `None` or show "Supply not tightening"

### Edge Cases
- If `boxes_sold_30d_avg` is 0 or None: Return `None`
- If `avg_boxes_added_per_day` is None: Use 0
- If `net_burn_rate <= 0`: Return `None` (supply not tightening)
- If `T₊ = 0` (no listings below +20% tier): Return `None` or 0 (already at/above +20%)
- If price ladder data unavailable: Cannot calculate T₊ → Return `None`
- If any required component is missing: Return `None`
- If `net_burn_rate < 0.05`: Return `None` (too slow to be meaningful)

### Data Requirements
- **Price ladder data**: Individual listing prices (price + shipping) and quantities
- **Screenshots provide**: Individual listings with price, quantity, seller, title
- Extract price ladder data from screenshots to calculate T₊
- Store internally for calculation (not persisted individually, only used to calculate T₊)
- **eBay listings**: Only include listings where title matches booster box name (use best judgment)

Store as `days_to_20pct_increase` (Decimal, 2 decimal places, nullable)

---

## Additional Calculations (Derived Metrics)

### 7. Floor Price 1-Day Change Percentage

**Formula**: `((current_floor_price - previous_floor_price) / previous_floor_price) × 100`

Store as `floor_price_1d_change_pct` (Decimal, 2 decimal places, nullable)

---

### 8. Listed Percentage

**Formula**: `(active_listings_count / estimated_total_supply) × 100`

Only calculate if `estimated_total_supply` is available.

Store as `listed_percentage` (Decimal, 2 decimal places, nullable)

---

### 9. Visible Market Cap

**Formula**: `floor_price_usd × estimated_total_supply`

Only calculate if both values are available.

Store as `visible_market_cap_usd` (Decimal, 2 decimal places, nullable)

---

### 10. Expected Days to Sell (Expected Time to Sale)

**Purpose**: Calculate how long it will take to sell all current listings at the current sales rate

**Formula**: `active_listings_count / boxes_sold_per_day`

**Components**:
- `active_listings_count`: Total active listings from eBay + TCGPlayer
- `boxes_sold_per_day`: Current day's boxes sold (or use `boxes_sold_30d_avg` for smoother estimate)

**Calculation Method**:
- Use `boxes_sold_per_day` if available for current day
- Fallback to `boxes_sold_30d_avg` if daily value not available
- Only calculate if `boxes_sold_per_day > 0` or `boxes_sold_30d_avg > 0`

**Example**:
- Active listings: 100
- Boxes sold per day: 5
- **Expected days to sell = 100 / 5 = 20 days**

Store as `expected_days_to_sell` (Decimal, 2 decimal places, nullable)

---

### 11. Liquidity Score

**Formula**: `MIN(1.0, active_listings_count / (boxes_sold_per_day × 7))`

- Represents how many weeks of inventory at current sales rate
- Capped at 1.0 (1 week or less)
- Only calculate if `boxes_sold_per_day > 0`

Store as `liquidity_score` (Decimal, 2 decimal places, nullable)

---

## Data Storage Requirements

### Fields That Need to be Stored

#### Directly Extracted (from screenshots)
- `floor_price_usd` - Floor price (price + shipping)
- `active_listings_count` - Count of active listings
- `boxes_sold_today` - Boxes sold today (aggregated from sales)
- `daily_volume_usd` - Daily volume (sum of sales)
- `boxes_added_today` - New listings detected today

#### Calculated (derived from historical data)
- `floor_price_1d_change_pct` - 1-day price change
- `unified_volume_usd` - Daily volume (same as daily_volume_usd)
- `unified_volume_7d_ema` - 7-day EMA of volume
- `unified_volume_30d_sma` - 30-day SMA of volume (may need to add to model)
- `boxes_sold_per_day` - Current day boxes sold
- `boxes_sold_30d_avg` - 30-day average boxes sold per day
- `avg_boxes_added_per_day` - 30-day average new listings per day (capped at 30d avg)
- `volume_mom_change_pct` - Month-over-month volume change (may need to add to model)
- `days_to_20pct_increase` - Days until 20% price increase (net supply tightening model using price ladder T₊)
- `listed_percentage` - Percentage of supply listed
- `visible_market_cap_usd` - Market cap calculation
- `expected_days_to_sell` - Expected days to sell all listings
- `liquidity_score` - Liquidity metric

### Fields NOT Stored Permanently (Internal Use Only)
- Individual listing prices - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Individual listing quantities - **BUT REQUIRED during processing for price ladder/T₊ calculation**
- Seller identifiers
- Individual sale records (only aggregated totals stored)
- Price ladder data (used to calculate T₊, then discarded)

**Note**: Price ladder data (individual listing prices and quantities) must be maintained during processing to calculate T₊ for "Days to 20% Increase", but is not stored permanently in the database.

---

## Calculation Execution Order

When processing new screenshot data:

1. **Extract raw data** from screenshot
   - Floor price (price + shipping) - TCGPlayer only
   - Individual listings with: price, quantity, seller, title, platform - **REQUIRED for price ladder/T₊ calculation**
   - Individual sales with: price, quantity, date, seller, title, platform
   - Apply filtering:
     - eBay: Only count listings/sales where title matches booster box name
     - Exclude "JP" in title/description
     - Exclude listings/sales 25%+ below floor price
     - Detect and skip duplicates (seller + price + quantity + date/platform)
   - Active listings count = count of filtered listings

2. **Detect new listings** (compare to previous data)
   - Compare each listing: seller + quantity + platform
   - If new (not seen before) → count as new listing
   - If exists but price changed → UPDATE (not new)
   - If exact duplicate → SKIP
   - Calculate `boxes_added_today` = count of new listings (after filtering)

3. **Aggregate sales data** (after filtering and duplicate detection)
   - Filter sales: eBay title must match box name, exclude JP, exclude 25%+ below floor
   - Check duplicates: seller + price + quantity + date + platform
   - Skip duplicate sales
   - Calculate `daily_volume_usd` (sum of legitimate, non-duplicate sales)
   - Calculate `boxes_sold_today` (sum of quantities from legitimate, non-duplicate sales)

4. **Store raw entry** in historical data

5. **Calculate derived metrics** from historical data:
   - Floor price 1d change
   - 7-day volume EMA
   - 30-day volume SMA
   - 30-day average boxes sold
   - 30-day average boxes added (capped)
   - Month-over-month volume change
   - Days to 20% increase (requires price ladder data for T₊ calculation)
   - Other derived metrics

6. **Update unified metrics** in database/JSON

---

## 12. Rankings (Daily, Weekly, Monthly)

### Purpose
Keep running counts of volume and all statistics to maintain active and moving rankings in the leaderboard. Rankings fluctuate based on daily, weekly, and monthly time periods.

### Ranking Metrics
Rankings should be calculated for:
- **Daily Rankings**: Based on current day metrics (floor_price_usd, unified_volume_usd, etc.)
- **Weekly Rankings**: Based on 7-day averages (unified_volume_7d_ema, boxes_sold_30d_avg, etc.)
- **Monthly Rankings**: Based on 30-day averages (unified_volume_30d_sma, monthly totals, etc.)

### Ranking Criteria
Primary ranking metrics (in order of importance):
1. `unified_volume_7d_ema` - 7-day EMA volume (PRIMARY RANKING METRIC)
2. `unified_volume_30d_sma` - 30-day SMA volume
3. `floor_price_usd` - Current floor price
4. `boxes_sold_30d_avg` - 30-day average sales
5. `liquidity_score` - Liquidity metric

### Implementation
- Calculate rankings after each data update
- Update rankings for all time periods (daily, weekly, monthly)
- Store rankings in leaderboard data structure
- Rankings should update automatically as new data is added

### Ranking Calculation
- Sort boxes by ranking metric (descending for volume/price, ascending for days_to_sell)
- Assign rank 1, 2, 3, etc.
- Handle ties appropriately (same rank, skip next rank number)

---

## Additional Recommended Calculations

### 13. Floor Price 30-Day Change
- Similar to 1-day change, but 30-day
- Useful for trend analysis
- Formula: `((current_price - price_30d_ago) / price_30d_ago) × 100`
- Store as `floor_price_30d_change_pct` (Decimal, 2 decimal places, nullable)

### 14. Sales Velocity
- Rate of sales acceleration/deceleration
- Measures change in sales rate over time
- Formula: `((current_boxes_sold_30d_avg - previous_boxes_sold_30d_avg) / previous_boxes_sold_30d_avg) × 100`
- Store as `sales_velocity_pct` (Decimal, 2 decimal places, nullable)

### 15. Supply Velocity
- Rate of new listings acceleration/deceleration
- Measures change in listing addition rate over time
- Formula: `((current_avg_boxes_added - previous_avg_boxes_added) / previous_avg_boxes_added) × 100`
- Store as `supply_velocity_pct` (Decimal, 2 decimal places, nullable)

### 16. Volume Velocity
- Rate of volume acceleration/deceleration
- Measures change in volume over time
- Formula: `((current_volume_30d_sma - previous_volume_30d_sma) / previous_volume_30d_sma) × 100`
- Store as `volume_velocity_pct` (Decimal, 2 decimal places, nullable)

---

## Implementation Notes

### Data Sources Priority
1. **Floor Price**: TCGPlayer ONLY (authoritative source - NOT eBay)
2. **Listings**: eBay AND TCGPlayer (both platforms combined)
3. **Sales**: eBay AND TCGPlayer (treated equally, no weighting)

### Filtering Rules
- **JP Filter**: Exclude anything with "JP" in title or description (listings AND sales)
- **Low Price Filter**: Exclude listings/sales that are 25% or more below current floor price
- **Platform Equality**: eBay and TCGPlayer sales/listings are treated identically (no weighting)
- **Duplicate Prevention**: Very important - do NOT input duplicate data - check carefully before adding

### Historical Data Requirements
- Store all raw entries to enable historical calculations
- Track dates for time-based calculations (7d, 30d, MoM)
- Maintain seller identifiers internally (in memory/during processing) but do NOT persist them

### Calculation Accuracy
- All currency values: 2 decimal places
- All percentages: 2 decimal places
- All counts: Integers (no decimals)
- All day calculations: 2 decimal places

---

## Database Model Field Status

### Fields That Exist in Database Model
✅ `floor_price_usd` - EXISTS
✅ `floor_price_1d_change_pct` - EXISTS
✅ `unified_volume_usd` - EXISTS
✅ `unified_volume_7d_ema` - EXISTS
✅ `boxes_sold_per_day` - EXISTS
✅ `boxes_sold_30d_avg` - EXISTS
✅ `active_listings_count` - EXISTS
✅ `boxes_added_today` - EXISTS
✅ `visible_market_cap_usd` - EXISTS
✅ `days_to_20pct_increase` - EXISTS
✅ `listed_percentage` - EXISTS
✅ `expected_days_to_sell` - EXISTS
✅ `liquidity_score` - EXISTS
✅ `momentum_score` - EXISTS

### Fields That Need to be Added to Database Model
❌ `unified_volume_30d_sma` - NEEDS TO BE ADDED (30-day SMA of volume)
❌ `volume_mom_change_pct` - NEEDS TO BE ADDED (month-over-month volume change percentage)
❌ `avg_boxes_added_per_day` - NEEDS TO BE ADDED (30-day average of boxes added per day)

### Recommended Fields to Add (from recommendations section)
- `floor_price_30d_change_pct` - 30-day price change percentage
- `sales_velocity_pct` - Sales velocity (rate of change)
- `supply_velocity_pct` - Supply velocity (rate of change)
- `volume_velocity_pct` - Volume velocity (rate of change)

---

## Summary of Key Rules

1. **Data Sources**:
   - Floor Price: TCGPlayer ONLY
   - Listings: eBay AND TCGPlayer (combined)
   - Sales: eBay AND TCGPlayer (combined, treated equally)

2. **Filtering**:
   - Exclude anything with "JP" in title/description
   - Exclude listings/sales 25% or more below floor price
   - Very important: Do NOT input duplicate data

3. **Duplicate Detection**:
   - Listings: Price change = UPDATE (not new listing)
   - Sales: Check for exact duplicates before adding

4. **Rankings**:
   - Calculate daily, weekly, and monthly rankings
   - Update automatically with new data
   - Primary metric: unified_volume_7d_ema

5. **Calculations**:
   - All use 30-day moving averages where specified
   - Keep running counts for rankings
   - Update rankings after each data entry

6. **Automation Requirements**:
   - All screenshot data must automatically populate fields in leaderboard table
   - All screenshot data must automatically populate fields in box detail pages
   - No manual data entry required for displayed metrics
   - All calculations must run automatically
   - Data must flow: Screenshot → Extraction → Calculation → Database → API → Frontend
   - Rankings must update automatically
   - See `AUTOMATION_REQUIREMENTS.md` for complete integration requirements

