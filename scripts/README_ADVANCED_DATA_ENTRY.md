# Advanced Screenshot Data Entry System

This system intelligently processes TCGPlayer screenshots, tracks historical data, identifies new vs existing entries, and calculates all metrics automatically.

## Key Features

### 1. **Historical Data Tracking**
- Tracks all data entries by date and type (sales, listings, combined)
- Stores raw data from each screenshot
- Maintains complete history for metric calculations

### 2. **Smart Duplicate Detection**
- Identifies which data is new vs already entered
- Compares by date, data type, and field values
- Prevents duplicate entries while allowing updates

### 3. **Automatic Metric Calculation**
- Calculates all derived metrics from raw data:
  - **Daily Volume** - From sales data
  - **7-Day EMA Volume** - Exponential moving average
  - **Boxes Sold Per Day** - Average from historical data
  - **30-Day Average** - Long-term trends
  - **Price Changes** - Day-over-day percentage
  - **Listed Percentage** - Listings / Total Supply
  - **Market Cap** - Floor Price × Total Supply
  - **Liquidity Score** - Based on listings and sales velocity
  - **Days to 20% Increase** - Projected price growth
  - **Expected Days to Sell** - Based on current velocity

### 4. **Data Type Recognition**
- **Sales Screenshots** - Extracts sales data, volume, units sold
- **Listing Screenshots** - Extracts floor price, active listings, supply
- **Combined Screenshots** - Both sales and listing data
- **Auto-Detection** - Automatically determines type from content

### 5. **Data Merging**
- Merges multiple screenshots for the same day
- Combines sales and listing data intelligently
- Preserves all raw data for calculations

## How It Works

### Step 1: Screenshot Processing
1. You send a TCGPlayer screenshot
2. AI extracts all visible data:
   - Product name / Set code
   - Floor price
   - Active listings
   - Sales data
   - Volume
   - Market cap
   - Supply information

### Step 2: Historical Tracking
1. System checks if data already exists for this date/type
2. Compares new data with existing entries
3. Identifies what's new vs what's duplicate

### Step 3: Data Storage
1. Stores raw data in historical entries
2. Merges with existing data if needed
3. Preserves all information for calculations

### Step 4: Metric Calculation
1. Retrieves all historical data for the box
2. Calculates derived metrics:
   - Averages over time periods
   - Trends and changes
   - Projections and estimates
3. Updates leaderboard with calculated values

### Step 5: Update
1. Updates the box's metrics in the database
2. Reflects changes in the app immediately
3. Reports what was updated

## Example Workflow

### Scenario: Daily Data Entry

**Day 1 - Sales Screenshot:**
- You send: Sales screenshot showing 10 boxes sold, $5,000 volume
- System: 
  - Extracts: Sales data
  - Stores: Historical entry (type: "sales")
  - Calculates: Daily volume, boxes sold per day
  - Updates: Metrics in app

**Day 1 - Listing Screenshot (later):**
- You send: Listing screenshot showing floor $100, 50 listings
- System:
  - Extracts: Listing data
  - Stores: Historical entry (type: "listings")
  - Merges: With sales data from earlier
  - Calculates: All metrics from combined data
  - Updates: Complete metrics in app

**Day 2 - Combined Screenshot:**
- You send: Screenshot with both sales and listings
- System:
  - Extracts: All data
  - Checks: Not duplicate (different date)
  - Stores: Historical entry (type: "combined")
  - Calculates: Updated metrics including trends
  - Updates: Metrics with day-over-day changes

## Metric Calculations

### Volume Metrics
- **Daily Volume**: Sum of all sales for the day
- **7-Day EMA**: Exponential moving average of last 7 days
- **30-Day Average**: Simple average of last 30 days

### Sales Metrics
- **Boxes Sold Per Day**: Average from historical data
- **30-Day Average**: Long-term sales trend

### Price Metrics
- **Floor Price**: Current lowest listing price
- **1-Day Change %**: ((Today - Yesterday) / Yesterday) × 100
- **Days to 20% Increase**: Projected based on current trend

### Supply Metrics
- **Listed Percentage**: (Active Listings / Total Supply) × 100
- **Boxes Added Today**: New listings added
- **Average Added Per Day**: 7-day average

### Market Metrics
- **Market Cap**: Floor Price × Total Supply
- **Liquidity Score**: Based on listings and sales velocity
- **Expected Days to Sell**: Active Listings / Daily Sales Rate

## Data Structure

### Historical Entry
```json
{
  "date": "2024-01-15",
  "source": "screenshot",
  "data_type": "sales",
  "floor_price_usd": 362.52,
  "active_listings_count": 22,
  "boxes_sold_today": 19,
  "daily_volume_usd": 7003.88,
  "boxes_added_today": 5,
  "visible_market_cap_usd": 79754.40,
  "estimated_total_supply": 220,
  "screenshot_metadata": {
    "confidence_scores": {...},
    "extraction_timestamp": "..."
  }
}
```

### Calculated Metrics
```json
{
  "floor_price_usd": 362.52,
  "floor_price_1d_change_pct": 2.1,
  "daily_volume_usd": 7003.88,
  "unified_volume_7d_ema": 49027.20,
  "units_sold_count": 19,
  "boxes_sold_per_day": 19.32,
  "boxes_sold_30d_avg": 18.5,
  "active_listings_count": 22,
  "listed_percentage": 10.0,
  "liquidity_score": 1.0,
  "days_to_20pct_increase": 1.14,
  "expected_days_to_sell": 1.14
}
```

## Benefits

1. **No Manual Calculations** - All metrics calculated automatically
2. **Historical Context** - Uses full history for accurate trends
3. **Duplicate Prevention** - Knows what's already been entered
4. **Data Merging** - Combines multiple screenshots intelligently
5. **Accurate Metrics** - Calculations based on real historical data
6. **Automatic Updates** - App reflects changes immediately

## Usage

Simply send screenshots of TCGPlayer data. The system will:
1. Extract all visible data
2. Check for duplicates
3. Store historical entries
4. Calculate all metrics
5. Update the app
6. Report what happened

No need to specify data types or dates - the system figures it out automatically!





