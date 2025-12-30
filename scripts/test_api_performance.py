"""
Performance validation tests for API endpoints
Validates that endpoints meet Phase 7 performance targets (<200ms, cached <10ms)
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import time
import httpx
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from app.database import get_db, init_db
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.metrics_calculator import MetricsCalculator
from app.services.ranking_calculator import RankingCalculator

API_BASE_URL = "http://localhost:8000/api/v1"

# Performance targets
TARGET_CACHED_MS = 10  # Cached responses should be <10ms
TARGET_UNCACHED_MS = 200  # Uncached responses should be <200ms
TARGET_TIMESERIES_MS = 100  # Time-series should be <100ms


async def setup_test_data():
    """Setup test data for performance testing"""
    print("Setting up test data for performance testing...")
    await init_db()
    
    async for db in get_db():
        # Create test box if it doesn't exist
        test_box_name = "Performance Test Box OP-01"
        from sqlalchemy import select
        from app.models.booster_box import BoosterBox
        result = await db.execute(select(BoosterBox).where(BoosterBox.product_name == test_box_name))
        test_box = result.scalar_one_or_none()
        
        if not test_box:
            box_data = {
                "product_name": test_box_name,
                "set_name": "Performance Test Set",
                "game_type": "One Piece",
                "release_date": date(2023, 1, 1),
                "reprint_risk": "LOW",
                "estimated_total_supply": 10000,
            }
            test_box = await BoosterBoxRepository.create(db, box_data)
            print(f"  ✓ Created test box: {test_box.product_name}")
        else:
            print(f"  ✓ Using existing test box: {test_box.product_name}")
        
        # Create 30 days of metrics
        today = date.today()
        metrics_calculator = MetricsCalculator(db)
        
        for i in range(30):
            metric_date = today - timedelta(days=29 - i)
            metrics_data = {
                "booster_box_id": test_box.id,
                "metric_date": metric_date,
                "floor_price_usd": Decimal("200.00") + Decimal(str(i * 2)),
                "active_listings_count": 1000 + (i * 5),
                "unified_volume_usd": Decimal("10000.00") + Decimal(str(i * 500)),
                "boxes_sold_per_day": Decimal(str(10 + i)),
                "boxes_sold_30d_avg": Decimal(str(10 + i)),
            }
            await UnifiedMetricsRepository.create_or_update(db, metrics_data)
            await metrics_calculator.update_metrics_with_calculations(test_box.id, metric_date)
        
        # Calculate ranks
        ranking_calculator = RankingCalculator(db)
        await ranking_calculator.update_ranks_for_date(today)
        
        print(f"  ✓ Created 30 days of metrics for {test_box.product_name}")
        return test_box.id


async def test_endpoint_performance(url: str, description: str, target_ms: int, warm_cache: bool = False):
    """Test a single endpoint's performance"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Warm cache if requested
        if warm_cache:
            await client.get(url)
            await asyncio.sleep(0.1)  # Small delay
        
        # Measure response time
        start_time = time.perf_counter()
        try:
            response = await client.get(url)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                passed = elapsed_ms <= target_ms
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status} {description}: {elapsed_ms:.2f}ms (target: <{target_ms}ms)")
                return passed, elapsed_ms
            else:
                print(f"  ⚠️  {description}: HTTP {response.status_code}")
                return False, elapsed_ms
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            print(f"  ❌ {description}: Error - {e}")
            return False, elapsed_ms


async def main():
    """Run performance validation tests"""
    print("\n" + "="*60)
    print("Phase 7 Performance Validation")
    print("="*60)
    print("\n⚠️  Note: Server must be running at http://localhost:8000")
    print("   Start with: uvicorn app.main:app --reload\n")
    
    # Setup test data
    try:
        test_box_id = await setup_test_data()
    except Exception as e:
        print(f"❌ Failed to setup test data: {e}")
        print("   Make sure database is accessible and server is running.")
        return
    
    print("\n" + "="*60)
    print("Performance Tests")
    print("="*60)
    
    results = []
    
    # Test 1: Leaderboard (uncached)
    print("\n📊 Test 1: Leaderboard Endpoint (Uncached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes?limit=10",
        "Leaderboard (uncached)",
        TARGET_UNCACHED_MS,
        warm_cache=False
    )
    results.append(("Leaderboard (uncached)", passed, elapsed, TARGET_UNCACHED_MS))
    
    # Test 2: Leaderboard (cached)
    print("\n📊 Test 2: Leaderboard Endpoint (Cached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes?limit=10",
        "Leaderboard (cached)",
        TARGET_CACHED_MS,
        warm_cache=True
    )
    results.append(("Leaderboard (cached)", passed, elapsed, TARGET_CACHED_MS))
    
    # Test 3: Box Detail (uncached)
    print("\n📦 Test 3: Box Detail Endpoint (Uncached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes/{test_box_id}",
        "Box Detail (uncached)",
        TARGET_UNCACHED_MS,
        warm_cache=False
    )
    results.append(("Box Detail (uncached)", passed, elapsed, TARGET_UNCACHED_MS))
    
    # Test 4: Box Detail (cached)
    print("\n📦 Test 4: Box Detail Endpoint (Cached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes/{test_box_id}",
        "Box Detail (cached)",
        TARGET_CACHED_MS,
        warm_cache=True
    )
    results.append(("Box Detail (cached)", passed, elapsed, TARGET_CACHED_MS))
    
    # Test 5: Time-Series (uncached)
    print("\n📈 Test 5: Time-Series Endpoint (Uncached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes/{test_box_id}/time-series",
        "Time-Series (uncached)",
        TARGET_TIMESERIES_MS,
        warm_cache=False
    )
    results.append(("Time-Series (uncached)", passed, elapsed, TARGET_TIMESERIES_MS))
    
    # Test 6: Time-Series (cached)
    print("\n📈 Test 6: Time-Series Endpoint (Cached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes/{test_box_id}/time-series",
        "Time-Series (cached)",
        TARGET_CACHED_MS,
        warm_cache=True
    )
    results.append(("Time-Series (cached)", passed, elapsed, TARGET_CACHED_MS))
    
    # Test 7: Sparkline (uncached)
    print("\n📉 Test 7: Sparkline Endpoint (Uncached)")
    passed, elapsed = await test_endpoint_performance(
        f"{API_BASE_URL}/booster-boxes/{test_box_id}/sparkline?days=7",
        "Sparkline (uncached)",
        TARGET_UNCACHED_MS,
        warm_cache=False
    )
    results.append(("Sparkline (uncached)", passed, elapsed, TARGET_UNCACHED_MS))
    
    # Summary
    print("\n" + "="*60)
    print("Performance Summary")
    print("="*60)
    
    all_passed = True
    for name, passed, elapsed, target in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        margin = elapsed - target
        print(f"  {status} {name}: {elapsed:.2f}ms (target: <{target}ms, margin: {margin:+.2f}ms)")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All performance targets met!")
    else:
        print("⚠️  Some performance targets not met. Consider optimization.")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

