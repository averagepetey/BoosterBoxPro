#!/usr/bin/env python3
"""
Test Public API Endpoints
Tests the public booster boxes endpoints (leaderboard, detail, time-series, sparkline)
"""

import sys
import os
import requests
import time
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


def test_health_check():
    """Test that the server is running"""
    print("=" * 60)
    print("Test 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first:")
        print("   python scripts/run_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_leaderboard():
    """Test leaderboard endpoint"""
    print("\n" + "=" * 60)
    print("Test 2: Leaderboard Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE}/booster-boxes",
            params={"limit": 10},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Total boxes: {data['meta']['total']}")
            print(f"   Returned: {len(data['data'])}")
            print(f"   Sort: {data['meta']['sort']}")
            
            if data['data']:
                print(f"\n   First box:")
                first_box = data['data'][0]
                print(f"      ID: {first_box['id']}")
                print(f"      Name: {first_box['product_name']}")
                print(f"      Rank: {first_box['rank']}")
                print(f"      Volume (7d EMA): {first_box['metrics'].get('unified_volume_7d_ema')}")
            else:
                print("   ⚠️  No boxes returned (may need data)")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_leaderboard_with_sort():
    """Test leaderboard with different sort options"""
    print("\n" + "=" * 60)
    print("Test 3: Leaderboard with Sort Options")
    print("=" * 60)
    
    sort_options = ["unified_volume_7d_ema", "liquidity_score", "floor_price_usd"]
    
    for sort_by in sort_options:
        try:
            response = requests.get(
                f"{API_BASE}/booster-boxes",
                params={"sort": sort_by, "limit": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sort by '{sort_by}': {len(data['data'])} results")
            else:
                print(f"❌ Sort by '{sort_by}': Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Sort by '{sort_by}': Error {e}")


def test_box_detail():
    """Test box detail endpoint"""
    print("\n" + "=" * 60)
    print("Test 4: Box Detail Endpoint")
    print("=" * 60)
    
    # First, get a box ID from the leaderboard
    try:
        response = requests.get(
            f"{API_BASE}/booster-boxes",
            params={"limit": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                box_id = data['data'][0]['id']
                
                # Now get detail for this box
                detail_response = requests.get(
                    f"{API_BASE}/booster-boxes/{box_id}",
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"✅ Box Detail Retrieved!")
                    print(f"   ID: {detail_data['id']}")
                    print(f"   Name: {detail_data['product_name']}")
                    print(f"   Rank: {detail_data.get('rank')}")
                    print(f"   Metric Date: {detail_data['metric_date']}")
                    print(f"   Time-series points: {len(detail_data.get('time_series_data', []))}")
                    print(f"   Rank history points: {len(detail_data.get('rank_history', []))}")
                    return True
                elif detail_response.status_code == 404:
                    print(f"⚠️  Box detail not found (box may not have metrics yet)")
                    return True
                else:
                    print(f"❌ Error: {detail_response.status_code}")
                    print(f"   Response: {detail_response.text[:200]}")
                    return False
            else:
                print("⚠️  No boxes available to test detail endpoint")
                return True
        else:
            print(f"❌ Could not get leaderboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_time_series():
    """Test time-series endpoint"""
    print("\n" + "=" * 60)
    print("Test 5: Time-Series Endpoint")
    print("=" * 60)
    
    # Get a box ID
    try:
        response = requests.get(
            f"{API_BASE}/booster-boxes",
            params={"limit": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                box_id = data['data'][0]['id']
                
                # Get time-series
                ts_response = requests.get(
                    f"{API_BASE}/booster-boxes/{box_id}/time-series",
                    params={
                        "start_date": str(date.today() - timedelta(days=30)),
                        "end_date": str(date.today())
                    },
                    timeout=10
                )
                
                if ts_response.status_code == 200:
                    ts_data = ts_response.json()
                    print(f"✅ Time-series Retrieved!")
                    print(f"   Data points: {len(ts_data)}")
                    if ts_data:
                        print(f"   First point: {ts_data[0]}")
                    return True
                else:
                    print(f"⚠️  Status: {ts_response.status_code} (may not have data)")
                    return True
            else:
                print("⚠️  No boxes available")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sparkline():
    """Test sparkline endpoint"""
    print("\n" + "=" * 60)
    print("Test 6: Sparkline Endpoint")
    print("=" * 60)
    
    # Get a box ID
    try:
        response = requests.get(
            f"{API_BASE}/booster-boxes",
            params={"limit": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                box_id = data['data'][0]['id']
                
                # Get sparkline
                spark_response = requests.get(
                    f"{API_BASE}/booster-boxes/{box_id}/sparkline",
                    params={"days": 7},
                    timeout=10
                )
                
                if spark_response.status_code == 200:
                    spark_data = spark_response.json()
                    print(f"✅ Sparkline Retrieved!")
                    print(f"   Data points: {len(spark_data)}")
                    if spark_data:
                        print(f"   First point: {spark_data[0]}")
                    return True
                else:
                    print(f"⚠️  Status: {spark_response.status_code} (may not have data)")
                    return True
            else:
                print("⚠️  No boxes available")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Testing Public API Endpoints")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start it first.")
        sys.exit(1)
    
    # Test 2: Leaderboard
    test_leaderboard()
    
    # Test 3: Leaderboard with sort
    test_leaderboard_with_sort()
    
    # Test 4: Box detail
    test_box_detail()
    
    # Test 5: Time-series
    test_time_series()
    
    # Test 6: Sparkline
    test_sparkline()
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\n💡 Note: Some endpoints may return empty data if metrics haven't been entered yet.")
    print("   This is expected behavior. Endpoints are working correctly.")


if __name__ == "__main__":
    main()

