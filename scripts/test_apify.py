#!/usr/bin/env python3
"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)


"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)


"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)

"""
Quick test script for Apify TCGplayer integration
Run with: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apify_client import ApifyClient


def test_apify(api_token: str, tcgplayer_url: str):
    """Test the Apify TCGplayer actor"""
    print(f"🔄 Testing Apify with URL: {tcgplayer_url}")
    print("-" * 60)
    
    client = ApifyClient(api_token)
    
    print("📡 Calling Apify actor...")
    run = client.actor("scraped/tcgplayer-sales-history").call(
        run_input={"url": tcgplayer_url}
    )
    
    print(f"✅ Run completed! Dataset ID: {run['defaultDatasetId']}")
    
    # Get results
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    if not items:
        print("❌ No data returned!")
        return
    
    data = items[0]
    
    print("\n📊 RAW DATA:")
    print("-" * 60)
    print(json.dumps(data, indent=2, default=str))
    
    print("\n📈 KEY METRICS:")
    print("-" * 60)
    print(f"Average Daily Sold: {data.get('averageDailyQuantitySold')}")
    print(f"Total Quantity Sold: {data.get('totalQuantitySold')}")
    print(f"Total Transactions: {data.get('totalTransactionCount')}")
    
    buckets = data.get('buckets', [])
    print(f"\n📅 BUCKETS ({len(buckets)} found):")
    print("-" * 60)
    
    for i, bucket in enumerate(buckets[:5]):  # Show first 5
        print(f"\nBucket {i+1}:")
        print(f"  Date: {bucket.get('bucketStartDate')}")
        print(f"  Market Price: ${bucket.get('marketPrice')}")
        print(f"  Quantity Sold: {bucket.get('quantitySold')}")
        print(f"  Low Sale: ${bucket.get('lowSalePrice')}")
        print(f"  High Sale: ${bucket.get('highSalePrice')}")
        print(f"  Transactions: {bucket.get('transactionCount')}")
    
    if len(buckets) > 5:
        print(f"\n... and {len(buckets) - 5} more buckets")
    
    # Check bucket frequency
    if len(buckets) >= 2:
        dates = [b.get('bucketStartDate') for b in buckets[:2]]
        print(f"\n⏱️ BUCKET FREQUENCY CHECK:")
        print(f"  First bucket: {dates[0]}")
        print(f"  Second bucket: {dates[1]}")
        
        from datetime import datetime
        try:
            d1 = datetime.strptime(dates[0], '%Y-%m-%d')
            d2 = datetime.strptime(dates[1], '%Y-%m-%d')
            diff = abs((d1 - d2).days)
            print(f"  Days between: {diff}")
            if diff == 1:
                print("  ✅ DAILY buckets!")
            elif diff == 7:
                print("  ⚠️ WEEKLY buckets")
            else:
                print(f"  ℹ️ {diff}-day buckets")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_apify.py <APIFY_TOKEN> <TCGPLAYER_URL>")
        print("\nExample:")
        print('  python scripts/test_apify.py "apify_api_xxx" "https://www.tcgplayer.com/product/..."')
        sys.exit(1)
    
    api_token = sys.argv[1]
    tcgplayer_url = sys.argv[2]
    
    test_apify(api_token, tcgplayer_url)



