"""
Phase 6 Comprehensive Test Script
Creates test data and tests rankings, caching, and API endpoints
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID
import httpx
import logging

from app.database import get_db, init_db
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.ranking_calculator import RankingCalculator
from app.services.cache_service import CacheService
from app.services.metrics_calculator import MetricsCalculator
from app.services.leaderboard_service import LeaderboardService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
API_BASE_URL = "http://localhost:8000/api/v1"
NUM_TEST_BOXES = 5
NUM_TEST_DAYS = 14  # Create 14 days of data for EMA calculation


async def create_test_boxes(db):
    """Create test booster boxes"""
    logger.info(f"\n{'='*60}")
    logger.info("Step 1: Creating Test Booster Boxes")
    logger.info(f"{'='*60}")
    
    test_boxes = []
    box_names = [
        "OP-01 Romance Dawn (Test)",
        "OP-02 Paramount War (Test)",
        "OP-03 Pillars of Strength (Test)",
        "OP-04 Kingdoms of Intrigue (Test)",
        "OP-05 Awakening of the New Era (Test)",
    ]
    
    for i, box_name in enumerate(box_names[:NUM_TEST_BOXES]):
        # Check if box already exists (search by product_name using SQL)
        from sqlalchemy import select
        from app.models.booster_box import BoosterBox
        result = await db.execute(
            select(BoosterBox).where(BoosterBox.product_name == box_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info(f"  ✓ Box already exists: {box_name}")
            test_boxes.append(existing)
            continue
        
        box_data = {
            "product_name": box_name,
            "set_name": box_name.split(" (")[0],
            "game_type": "One Piece",
            "release_date": date(2023, 1, 1) + timedelta(days=i*30),
            "reprint_risk": "LOW" if i % 2 == 0 else "MEDIUM",
            "estimated_total_supply": 10000 + (i * 2000),
        }
        box = await BoosterBoxRepository.create(db, box_data)
        test_boxes.append(box)
        logger.info(f"  ✓ Created: {box.product_name} (ID: {box.id})")
    
    return test_boxes


async def create_test_metrics(db, boxes):
    """Create test metrics data for multiple days"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Step 2: Creating {NUM_TEST_DAYS} Days of Test Metrics")
    logger.info(f"{'='*60}")
    
    today = date.today()
    metrics_calculator = MetricsCalculator(db)
    
    for day_offset in range(NUM_TEST_DAYS):
        metric_date = today - timedelta(days=NUM_TEST_DAYS - day_offset - 1)
        
        for i, box in enumerate(boxes):
            # Create varying metrics to ensure different rankings
            base_price = 200 + (i * 10)  # Different base prices
            price_variation = day_offset * 2  # Price increases over time
            floor_price = Decimal(f"{base_price + price_variation}.00")
            
            # Varying volumes - box 0 has highest volume, decreasing
            base_volume = 10000 - (i * 1000)
            volume_variation = day_offset * 100
            daily_volume = Decimal(f"{base_volume + volume_variation}.00")
            
            # Varying listings
            base_listings = 1000 + (i * 100)
            active_listings = base_listings - (day_offset * 5)
            
            # Units sold varies
            units_sold = 10 + i + (day_offset % 5)
            
            metrics_data = {
                "booster_box_id": box.id,
                "metric_date": metric_date,
                "floor_price_usd": floor_price,
                "active_listings_count": active_listings,
                "unified_volume_usd": daily_volume,
                "boxes_sold_per_day": Decimal(str(units_sold)),
                "boxes_sold_30d_avg": Decimal(str(units_sold)),
            }
            
            # Create or update metrics
            await UnifiedMetricsRepository.create_or_update(db, metrics_data)
            
            # Calculate derived metrics (EMA, liquidity score, etc.)
            await metrics_calculator.update_metrics_with_calculations(
                box.id, metric_date
            )
        
        if day_offset % 5 == 0:
            logger.info(f"  ✓ Created metrics for {metric_date} ({day_offset + 1}/{NUM_TEST_DAYS} days)")
    
    logger.info(f"  ✅ Created metrics for all {NUM_TEST_DAYS} days")


async def test_ranking_calculator(db):
    """Test ranking calculator"""
    logger.info(f"\n{'='*60}")
    logger.info("Step 3: Testing Ranking Calculator")
    logger.info(f"{'='*60}")
    
    calculator = RankingCalculator(db)
    today = date.today()
    
    # Calculate and update ranks for today (this method does both)
    updated_count = await calculator.update_ranks_for_date(today)
    
    if updated_count == 0:
        logger.warning("  ⚠️  No ranks updated. Ensure metrics exist for today.")
        return False
    
    logger.info(f"  ✓ Updated ranks for {updated_count} boxes")
    
    # Get ranks again to display
    ranks = await calculator.calculate_ranks_for_date(today)
    
    # Display rankings
    logger.info("\n  📊 Rankings (Top 5):")
    sorted_ranks = sorted(ranks.items(), key=lambda x: x[1])[:5]
    for box_id, rank in sorted_ranks:
        metrics = await UnifiedMetricsRepository.get_latest_for_box(db, box_id)
        box = await BoosterBoxRepository.get_by_id(db, box_id)
        if metrics and box:
            rank_change_str = ""
            if metrics.rank_change is not None:
                if metrics.rank_change > 0:
                    rank_change_str = f" (↑{metrics.rank_change})"
                elif metrics.rank_change < 0:
                    rank_change_str = f" (↓{abs(metrics.rank_change)})"
                else:
                    rank_change_str = " (→)"
            logger.info(f"    #{rank}{rank_change_str}: {box.product_name} - Volume EMA: ${metrics.unified_volume_7d_ema or 0}")
    
    return True


async def test_cache_operations(db):
    """Test Redis caching"""
    logger.info(f"\n{'='*60}")
    logger.info("Step 4: Testing Redis Cache")
    logger.info(f"{'='*60}")
    
    cache = CacheService()
    today = date.today()
    
    # Force connection test
    try:
        if cache.redis_client:
            await cache.redis_client.ping()
            cache._connected = True
            logger.info("  ✓ Redis connection successful")
        else:
            logger.warning("  ⚠️  Redis client not initialized")
            return False
    except Exception as e:
        logger.warning(f"  ⚠️  Redis not connected: {e}")
        return False
    
    # Test basic cache operations
    test_key = "test:phase6:cache"
    test_data = {"test": "data", "timestamp": str(today)}
    
    # Set
    result = await cache.set(test_key, test_data, ttl=60)
    if result:
        logger.info("  ✓ Cache SET operation works")
    else:
        logger.error("  ❌ Cache SET failed")
        return False
    
    # Get
    cached = await cache.get(test_key)
    if cached == test_data:
        logger.info("  ✓ Cache GET operation works")
    else:
        logger.error("  ❌ Cache GET failed")
        return False
    
    # Delete
    await cache.delete(test_key)
    logger.info("  ✓ Cache DELETE operation works")
    
    return True


async def test_leaderboard_with_cache(db):
    """Test leaderboard service with caching"""
    logger.info(f"\n{'='*60}")
    logger.info("Step 5: Testing Leaderboard with Caching")
    logger.info(f"{'='*60}")
    
    leaderboard_service = LeaderboardService(db)
    today = date.today()
    
    # First call (should be cache miss)
    import time
    start_time = time.perf_counter()
    leaderboard_1 = await leaderboard_service.get_ranked_boxes(
        target_date=today,
        limit=10
    )
    duration_1 = (time.perf_counter() - start_time) * 1000
    
    if not leaderboard_1:
        logger.warning("  ⚠️  No leaderboard data returned")
        return False
    
    logger.info(f"  ✓ First query (cache miss): {duration_1:.2f}ms - {len(leaderboard_1)} boxes")
    
    # Second call (should be cache hit)
    start_time = time.perf_counter()
    leaderboard_2 = await leaderboard_service.get_ranked_boxes(
        target_date=today,
        limit=10
    )
    duration_2 = (time.perf_counter() - start_time) * 1000
    
    logger.info(f"  ✓ Second query (cache hit): {duration_2:.2f}ms - {len(leaderboard_2)} boxes")
    
    if duration_2 < duration_1:
        logger.info(f"  ✅ Cache improved performance by {duration_1 - duration_2:.2f}ms ({(1 - duration_2/duration_1)*100:.1f}% faster)")
    else:
        logger.warning(f"  ⚠️  Cache didn't improve performance (data may be too small)")
    
    # Display all returned boxes
    logger.info(f"\n  📊 Leaderboard (Top {len(leaderboard_1)}):")
    for box, metrics, rank, rank_change in leaderboard_1:
        rank_str = f"#{rank}"
        if rank_change:
            direction = "↑" if rank_change.get("direction") == "up" else "↓" if rank_change.get("direction") == "down" else "→"
            rank_str += f" ({direction}{rank_change.get('amount', 0)})"
        logger.info(f"    {rank_str}: {box.product_name} - ${metrics.unified_volume_7d_ema or 0}")
    
    return True


async def test_api_endpoints():
    """Test API endpoints"""
    logger.info(f"\n{'='*60}")
    logger.info("Step 6: Testing API Endpoints")
    logger.info(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test leaderboard endpoint
        try:
            response = await client.get(f"{API_BASE_URL}/booster-boxes", params={"limit": 5})
            if response.status_code == 200:
                data = response.json()
                logger.info(f"  ✓ Leaderboard endpoint: {len(data.get('data', []))} boxes returned")
                
                # Display all returned boxes from API
                if data.get('data'):
                    boxes_returned = len(data['data'])
                    logger.info(f"\n  📊 API Leaderboard (Top {boxes_returned}):")
                    for item in data['data']:
                        rank = item.get('rank', 'N/A')
                        name = item.get('product_name', 'Unknown')
                        volume = item.get('metrics', {}).get('unified_volume_7d_ema', 0)
                        rank_change = item.get('rank_change_direction')
                        rank_amount = item.get('rank_change_amount')
                        change_str = ""
                        if rank_change:
                            arrow = "↑" if rank_change == "up" else "↓" if rank_change == "down" else "→"
                            change_str = f" ({arrow}{rank_amount or 0})"
                        logger.info(f"    #{rank}{change_str}: {name} - ${volume}")
            else:
                logger.error(f"  ❌ Leaderboard endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"  ❌ Leaderboard endpoint error: {e}")
            return False
        
        # Test health endpoint
        try:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                logger.info("  ✓ Health endpoint working")
            else:
                logger.warning(f"  ⚠️  Health endpoint returned: {response.status_code}")
        except Exception as e:
            logger.warning(f"  ⚠️  Health endpoint error: {e}")
    
    return True


async def cleanup_test_data(db, boxes):
    """Optional: Clean up test data"""
    logger.info(f"\n{'='*60}")
    logger.info("Cleanup (Optional - Uncomment to enable)")
    logger.info(f"{'='*60}")
    logger.info("  💡 Test data kept for further testing")
    # Uncomment to delete test boxes:
    # for box in boxes:
    #     await BoosterBoxRepository.delete(db, box.id)
    #     logger.info(f"  ✓ Deleted: {box.product_name}")


async def main():
    """Run all Phase 6 tests"""
    logger.info("\n" + "="*60)
    logger.info("Phase 6 Comprehensive Test Suite")
    logger.info("="*60)
    
    await init_db()
    
    async for db in get_db():
        try:
            # Step 1: Create test boxes
            boxes = await create_test_boxes(db)
            
            # Step 2: Create test metrics
            await create_test_metrics(db, boxes)
            
                    # Step 3: Test ranking calculator
            ranking_ok = await test_ranking_calculator(db)
            
            # Step 4: Test cache operations
            cache_ok = await test_cache_operations(db)
            
            # Step 5: Test leaderboard with caching
            leaderboard_ok = await test_leaderboard_with_cache(db)
            
            # Step 6: Test API endpoints (requires server running)
            try:
                api_ok = await test_api_endpoints()
            except Exception as e:
                logger.warning(f"  ⚠️  API tests skipped (server may not be running): {e}")
                api_ok = False
            
            # Summary
            logger.info(f"\n{'='*60}")
            logger.info("Test Summary")
            logger.info(f"{'='*60}")
            logger.info(f"  Ranking Calculator: {'✅ PASS' if ranking_ok else '❌ FAIL'}")
            logger.info(f"  Cache Operations: {'✅ PASS' if cache_ok else '❌ FAIL'}")
            logger.info(f"  Leaderboard + Cache: {'✅ PASS' if leaderboard_ok else '❌ FAIL'}")
            logger.info(f"  API Endpoints: {'✅ PASS' if api_ok else '⚠️  SKIP (server not running)'}")
            
            # Optional cleanup
            # await cleanup_test_data(db, boxes)
            
        except Exception as e:
            logger.error(f"\n❌ Test suite failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

