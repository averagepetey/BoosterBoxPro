# Import Excel Data Guide

## Your Data Format

Your Excel file contains **supply-focused data** for booster boxes, specifically tracking supply relative to 20% price increase:
- **Market Price** = Current floor price
- **20% Leg Up** = Price 20% above current floor (target price)
- **BB Supply** = Supply available at current price level (boxes priced at or below Market Price, before hitting 20% increase threshold)
- **Average Daily Sold** = Average boxes sold per day (28-day average)
- **Days of Inventory Remaining** = Days until BB Supply runs out (when prices could increase 20%) = maps to `days_to_20pct_increase`

## Column Mapping

| Excel Column | Maps To | Description |
|-------------|---------|-------------|
| **Set** | Box Identifier | Extracts OP code (e.g., "OP-01" from "(OP-01) Romance Dawn") |
| **Market Price** | `floor_price_usd` | Current floor price |
| **20% Leg Up** | *(not imported)* | Calculated target price (20% above Market Price) |
| **BB Supply** | `active_listings_count` | Supply at current price level (boxes at/below floor price, before 20% threshold) |
| **Average Daily Sold (28-day average)** | `boxes_sold_per_day` & `boxes_sold_30d_avg` | Average boxes sold per day |
| **Days of Inventory Remaining** | `days_to_20pct_increase` | Days until BB Supply runs out = when price could increase 20% |

## Automatic Calculations

The import script automatically calculates:
- **Market Cap** = Market Price × BB Supply (visible market cap at current price level)
- **Expected Days to Sell** = BB Supply / Average Daily Sold (days to sell supply at current price)
- **Days to 20% Increase** = Already in file as "Days of Inventory Remaining" (or calculated as BB Supply / Average Daily Sold)

## Important Notes

- **BB Supply** represents supply at the current price level (not total active listings)
  - These are boxes priced at or below the Market Price
  - Once these sell out, prices could increase toward the "20% Leg Up" price
- **Days to 20% Increase** indicates when supply at current price runs out, triggering potential price increase
- This is supply-focused data, tracking inventory pressure at current pricing levels

## Usage

1. **Install dependencies:**
   ```bash
   source venv/bin/activate
   pip install openpyxl
   ```

2. **Run import:**
   ```bash
   python scripts/import_metrics_from_excel.py path/to/your/file.xlsx
   ```

3. **Or specify date manually:**
   ```bash
   python scripts/import_metrics_from_excel.py path/to/your/file.xlsx --date "2025-12-25"
   ```

## What Happens

1. Script reads your Excel file
2. Extracts OP codes from Set column (e.g., "OP-01", "OP-06")
3. Matches boxes to database by OP code
4. Maps all columns to metrics format
5. Calculates derived metrics (market cap, expected days, etc.)
6. Imports via bulk API endpoint
7. Shows progress and any errors

## Notes

- The "20% Leg Up" column is not imported (it's a calculated target price)
- "Days of Inventory Remaining" represents when supply runs out, which is when price could increase by 20%
- If you have multiple dates in your file, each row will be imported for that date
- If all rows are for the same date, the script will detect it from the title or you can specify with `--date`

