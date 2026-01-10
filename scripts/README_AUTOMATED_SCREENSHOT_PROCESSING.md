# Automated Screenshot Processing System

## Overview

The automated screenshot processing system provides **complete end-to-end automation** for processing screenshot data. When you send a screenshot with extracted data, the system automatically:

1. Formats the data
2. Applies all filters (JP, 25% below floor, eBay title matching)
3. Detects and removes duplicates
4. Calculates all metrics
5. Saves to database
6. Updates all fields automatically

**Zero manual intervention required.**

---

## Quick Start

### For AI Assistant (Chat)

When you send a screenshot, extract the data and format it as follows:

```python
from scripts.automated_screenshot_processor import process_screenshot_data

# Extract data from screenshot and format as:
raw_data = {
    "floor_price": 100.0,  # TCGPlayer floor price
    "floor_price_shipping": 5.0,  # Shipping cost
    "listings": [
        {
            "price": 105.0,
            "shipping": 5.0,
            "quantity": 2,
            "seller": "seller1",
            "title": "OP-01 Booster Box",
            "platform": "ebay",  # or "tcgplayer"
            "listing_id": "12345"  # optional
        },
        # ... more listings
    ],
    "sales": [
        {
            "price": 110.0,
            "shipping": 5.0,
            "quantity": 1,
            "date": "2025-01-03",  # ISO date
            "seller": "seller2",
            "title": "OP-01 Booster Box",
            "platform": "tcgplayer",  # or "ebay"
            "sale_id": "67890"  # optional
        },
        # ... more sales
    ]
}

# Process the data
result = await process_screenshot_data(
    raw_data=raw_data,
    box_name="OP-01",  # Box name
    entry_date="2025-01-03"  # Optional, defaults to today
)

# Check result
if result["success"]:
    print(f"✅ {result['message']}")
    print(f"Metrics calculated: {result['metrics']}")
else:
    print(f"❌ Error: {result['errors']}")
```

---

## Data Extraction Format

### Required Structure

The `raw_data` dictionary must contain:

#### Floor Price (TCGPlayer Only)
```python
{
    "floor_price": 100.0,  # Price from TCGPlayer
    "floor_price_shipping": 5.0  # Shipping cost
}
```

#### Listings (eBay + TCGPlayer)
```python
"listings": [
    {
        "price": 105.0,  # Listing price
        "shipping": 5.0,  # Shipping cost
        "quantity": 2,  # Quantity available
        "seller": "seller_name",  # Seller identifier
        "title": "OP-01 Booster Box",  # Listing title
        "platform": "ebay",  # "ebay" or "tcgplayer"
        "listing_id": "12345",  # Optional: listing ID
        "description": "..."  # Optional: description
    }
]
```

#### Sales (eBay + TCGPlayer)
```python
"sales": [
    {
        "price": 110.0,  # Sale price
        "shipping": 5.0,  # Shipping cost
        "quantity": 1,  # Quantity sold
        "date": "2025-01-03",  # ISO date (YYYY-MM-DD)
        "seller": "seller_name",  # Seller identifier
        "title": "OP-01 Booster Box",  # Sale title
        "platform": "tcgplayer",  # "ebay" or "tcgplayer"
        "sale_id": "67890",  # Optional: sale ID
        "description": "..."  # Optional: description
    }
]
```

---

## Processing Pipeline

The system processes data through these steps automatically:

### 1. Data Formatting
- Converts AI-extracted data to structured format
- Calculates total prices (price + shipping)
- Validates required fields
- Builds price ladder for T₊ calculation

### 2. Filtering
- **JP Filter**: Excludes listings/sales with "JP" in title/description
- **25% Below Floor**: Excludes listings/sales 25%+ below floor price
- **eBay Title Matching**: Only counts eBay items where title matches box name

### 3. Duplicate Detection
- **Listings**: Checks seller + price + quantity + platform
- **Sales**: Checks seller + price + quantity + date + platform
- Skips exact duplicates
- Detects price changes (UPDATE vs NEW)

### 4. Aggregation
- Counts filtered listings → `active_listings_count`
- Aggregates sales by date → `daily_volume_usd`, `boxes_sold_today`
- Counts new listings → `boxes_added_today`

### 5. Metric Calculations
All metrics calculate automatically:
- Volume metrics (daily, 7d EMA, 30d SMA, MoM change)
- Price metrics (current, 1d change, 30d change)
- Supply metrics (listings, added, averages)
- Demand metrics (sold, averages)
- Derived metrics (liquidity, market cap, days to 20%, etc.)

### 6. Database Save
- Saves all calculated metrics to `box_metrics_unified` table
- Updates existing records or creates new ones
- All fields populate automatically

### 7. Historical Data Save
- Saves raw data to historical data manager
- Stores price ladder for future T₊ calculations
- Tracks listings and sales for duplicate detection

---

## Result Structure

The processing result contains:

```python
{
    "success": True/False,
    "box_name": "OP-01",
    "entry_date": "2025-01-03",
    "box_id": "uuid",
    "steps": {
        "formatting": "success",
        "box_lookup": "success",
        "filtering": {
            "listings_before": 10,
            "listings_after": 8,
            "sales_before": 5,
            "sales_after": 4
        },
        "duplicate_detection": {
            "new_listings": 6,
            "updated_listings": 2,
            "duplicate_listings": 0,
            "new_sales": 3,
            "duplicate_sales": 1
        },
        "aggregation": "success",
        "calculations": "success",
        "database_save": {"action": "created", "success": True},
        "historical_save": "success"
    },
    "metrics": {
        "floor_price_usd": 105.0,
        "unified_volume_usd": 500.0,
        "unified_volume_7d_ema": 450.0,
        "unified_volume_30d_sma": 400.0,
        "volume_mom_change_pct": 5.2,
        # ... all other metrics
    },
    "errors": [],
    "message": "Successfully processed screenshot data for OP-01"
}
```

---

## Error Handling

The system handles errors gracefully:

- **Missing Box**: Returns error if box not found in database
- **Invalid Data**: Skips invalid listings/sales (logs but continues)
- **Database Errors**: Rolls back transaction, returns error
- **Calculation Errors**: Returns None for metrics that can't be calculated

All errors are included in the `errors` array in the result.

---

## Examples

### Example 1: Basic Processing

```python
raw_data = {
    "floor_price": 100.0,
    "floor_price_shipping": 5.0,
    "listings": [
        {
            "price": 105.0,
            "shipping": 5.0,
            "quantity": 1,
            "seller": "seller1",
            "title": "OP-01 Booster Box",
            "platform": "tcgplayer"
        }
    ],
    "sales": []
}

result = await process_screenshot_data(
    raw_data=raw_data,
    box_name="OP-01"
)
```

### Example 2: With Sales Data

```python
raw_data = {
    "floor_price": 100.0,
    "floor_price_shipping": 5.0,
    "listings": [],
    "sales": [
        {
            "price": 110.0,
            "shipping": 5.0,
            "quantity": 2,
            "date": "2025-01-03",
            "seller": "seller1",
            "title": "OP-01 Booster Box",
            "platform": "tcgplayer"
        }
    ]
}

result = await process_screenshot_data(
    raw_data=raw_data,
    box_name="OP-01",
    entry_date="2025-01-03"
)
```

### Example 3: Complete Data

```python
raw_data = {
    "floor_price": 100.0,
    "floor_price_shipping": 5.0,
    "listings": [
        {
            "price": 105.0,
            "shipping": 5.0,
            "quantity": 2,
            "seller": "seller1",
            "title": "OP-01 Booster Box",
            "platform": "ebay",
            "listing_id": "12345"
        },
        {
            "price": 110.0,
            "shipping": 0.0,
            "quantity": 1,
            "seller": "seller2",
            "title": "OP-01 Booster Box",
            "platform": "tcgplayer"
        }
    ],
    "sales": [
        {
            "price": 115.0,
            "shipping": 5.0,
            "quantity": 1,
            "date": "2025-01-03",
            "seller": "seller3",
            "title": "OP-01 Booster Box",
            "platform": "tcgplayer",
            "sale_id": "67890"
        }
    ]
}

result = await process_screenshot_data(
    raw_data=raw_data,
    box_name="OP-01"
)
```

---

## Important Notes

### Filtering Rules
- **JP Filter**: Automatically excludes items with "JP" in title/description
- **25% Below Floor**: Automatically excludes listings/sales 25%+ below floor price
- **eBay Title Matching**: Only counts eBay items where title matches box name (uses best judgment)

### Duplicate Detection
- **Listings**: Exact duplicates (same seller + price + quantity + platform) are skipped
- **Sales**: Exact duplicates (same seller + price + quantity + date + platform) are skipped
- **Price Changes**: Listings with same seller+quantity+platform but different price are treated as UPDATES (not new)

### Calculations
- All metrics calculate automatically from historical data
- Volume metrics use aggregated sales data
- Days to 20% uses price ladder data (T₊ calculation)
- All calculations follow `CALCULATION_SPECIFICATION.md` exactly

### Database Updates
- All fields populate automatically
- Existing records are updated (not duplicated)
- New records are created when needed
- All timestamps are set automatically

---

## Troubleshooting

### Box Not Found
**Error**: `Box 'OP-01' not found in database`

**Solution**: Ensure the box exists in the database. Check box names in the database.

### No Metrics Calculated
**Issue**: Metrics dictionary is empty

**Solution**: Ensure historical data exists. First entry may have limited metrics. Metrics improve as more data is added.

### Duplicate Detection Too Strict
**Issue**: Valid listings/sales are being skipped

**Solution**: Check that seller, price, quantity, platform, and date are accurate. Duplicate detection is strict to prevent double-counting.

### Filtering Too Aggressive
**Issue**: Valid listings/sales are being filtered out

**Solution**: Check filtering rules:
- Ensure titles don't contain "JP"
- Ensure prices aren't 25%+ below floor
- For eBay, ensure titles match box name

---

## Integration

The system integrates with:

- **Database**: `box_metrics_unified` table
- **Historical Data**: `data/historical_entries.json`
- **Metrics Calculator**: All calculations
- **API**: Metrics automatically available via API endpoints
- **Frontend**: Metrics automatically display in leaderboard and box detail pages

---

## Support

For issues or questions:
1. Check `CALCULATION_SPECIFICATION.md` for calculation details
2. Check `DATA_EXTRACTION_REQUIREMENTS.md` for extraction requirements
3. Check `AUTOMATION_REQUIREMENTS.md` for automation requirements
4. Review error messages in processing result

---

## Summary

The automated screenshot processing system provides **complete automation** with **zero manual intervention**. Simply extract data from screenshots, format it correctly, and call `process_screenshot_data()`. The system handles everything else automatically.

**All fields populate automatically. All calculations run automatically. All data saves automatically.**



