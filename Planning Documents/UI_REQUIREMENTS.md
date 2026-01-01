# UI Requirements Based on Mockup

## UI Structure (Leaderboard/Table View)

Based on the provided mockup, the UI is a dark-themed leaderboard table with the following columns:

### Columns (Left to Right)

1. **# (Rank)** - Rank number (1, 2, 3, etc.)
2. **Collection (Booster Box)** - Name + Avatar/Logo + Rank Change Indicator
3. **Floor** - Current floor price (USD)
4. **Top Offer** - NOT APPLICABLE (no order book in requirements)
5. **Floor 1d %** - 1-day floor price percentage change (with ▲/▼ indicators)
6. **Volume** - Daily volume USD (PRIMARY METRIC - most prominent)
7. **Sales** - Number of boxes sold (count)
8. **Listed** - Percentage + absolute numbers (e.g., "1,693 / 10K" = 16.9%)
9. **Last 1d** - Sparkline chart showing price trend over last 24 hours

### UI Features

- **Sortable Columns** - Up/down arrows on column headers
- **Color Coding:**
  - Red: Negative changes (▼), downward trends
  - Green: Positive changes (▲), upward trends
- **Rank Change Indicators** - Up/down arrows on collection avatars
- **Sparklines** - Mini price trend charts (24-hour view)
- **Dark Theme** - Dark background with white/light text

---

## Data Requirements for UI

### Additional Fields Needed

1. **Avatar/Image URL** - For booster box logo/image
2. **1-Day Floor Price Change %** - Calculate from today vs yesterday floor price
3. **Sparkline Data** - Array of price points for last 24 hours (or last day's data points)
4. **Rank Change Direction** - Visual indicator (up/down/neutral)
5. **Listed Percentage** - active_listings / estimated_total_supply (or just show active count if no supply estimate)
6. **Sales Count** - units_sold_count (already have this)

### Mappings from UI to Our Metrics

| UI Column | Our Metric | Notes |
|-----------|-----------|-------|
| Rank (#) | current_rank | Based on volume_7d_ema |
| Collection | product_name + image_url | Need to add image_url |
| Floor | floor_price_usd | Already have |
| Top Offer | N/A | Not tracking order book |
| Floor 1d % | floor_price_1d_change_pct | Need to calculate |
| Volume | daily_volume_usd | PRIMARY - already have |
| Sales | units_sold_count | Already have |
| Listed | active_listings_count / (total_supply or just count) | Need percentage |
| Last 1d (Sparkline) | price_sparkline_1d | Array of price points |

---

## Database Schema Updates Needed

### Add to `booster_boxes` table:
```sql
ALTER TABLE booster_boxes ADD COLUMN image_url VARCHAR(500);
ALTER TABLE booster_boxes ADD COLUMN estimated_total_supply INT; -- Optional, for listed %
```

### Add to `daily_derived_metrics` table:
```sql
ALTER TABLE daily_derived_metrics ADD COLUMN floor_price_1d_change_pct DECIMAL(6, 2);
-- Percentage change from yesterday's floor price
-- NULL if no previous day data
```

---

## Calculation Updates Needed

### 1. Floor Price 1-Day Change %
```python
yesterday_floor = get_floor_price(booster_box_id, date=yesterday)
today_floor = get_floor_price(booster_box_id, date=today)

if yesterday_floor and today_floor:
    floor_price_1d_change_pct = ((today_floor - yesterday_floor) / yesterday_floor) * 100
else:
    floor_price_1d_change_pct = None
```

### 2. Listed Percentage
```python
active_listings_count = count_active_listings(booster_box_id)
estimated_total_supply = booster_box.estimated_total_supply

if estimated_total_supply and estimated_total_supply > 0:
    listed_percentage = (active_listings_count / estimated_total_supply) * 100
else:
    listed_percentage = None  # Just show absolute count
```

### 3. Sparkline Data (1-Day Price Trend)
```python
# Get hourly or 4-hour price snapshots from last 24 hours
sparkline_data = get_price_snapshots(
    booster_box_id, 
    start_time=now - 24_hours,
    interval='4h'  # 6 data points for 24h
)
# Returns: [{timestamp, floor_price}, ...]
```

**Note:** For sparklines, we might need to:
- Store hourly snapshots of floor_price (separate table or embedded in existing structure)
- Or use daily snapshots and interpolate for smoother charts
- Start simple: use daily data for first 7 days (weekly sparkline)

---

## Updated API Response Shape

### Home Screen (Leaderboard) - Updated for UI

**Endpoint:** `GET /api/v1/booster-boxes?sort=volume&limit=10`

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "rank_change_direction": "up",  // "up", "down", "same"
      "rank_change_amount": 2,  // moved up 2 positions (optional)
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      "set_name": "Modern Horizons 3",
      "game_type": "MTG",
      "image_url": "https://cdn.example.com/mh3-box.jpg",
      
      "metrics": {
        "floor_price_usd": 245.99,
        "floor_price_1d_change_pct": -1.3,  // -1.3% change
        "daily_volume_usd": 45230.50,  // PRIMARY - most prominent
        "volume_7d_ema": 43890.25,
        "units_sold_count": 18,  // Sales count
        "active_listings_count": 3044,
        "listed_percentage": 8.3,  // 8.3% if we have total_supply
        "estimated_total_supply": 36600,  // For "3,044 / 36.6K" display
        "days_to_20pct_increase": 12.5,
        "price_sparkline_1d": [  // For sparkline chart
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

### Detail View (Advanced Analytics Page)

**Navigation:** Clicking/tapping on any booster box row in the leaderboard navigates to the detail page.

**Endpoint:** `GET /api/v1/booster-boxes/{id}`

**Purpose:** Provide advanced analytics and detailed insights beyond the summary shown in the leaderboard.

**Key Features:**
1. **Header Section:**
   - Box image/avatar (large)
   - Product name and set name
   - Current rank with rank change indicator
   - Favorite/Unfavorite button (if authenticated)

2. **Key Metrics Card:**
   - Current floor price (large, prominent)
   - Floor price 24h change %
   - Volume (7-day EMA and daily)
   - Active listings count
   - Liquidity score
   - Expected days to sell
   - Days to +20% projection

3. **Price Chart (Sparkline/Line Chart):**
   - Historical price trend (last 30 days default, with time range selector)
   - Interactive chart showing floor price over time
   - Hover tooltips showing exact price and date

4. **Advanced Metrics Table:**
   - Time-series data (last 30 days)
   - Columns: Date, Floor Price, Volume, Listings Count, Sales Count, Market Cap
   - Sortable by any column
   - Export to CSV option (future enhancement)

5. **Historical Rankings:**
   - Rank history chart/graph
   - Shows rank position over time
   - Highlights rank changes

6. **Additional Context:**
   - Set release date
   - Game type
   - Reprint risk level
   - Visible market cap
   - Absorption rate

**Response Structure:** (Extended version with all details - see ARCHITECTURE_PLAN.md)
- All metrics from leaderboard (included for consistency)
- Extended time-series data (30+ days)
- Historical rank movements
- Price history data
- Additional advanced metrics

**Navigation Flow:**
```
Leaderboard List
  ↓ (click/tap on row)
Box Detail Page (Advanced Analytics)
  ↓ (back button/tap)
Leaderboard List
```

---

## Sorting Options (Based on Sortable Columns)

Supported sort parameters:
- `sort=volume` (default) - Sort by daily_volume_usd DESC
- `sort=market_cap` - Sort by visible_market_cap_usd DESC
- `sort=floor_price` - Sort by floor_price_usd DESC
- `sort=floor_change_1d` - Sort by floor_price_1d_change_pct DESC
- `sort=sales` - Sort by units_sold_count DESC
- `sort=listed` - Sort by active_listings_count DESC

All support `order=asc` or `order=desc` (default: desc)

Example:
```
GET /api/v1/booster-boxes?sort=floor_price&order=asc&limit=10
```

---

## Implementation Priority

### Phase 1 (MVP - Essential for UI)
1. ✅ Add `image_url` to booster_boxes
2. ✅ Calculate `floor_price_1d_change_pct` in metrics
3. ✅ Add `rank_change_direction` to API response
4. ✅ Include `units_sold_count` in API (already have)
5. ✅ Update API response shape to match UI structure

### Phase 2 (Enhanced Features)
1. Add sparkline data (start with daily snapshots, upgrade to hourly later)
2. Add listed percentage calculation (if we have total_supply estimates)
3. Support all sortable columns

### Phase 3 (Future)
1. Hourly price snapshots for smoother sparklines
2. Total supply estimates (if available from marketplace APIs)
3. More granular sparkline intervals

---

## UI Display Examples

### Floor 1d % Display
```
floor_price_1d_change_pct: -1.3
→ Display: "▼1.3%" (red)

floor_price_1d_change_pct: 4.7
→ Display: "▲4.7%" (green)

floor_price_1d_change_pct: null or 0
→ Display: "--" or "0.0%"
```

### Listed Display
```
If estimated_total_supply exists:
  active_listings_count: 3044
  estimated_total_supply: 36600
  listed_percentage: 8.3
→ Display: "3,044 / 36.6K (8.3%)"

If no estimated_total_supply:
  active_listings_count: 125
→ Display: "125 listed"
```

### Rank Change Display
```
rank_change_direction: "up"
→ Show ↑ arrow on avatar

rank_change_direction: "down"
→ Show ↓ arrow on avatar

rank_change_direction: "same"
→ No indicator
```



