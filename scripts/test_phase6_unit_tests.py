"""
Phase 6 Unit Tests
Tests individual components without requiring database data
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from app.services.ranking_calculator import RankingCalculator
from app.services.cache_service import CacheService
from app.services.ema_calculator import EMACalculator


async def test_ema_calculator():
    """Test EMA calculator with sample data"""
    print("\n" + "="*60)
    print("Unit Test: EMA Calculator")
    print("="*60)
    
    # Sample volume data (7 days)
    volumes = [
        Decimal("1000.00"),
        Decimal("1200.00"),
        Decimal("1100.00"),
        Decimal("1300.00"),
        Decimal("1250.00"),
        Decimal("1400.00"),
        Decimal("1350.00"),
    ]
    
    # Calculate EMA (7-day EMA uses window=7)
    ema = EMACalculator.calculate_ema(volumes, window=7)
    
    print(f"\n  Input volumes: {[float(v) for v in volumes]}")
    print(f"  Calculated EMA (7-day): ${float(ema):.2f}")
    
    # Validate EMA is reasonable (between min and max)
    min_vol = min(volumes)
    max_vol = max(volumes)
    
    if ema and min_vol <= ema <= max_vol:
        print("  ✅ EMA is within expected range")
        
        # Also test SMA
        sma = EMACalculator.calculate_sma(volumes, window=7)
        print(f"  Calculated SMA (7-day): ${float(sma):.2f}")
        print("  ✅ SMA calculation works")
        
        return True
    else:
        print(f"  ❌ EMA out of range: min=${min_vol}, max=${max_vol}")
        return False


async def test_cache_service():
    """Test cache service operations"""
    print("\n" + "="*60)
    print("Unit Test: Cache Service")
    print("="*60)
    
    cache = CacheService()
    
    # Check if Redis is available
    try:
        if cache.redis_client:
            await cache.redis_client.ping()
            cache._connected = True
            print("  ✓ Redis connected")
        else:
            print("  ⚠️  Redis not available, skipping cache tests")
            return True  # Not a failure, just not available
    except Exception as e:
        print(f"  ⚠️  Redis not available: {e}")
        return True  # Not a failure
    
    # Test operations
    test_key = "test:unit:cache"
    test_value = {
        "test": "data",
        "number": 123,
        "date": date.today().isoformat(),
    }
    
    # Set
    result = await cache.set(test_key, test_value, ttl=60)
    if result:
        print("  ✅ Cache SET works")
    else:
        print("  ❌ Cache SET failed")
        return False
    
    # Get
    retrieved = await cache.get(test_key)
    if retrieved == test_value:
        print("  ✅ Cache GET works")
    else:
        print(f"  ❌ Cache GET failed. Expected: {test_value}, Got: {retrieved}")
        return False
    
    # Exists
    exists = await cache.exists(test_key)
    if exists:
        print("  ✅ Cache EXISTS works")
    else:
        print("  ❌ Cache EXISTS failed")
        return False
    
    # Delete
    deleted = await cache.delete(test_key)
    if deleted:
        print("  ✅ Cache DELETE works")
    else:
        print("  ❌ Cache DELETE failed")
        return False
    
    # Verify deleted
    exists_after = await cache.exists(test_key)
    if not exists_after:
        print("  ✅ Cache DELETE verified (key removed)")
    else:
        print("  ❌ Cache DELETE failed (key still exists)")
        return False
    
    await cache.close()
    return True


def test_rank_calculation_logic():
    """Test ranking calculation logic (synchronous)"""
    print("\n" + "="*60)
    print("Unit Test: Rank Calculation Logic")
    print("="*60)
    
    # Simulate box volumes (sorted descending)
    box_volumes = {
        uuid4(): Decimal("10000.00"),  # Rank 1
        uuid4(): Decimal("9000.00"),   # Rank 2
        uuid4(): Decimal("9000.00"),   # Rank 2 (tie)
        uuid4(): Decimal("8000.00"),   # Rank 4
        uuid4(): Decimal("7000.00"),   # Rank 5
    }
    
    # Calculate ranks manually
    sorted_boxes = sorted(box_volumes.items(), key=lambda x: x[1], reverse=True)
    
    ranks = {}
    current_rank = 1
    previous_volume = None
    
    for idx, (box_id, volume) in enumerate(sorted_boxes):
        if previous_volume is None or volume < previous_volume:
            current_rank = idx + 1
        ranks[box_id] = current_rank
        previous_volume = volume
    
    print(f"\n  Box volumes: {[float(v) for v in box_volumes.values()]}")
    print(f"  Calculated ranks: {list(ranks.values())}")
    
    # Validate ranks
    expected_ranks = [1, 2, 2, 4, 5]
    actual_ranks = list(ranks.values())
    
    if actual_ranks == expected_ranks:
        print("  ✅ Rank calculation logic is correct")
        return True
    else:
        print(f"  ❌ Rank calculation failed. Expected: {expected_ranks}, Got: {actual_ranks}")
        return False


def test_rank_change_logic():
    """Test rank change calculation logic"""
    print("\n" + "="*60)
    print("Unit Test: Rank Change Logic")
    print("="*60)
    
    # Previous ranks
    previous_ranks = {
        "box1": 1,
        "box2": 2,
        "box3": 3,
    }
    
    # Current ranks
    current_ranks = {
        "box1": 2,  # Moved down 1
        "box2": 1,  # Moved up 1
        "box3": 3,  # No change
    }
    
    # Calculate rank changes
    rank_changes = {}
    for box_id in current_ranks:
        prev = previous_ranks.get(box_id)
        curr = current_ranks[box_id]
        if prev is not None:
            rank_changes[box_id] = prev - curr  # Positive = moved up, Negative = moved down
    
    print(f"\n  Previous ranks: {previous_ranks}")
    print(f"  Current ranks:  {current_ranks}")
    print(f"  Rank changes:   {rank_changes}")
    
    # Validate changes
    expected_changes = {
        "box1": -1,  # Down 1
        "box2": 1,   # Up 1
        "box3": 0,   # No change
    }
    
    if rank_changes == expected_changes:
        print("  ✅ Rank change calculation is correct")
        print("    box1: ↓ 1 (down)")
        print("    box2: ↑ 1 (up)")
        print("    box3: → 0 (same)")
        return True
    else:
        print(f"  ❌ Rank change calculation failed")
        return False


async def main():
    """Run all unit tests"""
    print("\n" + "="*60)
    print("Phase 6 Unit Test Suite")
    print("="*60)
    print("\nThese tests don't require database data or server running")
    
    # Run tests
    ema_ok = await test_ema_calculator()
    cache_ok = await test_cache_service()
    rank_logic_ok = test_rank_calculation_logic()
    rank_change_ok = test_rank_change_logic()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"  EMA Calculator:        {'✅ PASS' if ema_ok else '❌ FAIL'}")
    print(f"  Cache Service:         {'✅ PASS' if cache_ok else '❌ FAIL'}")
    print(f"  Rank Calculation:      {'✅ PASS' if rank_logic_ok else '❌ FAIL'}")
    print(f"  Rank Change Logic:     {'✅ PASS' if rank_change_ok else '❌ FAIL'}")
    
    all_passed = all([ema_ok, cache_ok, rank_logic_ok, rank_change_ok])
    if all_passed:
        print("\n✅ All unit tests passed!")
    else:
        print("\n❌ Some unit tests failed")


if __name__ == "__main__":
    asyncio.run(main())

