#!/usr/bin/env python3
"""
Import Metrics from Excel File
Reads an Excel file and imports metrics data via the bulk endpoint
"""

import sys
import os
import asyncio
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
except ImportError:
    print("Error: pandas library not found. Please install it:")
    print("  pip install pandas openpyxl")
    sys.exit(1)

import httpx
from app.config import settings


def parse_date(date_value) -> Optional[date]:
    """Parse date from various formats"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, date):
        return date_value
    elif isinstance(date_value, datetime):
        return date_value.date()
    elif isinstance(date_value, str):
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                continue
        # Try pandas to_datetime
        try:
            dt = pd.to_datetime(date_value)
            return dt.date()
        except:
            return None
    else:
        return None


def parse_decimal(value) -> Optional[Decimal]:
    """Parse decimal from various formats"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        elif isinstance(value, str):
            # Remove $, commas, etc.
            cleaned = value.replace('$', '').replace(',', '').strip()
            return Decimal(cleaned)
        else:
            return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def parse_int(value) -> Optional[int]:
    """Parse integer from various formats"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, float):
            return int(value)
        elif isinstance(value, str):
            # Remove commas
            cleaned = value.replace(',', '').strip()
            return int(float(cleaned))
        else:
            return int(value)
    except (ValueError, TypeError):
        return None


def read_excel_file(file_path: str, date_override: Optional[str] = None) -> tuple[pd.DataFrame, Optional[date]]:
    """
    Read Excel file and return DataFrame with parsed date
    
    Args:
        file_path: Path to Excel file
        date_override: Optional date string to use (if not found in file)
        
    Returns:
        Tuple of (DataFrame, date or None)
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Try to extract date from first few rows or filename
        parsed_date = None
        
        if date_override:
            parsed_date = parse_date(date_override)
        
        # Look for date in first few rows (common in formatted sheets)
        if not parsed_date:
            for idx in range(min(5, len(df))):
                for col in df.columns:
                    cell_value = str(df.iloc[idx][col])
                    # Look for date patterns like "December 25, 2025" or "Week 37 - December 25, 2025"
                    if "2025" in cell_value or "2024" in cell_value or "2023" in cell_value:
                        # Try to parse date from this cell
                        for fmt in ['%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
                            try:
                                # Extract date part
                                import re
                                date_match = re.search(r'(\w+ \d{1,2}, \d{4})', cell_value)
                                if date_match:
                                    parsed_date = datetime.strptime(date_match.group(1), '%B %d, %Y').date()
                                    break
                                # Try other formats
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', cell_value)
                                if date_match:
                                    parsed_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                                    break
                            except:
                                continue
                    if parsed_date:
                        break
                if parsed_date:
                    break
        
        return df, parsed_date
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)


def extract_op_code(set_name: str) -> Optional[str]:
    """Extract OP-XX code from set name like '(OP-01) Romance Dawn (Blue)'"""
    import re
    match = re.search(r'\(OP-(\d+)\)', set_name)
    if match:
        return f"OP-{match.group(1).zfill(2)}"  # Ensure 2-digit format (OP-01 not OP-1)
    return None


def map_excel_to_metrics(df: pd.DataFrame, box_mapping: dict, metric_date: Optional[date] = None) -> List[dict]:
    """
    Map Excel data to metrics format
    
    Expected columns (flexible mapping):
    - Date/date/metric_date
    - Box/box_id/product_name/set_name (to find box_id)
    - Floor Price/floor_price/price
    - Listings/active_listings/listings_count
    - Volume/daily_volume/volume_usd
    - Market Cap/market_cap/visible_market_cap (optional)
    - Boxes Sold/boxes_sold/units_sold (optional)
    
    Args:
        df: DataFrame from Excel
        box_mapping: Dictionary mapping box identifiers to box_ids
                    e.g., {"OP-01": "uuid-here", "Romance Dawn": "uuid-here"}
    
    Returns:
        List of metrics dictionaries ready for API
    """
    metrics = []
    
    # Normalize column names (case-insensitive, remove spaces)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    
    # Use provided date or try to find date column
    date_col = None
    if not metric_date:
        for col in df.columns:
            if 'date' in col or col == 'date':
                date_col = col
                break
    
    # If no date column and no provided date, use today
    if not date_col and not metric_date:
        metric_date = date.today()
        print(f"⚠️  No date found, using today: {metric_date}")
    
    # Try to find box identifier column (Set column)
    box_col = None
    for col in df.columns:
        if col == 'set' or 'set' in col:
            box_col = col
            break
    
    if not box_col:
        print("Error: Could not find 'Set' column in Excel file")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Find other columns based on your format
    floor_price_col = None
    for col in df.columns:
        if 'market_price' in col or col == 'price' or 'market' in col:
            floor_price_col = col
            break
    
    listings_col = None
    for col in df.columns:
        if 'bb_supply' in col or 'supply' in col or 'inventory' in col:
            listings_col = col
            break
    
    boxes_sold_col = None
    for col in df.columns:
        if 'average_daily_sold' in col or 'daily_sold' in col or 'avg_daily' in col:
            boxes_sold_col = col
            break
    
    expected_days_col = None
    for col in df.columns:
        if 'days' in col and 'inventory' in col:
            expected_days_col = col
            break
    
    days_to_20pct_col = None
    for col in df.columns:
        if 'days' in col and ('inventory' in col or 'remaining' in col):
            days_to_20pct_col = col  # Days of Inventory Remaining = days to 20% increase
            break
    
    volume_col = None  # Not in your format, but keep for flexibility
    for col in df.columns:
        if any(term in col for term in ['volume', 'daily_volume']):
            volume_col = col
            break
    
    market_cap_col = None  # Can calculate from price * supply
    for col in df.columns:
        if any(term in col for term in ['market_cap', 'cap']):
            market_cap_col = col
            break
    
    # Process each row
    for idx, row in df.iterrows():
        # Use provided date or parse from row
        row_date = metric_date
        if not row_date and date_col:
            row_date = parse_date(row[date_col])
            if not row_date:
                print(f"Warning: Row {idx+1} has invalid date, skipping")
                continue
        
        if not row_date:
            print(f"Warning: Row {idx+1} - No date available, skipping")
            continue
        
        # Get box identifier
        box_identifier = str(row[box_col]).strip()
        
        # Extract OP code first (e.g., "OP-01" from "(OP-01) Romance Dawn (Blue)")
        op_code = extract_op_code(box_identifier)
        
        # Find box_id from mapping
        box_id = None
        
        # Try OP code first
        if op_code:
            for key, value in box_mapping.items():
                if op_code.lower() in key.lower():
                    box_id = value
                    break
        
        # If not found, try full set name
        if not box_id:
            for key, value in box_mapping.items():
                if key.lower() in box_identifier.lower() or box_identifier.lower() in key.lower():
                    box_id = value
                    break
        
        if not box_id:
            print(f"Warning: Row {idx+1} - Could not find box_id for '{box_identifier}' (OP code: {op_code}), skipping")
            continue
        
        # Build metrics dict
        metric_data = {
            "booster_box_id": box_id,
            "metric_date": row_date.isoformat(),
        }
        
        # Add optional fields if columns exist and have values
        if floor_price_col and not pd.isna(row[floor_price_col]):
            metric_data["floor_price_usd"] = float(parse_decimal(row[floor_price_col]))
        
        if listings_col and not pd.isna(row[listings_col]):
            # BB Supply = supply at current price level (before 20% increase threshold)
            metric_data["active_listings_count"] = parse_int(row[listings_col])
            
            # Calculate market cap if we have price and listings
            # This represents visible market cap at current price level
            if floor_price_col and not pd.isna(row[floor_price_col]):
                price = parse_decimal(row[floor_price_col])
                listings = parse_int(row[listings_col])
                if price and listings:
                    metric_data["visible_market_cap_usd"] = float(price * Decimal(str(listings)))
        
        if boxes_sold_col and not pd.isna(row[boxes_sold_col]):
            # This is 28-day average, store as boxes_sold_30d_avg
            metric_data["boxes_sold_30d_avg"] = float(parse_decimal(row[boxes_sold_col]))
            # Also use as daily sold (assuming it represents per-day average)
            metric_data["boxes_sold_per_day"] = float(parse_decimal(row[boxes_sold_col]))
        
        # Calculate expected_days_to_sell if we have listings and daily sold
        if listings_col and boxes_sold_col:
            listings = parse_int(row[listings_col])
            daily_sold = parse_decimal(row[boxes_sold_col])
            if listings and daily_sold and daily_sold > 0:
                expected_days = Decimal(str(listings)) / daily_sold
                expected_days = max(Decimal('1'), min(expected_days, Decimal('365')))
                metric_data["expected_days_to_sell"] = float(expected_days)
        
        # Map "Days of Inventory Remaining" to days_to_20pct_increase
        # This represents when supply runs out and price could increase by 20%
        if days_to_20pct_col and not pd.isna(row[days_to_20pct_col]):
            days_to_20pct = parse_decimal(row[days_to_20pct_col])
            if days_to_20pct:
                # Bound to reasonable range
                days_to_20pct = max(Decimal('0'), min(days_to_20pct, Decimal('365')))
                metric_data["days_to_20pct_increase"] = float(days_to_20pct)
        elif listings_col and boxes_sold_col:
            # Calculate from supply and daily sold rate
            listings = parse_int(row[listings_col])
            daily_sold = parse_decimal(row[boxes_sold_col])
            if listings and daily_sold and daily_sold > 0:
                days_to_20pct = Decimal(str(listings)) / daily_sold
                days_to_20pct = max(Decimal('0'), min(days_to_20pct, Decimal('365')))
                metric_data["days_to_20pct_increase"] = float(days_to_20pct)
        
        if volume_col and not pd.isna(row[volume_col]):
            metric_data["daily_volume_usd"] = float(parse_decimal(row[volume_col]))
        elif floor_price_col and boxes_sold_col:
            # Estimate volume from price * daily sold
            price = parse_decimal(row[floor_price_col])
            daily_sold = parse_decimal(row[boxes_sold_col])
            if price and daily_sold:
                estimated_volume = price * daily_sold
                metric_data["daily_volume_usd"] = float(estimated_volume)
        
        if market_cap_col and not pd.isna(row[market_cap_col]):
            metric_data["visible_market_cap_usd"] = float(parse_decimal(row[market_cap_col]))
        
        metrics.append(metric_data)
    
    return metrics


async def import_metrics(
    excel_file: str,
    date_override: Optional[str] = None,
    api_url: str = "http://localhost:8000",
    api_key: Optional[str] = None
):
    """Import metrics from Excel file"""
    
    # Get API key
    if api_key is None:
        api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print("📊 Reading Excel file...")
    df, parsed_date = read_excel_file(excel_file, date_override=date_override)
    print(f"✅ Read {len(df)} rows from Excel file")
    print(f"Columns: {list(df.columns)}")
    if parsed_date:
        print(f"📅 Detected date: {parsed_date}")
    print()
    
    # Get box mapping
    print("🔍 Getting box IDs from API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        # Fetch all boxes
        response = await client.get(
            f"{api_url}/api/v1/admin/boxes",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Error fetching boxes: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        boxes_data = response.json()
        boxes = boxes_data.get("boxes", [])
        
        # Create box mapping from set names and product names
        box_mapping = {}
        for box in boxes:
            box_id = box["id"]
            # Map by set name
            if box.get("set_name"):
                box_mapping[box["set_name"]] = box_id
            # Map by product name
            if box.get("product_name"):
                box_mapping[box["product_name"]] = box_id
                # Extract OP-XX if in product name
                if "OP-" in box["product_name"]:
                    parts = box["product_name"].split("OP-")
                    if len(parts) > 1:
                        op_code = "OP-" + parts[1].split()[0]
                        box_mapping[op_code] = box_id
        
        print(f"✅ Found {len(boxes)} boxes\n")
        print("Box mappings:")
        for key, value in list(box_mapping.items())[:5]:
            print(f"  {key} -> {value[:8]}...")
        if len(box_mapping) > 5:
            print(f"  ... and {len(box_mapping) - 5} more\n")
    
    # Map Excel data to metrics
    print("🔄 Mapping Excel data to metrics format...")
    metrics = map_excel_to_metrics(df, box_mapping, metric_date=parsed_date)
    print(f"✅ Mapped {len(metrics)} metrics entries\n")
    
    if not metrics:
        print("❌ No metrics to import!")
        sys.exit(1)
    
    # Import via bulk endpoint
    print(f"📤 Importing {len(metrics)} metrics entries...")
    
    # Split into batches of 100 (if needed)
    batch_size = 100
    total_success = 0
    total_errors = 0
    
    for i in range(0, len(metrics), batch_size):
        batch = metrics[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(metrics) + batch_size - 1) // batch_size
        
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} entries)...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{api_url}/api/v1/admin/manual-metrics/bulk",
                json={"metrics": batch},
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                successful = result.get("successful", 0)
                failed = result.get("failed", 0)
                total_success += successful
                total_errors += failed
                
                print(f"  ✅ {successful} successful, ❌ {failed} failed")
                
                if failed > 0:
                    errors = result.get("errors", [])
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"    Error: {error.get('error', 'Unknown')}")
            else:
                print(f"  ❌ Batch failed: {response.status_code}")
                print(f"  {response.text[:200]}")
                total_errors += len(batch)
    
    print("\n" + "=" * 60)
    print(f"✅ Import complete!")
    print(f"   Successful: {total_success}")
    print(f"   Errors: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import metrics from Excel file")
    parser.add_argument("excel_file", help="Path to Excel file (.xlsx or .xls)")
    parser.add_argument("--date", default=None, help="Date to use for all rows (YYYY-MM-DD), if not found in file")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default=None, help="Admin API key (defaults to ADMIN_API_KEY from .env)")
    
    args = parser.parse_args()
    
    asyncio.run(import_metrics(
        excel_file=args.excel_file,
        date_override=args.date,
        api_url=args.url,
        api_key=args.api_key
    ))

