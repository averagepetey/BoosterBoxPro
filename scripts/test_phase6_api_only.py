"""
Phase 6 API Endpoint Test Script
Tests Phase 6 features via API endpoints (requires server running)
"""
import sys
from pathlib import Path

# Add parent directory to path for imports (if needed)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import httpx
import json
from datetime import date, timedelta

API_BASE_URL = "http://localhost:8000/api/v1"


async def test_leaderboard_endpoint():
    """Test leaderboard endpoint with caching"""
    print("\n" + "="*60)
    print("Testing Leaderboard Endpoint")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Get leaderboard (default sort)
        print("\n📊 Test 1: Get Leaderboard (Default)")
        try:
            response = await client.get(f"{API_BASE_URL}/booster-boxes", params={"limit": 10})
            if response.status_code == 200:
                data = response.json()
                boxes = data.get("data", [])
                print(f"  ✅ Success: {len(boxes)} boxes returned")
                
                if boxes:
                    print("\n  Top 5 Rankings:")
                    for i, box in enumerate(boxes[:5], 1):
                        rank = box.get("rank", "N/A")
                        name = box.get("product_name", "Unknown")
                        volume = box.get("metrics", {}).get("unified_volume_7d_ema", 0)
                        rank_change = box.get("rank_change_direction")
                        rank_amount = box.get("rank_change_amount")
                        
                        change_str = ""
                        if rank_change:
                            arrow = "↑" if rank_change == "up" else "↓" if rank_change == "down" else "→"
                            change_str = f" ({arrow}{rank_amount or 0})"
                        
                        print(f"    #{rank}{change_str}: {name} - ${volume}")
            else:
                print(f"  ❌ Failed: Status {response.status_code}")
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        
        # Test 2: Get leaderboard with specific date
        print("\n📅 Test 2: Get Leaderboard (Specific Date)")
        try:
            target_date = date.today() - timedelta(days=1)
            response = await client.get(
                f"{API_BASE_URL}/booster-boxes",
                params={"limit": 5, "date": target_date.isoformat()}
            )
            if response.status_code == 200:
                data = response.json()
                boxes = data.get("data", [])
                print(f"  ✅ Success: {len(boxes)} boxes for {target_date}")
            else:
                print(f"  ⚠️  Status {response.status_code} (may be no data for this date)")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
        
        # Test 3: Test cache by making multiple requests
        print("\n⚡ Test 3: Cache Performance Test")
        try:
            import time
            
            # First request (cache miss)
            start = time.perf_counter()
            response1 = await client.get(f"{API_BASE_URL}/booster-boxes", params={"limit": 10})
            duration1 = (time.perf_counter() - start) * 1000
            
            # Second request (should be cache hit)
            start = time.perf_counter()
            response2 = await client.get(f"{API_BASE_URL}/booster-boxes", params={"limit": 10})
            duration2 = (time.perf_counter() - start) * 1000
            
            if response1.status_code == 200 and response2.status_code == 200:
                print(f"  First request (cache miss):  {duration1:.2f}ms")
                print(f"  Second request (cache hit):  {duration2:.2f}ms")
                if duration2 < duration1:
                    improvement = ((duration1 - duration2) / duration1) * 100
                    print(f"  ✅ Cache improved speed by {improvement:.1f}%")
                else:
                    print(f"  ⚠️  Cache didn't improve speed (data may be too small)")
            else:
                print(f"  ⚠️  One or both requests failed")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    return True


async def test_box_detail_endpoint():
    """Test box detail endpoint"""
    print("\n" + "="*60)
    print("Testing Box Detail Endpoint")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # First, get a box ID from leaderboard
        try:
            response = await client.get(f"{API_BASE_URL}/booster-boxes", params={"limit": 1})
            if response.status_code != 200:
                print("  ⚠️  Could not fetch leaderboard to get box ID")
                return False
            
            data = response.json()
            boxes = data.get("data", [])
            if not boxes:
                print("  ⚠️  No boxes in leaderboard")
                return False
            
            box_id = boxes[0].get("id")
            box_name = boxes[0].get("product_name")
            
            print(f"\n📦 Testing with box: {box_name}")
            print(f"   Box ID: {box_id}")
            
            # Test 1: Get box detail
            print("\n📊 Test 1: Get Box Detail")
            try:
                response = await client.get(f"{API_BASE_URL}/booster-boxes/{box_id}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success")
                    print(f"  Rank: #{data.get('rank', 'N/A')}")
                    
                    rank_change = data.get("rank_change_direction")
                    rank_amount = data.get("rank_change_amount")
                    if rank_change:
                        arrow = "↑" if rank_change == "up" else "↓" if rank_change == "down" else "→"
                        print(f"  Rank Change: {arrow}{rank_amount or 0}")
                    
                    metrics = data.get("metrics", {})
                    print(f"  Floor Price: ${metrics.get('floor_price_usd', 0)}")
                    print(f"  Volume (7d EMA): ${metrics.get('unified_volume_7d_ema', 0)}")
                    print(f"  Liquidity Score: {metrics.get('liquidity_score', 'N/A')}")
                    
                    time_series = data.get("time_series_data", [])
                    rank_history = data.get("rank_history", [])
                    print(f"  Time Series Points: {len(time_series)}")
                    print(f"  Rank History Points: {len(rank_history)}")
                else:
                    print(f"  ❌ Failed: Status {response.status_code}")
                    print(f"  Response: {response.text}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return False
            
            # Test 2: Get time-series data
            print("\n📈 Test 2: Get Time-Series Data")
            try:
                response = await client.get(f"{API_BASE_URL}/booster-boxes/{box_id}/time-series")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success: {len(data)} data points")
                    if data:
                        print(f"  Date Range: {data[0].get('date')} to {data[-1].get('date')}")
                else:
                    print(f"  ⚠️  Status {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
            
            # Test 3: Get sparkline data
            print("\n📉 Test 3: Get Sparkline Data")
            try:
                response = await client.get(
                    f"{API_BASE_URL}/booster-boxes/{box_id}/sparkline",
                    params={"days": 7}
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success: {len(data)} price points")
                else:
                    print(f"  ⚠️  Status {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    return True


async def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Server is healthy")
                print(f"  Environment: {data.get('environment', 'N/A')}")
            else:
                print(f"  ⚠️  Status {response.status_code}")
        except httpx.ConnectError:
            print("  ❌ Cannot connect to server. Is it running?")
            print("  💡 Start server: uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    return True


async def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("Phase 6 API Endpoint Test Suite")
    print("="*60)
    print("\n⚠️  Note: Server must be running at http://localhost:8000")
    print("   Start with: uvicorn app.main:app --reload\n")
    
    # Test health first
    health_ok = await test_health_check()
    if not health_ok:
        print("\n❌ Server is not running. Please start the server and try again.")
        return
    
    # Test endpoints
    leaderboard_ok = await test_leaderboard_endpoint()
    detail_ok = await test_box_detail_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"  Health Check:     {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"  Leaderboard:      {'✅ PASS' if leaderboard_ok else '❌ FAIL'}")
    print(f"  Box Detail:       {'✅ PASS' if detail_ok else '❌ FAIL'}")


if __name__ == "__main__":
    asyncio.run(main())

