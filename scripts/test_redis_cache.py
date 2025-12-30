#!/usr/bin/env python3
"""
Test Redis Cache and Ranking System
Verifies Redis connection, caching, and ranking calculations work correctly
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.cache_service import get_cache_service, CacheService
from app.services.ranking_calculator import RankingCalculator
from app.database import get_db, create_async_engine, async_sessionmaker
from app.config import settings


async def test_redis_connection():
    """Test basic Redis connection"""
    print("🔍 Testing Redis Connection...")
    # Create a fresh cache service instance for testing
    from app.services.cache_service import CacheService
    cache = CacheService()
    
    if not cache._connected:
        print("  ❌ Redis not connected")
        print("  💡 Make sure Redis is running: brew services start redis")
        return False
    
    print("  ✅ Redis connected successfully")
    
    # Test basic operations
    print("\n🔍 Testing Cache Operations...")
    
    # Test set/get
    test_key = "test:connection"
    test_value = {"test": "data", "timestamp": "2024-01-01"}
    
    result = await cache.set(test_key, test_value, ttl=60)
    if result:
        print("  ✅ Cache SET operation works")
    else:
        print("  ❌ Cache SET operation failed")
        return False
    
    cached = await cache.get(test_key)
    if cached and cached.get("test") == "data":
        print("  ✅ Cache GET operation works")
    else:
        print("  ❌ Cache GET operation failed")
        return False
    
    # Test exists
    exists = await cache.exists(test_key)
    if exists:
        print("  ✅ Cache EXISTS operation works")
    else:
        print("  ❌ Cache EXISTS operation failed")
        return False
    
    # Test delete
    deleted = await cache.delete(test_key)
    if deleted:
        print("  ✅ Cache DELETE operation works")
    else:
        print("  ❌ Cache DELETE operation failed")
        return False
    
    # Verify deletion
    exists_after = await cache.exists(test_key)
    if not exists_after:
        print("  ✅ Cache DELETE verified (key removed)")
    else:
        print("  ❌ Cache DELETE failed (key still exists)")
        return False
    
    await cache.close()
    return True


async def test_leaderboard_cache():
    """Test leaderboard-specific caching"""
    print("\n🔍 Testing Leaderboard Cache...")
    
    # Create a fresh cache service instance for testing
    from app.services.cache_service import CacheService
    cache = CacheService()
    
    # Force connection test by trying a ping
    try:
        if cache.redis_client:
            await cache.redis_client.ping()
            cache._connected = True
    except:
        cache._connected = False
    
    if not cache._connected:
        print("  ⚠️  Redis not connected, skipping cache test")
        await cache.close()
        return False
    
    test_date = date.today()
    test_data = [
        {"box_id": "test-1", "rank": 1, "volume": 1000},
        {"box_id": "test-2", "rank": 2, "volume": 900},
    ]
    
    # Test cache leaderboard
    result = await cache.cache_leaderboard(test_date, 10, test_data)
    if result:
        print("  ✅ Leaderboard cache SET works")
    else:
        print("  ❌ Leaderboard cache SET failed")
        return False
    
    # Test get cached leaderboard
    cached = await cache.get_cached_leaderboard(test_date, 10)
    if cached:
        print("  ✅ Leaderboard cache GET works")
        print(f"  ✅ Retrieved {len(cached)} items from cache")
    else:
        print("  ❌ Leaderboard cache GET failed")
        return False
    
    # Cleanup
    key = f"leaderboard:top10:{test_date.isoformat()}"
    await cache.delete(key)
    await cache.close()
    
    return True


async def test_ranking_calculator():
    """Test ranking calculator"""
    print("\n🔍 Testing Ranking Calculator...")
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as db:
        calculator = RankingCalculator(db)
        
        # Get all dates with metrics
        from sqlalchemy import select, distinct
        from app.models.unified_box_metrics import UnifiedBoxMetrics
        
        result = await db.execute(
            select(distinct(UnifiedBoxMetrics.metric_date))
            .order_by(UnifiedBoxMetrics.metric_date.desc())
            .limit(1)
        )
        
        test_date = result.scalar_one_or_none()
        
        if not test_date:
            print("  ⚠️  No metrics found in database. Create some metrics first.")
            print("  💡 Use the admin panel to add metrics, then test again.")
            await engine.dispose()
            return False
        
        print(f"  📅 Testing with date: {test_date}")
        
        # Test rank calculation
        try:
            ranks = await calculator.calculate_ranks_for_date(test_date)
            
            if ranks:
                print(f"  ✅ Rank calculation works - calculated ranks for {len(ranks)} boxes")
                
                # Show top 3
                sorted_ranks = sorted(ranks.items(), key=lambda x: x[1])[:3]
                print("  📊 Top 3 boxes:")
                for box_id, rank in sorted_ranks:
                    print(f"     Rank {rank}: {box_id}")
            else:
                print("  ⚠️  No ranks calculated (no metrics for this date)")
            
            # Test rank changes
            rank_changes = await calculator.calculate_rank_changes(test_date)
            if rank_changes:
                print(f"  ✅ Rank change calculation works - {len(rank_changes)} boxes")
            
            await engine.dispose()
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing ranking: {e}")
            import traceback
            traceback.print_exc()
            await engine.dispose()
            return False


async def test_cache_performance():
    """Test cache performance (speed comparison)"""
    print("\n🔍 Testing Cache Performance...")
    
    # Create a fresh cache service instance for testing
    from app.services.cache_service import CacheService
    cache = CacheService()
    
    # Force connection test by trying a ping
    try:
        if cache.redis_client:
            await cache.redis_client.ping()
            cache._connected = True
    except:
        cache._connected = False
    
    if not cache._connected:
        print("  ⚠️  Redis not connected, skipping performance test")
        await cache.close()
        return False
    
    import time
    
    test_date = date.today()
    test_data = [{"rank": i, "box_id": f"box-{i}"} for i in range(1, 51)]
    
    # Time cache set
    start = time.time()
    await cache.cache_leaderboard(test_date, 50, test_data)
    set_time = (time.time() - start) * 1000
    
    # Time cache get
    start = time.time()
    cached = await cache.get_cached_leaderboard(test_date, 50)
    get_time = (time.time() - start) * 1000
    
    print(f"  ⚡ Cache SET: {set_time:.2f}ms")
    print(f"  ⚡ Cache GET: {get_time:.2f}ms")
    
    if get_time < 10:
        print("  ✅ Cache performance excellent (<10ms)")
    elif get_time < 50:
        print("  ✅ Cache performance good (<50ms)")
    else:
        print("  ⚠️  Cache performance slower than expected")
    
    # Cleanup
    key = f"leaderboard:top50:{test_date.isoformat()}"
    await cache.delete(key)
    await cache.close()
    
    return True


async def main():
    """Run all tests"""
    print("="*60)
    print("Redis Cache & Ranking System Test")
    print("="*60)
    print()
    
    results = {}
    
    # Test 1: Redis Connection
    results["redis_connection"] = await test_redis_connection()
    
    # Test 2: Leaderboard Cache (only if Redis connected)
    if results["redis_connection"]:
        results["leaderboard_cache"] = await test_leaderboard_cache()
        results["cache_performance"] = await test_cache_performance()
    
    # Test 3: Ranking Calculator
    results["ranking_calculator"] = await test_ranking_calculator()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

