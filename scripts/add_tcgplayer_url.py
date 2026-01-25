#!/usr/bin/env python3
"""
Quick script to test and add TCGplayer URLs
Usage: python scripts/add_tcgplayer_url.py "URL"
Example: python scripts/add_tcgplayer_url.py "https://www.tcgplayer.com/product/..."
"""

import sys
import os
from apify_client import ApifyClient

# Get API token from environment variable (never hardcode secrets!)
API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not API_TOKEN:
    print("❌ Error: APIFY_API_TOKEN environment variable not set")
    print("   Set it with: export APIFY_API_TOKEN=your_token_here")
    sys.exit(1)

def test_url(url: str):
    """Test a TCGplayer URL and return key metrics"""
    client = ApifyClient(API_TOKEN)
    
    print(f"🔄 Testing URL...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": url},
        timeout_secs=60
    )
    
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        return None
    
    data = items[0]
    buckets = data.get('buckets', [])
    latest_bucket = buckets[0] if buckets else {}
    
    return {
        'avg_daily_sold': data.get('averageDailyQuantitySold'),
        'total_sold': data.get('totalQuantitySold'),
        'market_price': latest_bucket.get('marketPrice'),
        'low_sale': latest_bucket.get('lowSalePrice'),
        'high_sale': latest_bucket.get('highSalePrice'),
        'bucket_date': latest_bucket.get('bucketStartDate'),
        'sku_id': data.get('skuId'),
        'variant': data.get('variant'),
        'condition': data.get('condition'),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_tcgplayer_url.py 'URL'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    result = test_url(url)
    
    if result:
        print("\n✅ SUCCESS! Data found:")
        print(f"   Avg Daily Sold: {result['avg_daily_sold']}")
        print(f"   Total Sold: {result['total_sold']}")
        print(f"   Market Price: ${result['market_price']}")
        print(f"   Low Sale: ${result['low_sale']}")
        print(f"   High Sale: ${result['high_sale']}")
        print(f"   Latest Bucket: {result['bucket_date']}")
        print(f"   SKU ID: {result['sku_id']}")
        print(f"   Variant: {result['variant']}")
        print(f"   Condition: {result['condition']}")
    else:
        print("\n❌ No data found for this URL")
