#!/usr/bin/env python3
"""
Test Database and Services
Tests database connection, models, repositories, and services
"""

import sys
import os
import asyncio
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.ema_calculator import EMACalculator
from app.services.metrics_calculator import MetricsCalculator
from app.services.leaderboard_service import LeaderboardService

def test(name):
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print('='*60)
    return True

def success(msg):
    print(f"✅ {msg}")

def error(msg):
    print(f"❌ {msg}")

def warning(msg):
    print(f"⚠️  {msg}")

async def test_db_connection():
    test("Database Connection")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            if value == 1:
                success("Database connection successful")
                return True
            else:
                error("Database query returned unexpected value")
                return False
    except Exception as e:
        error(f"Database connection failed: {e}")
        return False

async def test_models():
    test("SQLAlchemy Models")
    try:
        from app.models.booster_box import BoosterBox
        from app.models.unified_box_metrics import UnifiedBoxMetrics
        
        # Check attributes
        assert hasattr(BoosterBox, 'id')
        assert hasattr(BoosterBox, 'product_name')
        assert hasattr(BoosterBox, 'set_name')
        
        assert hasattr(UnifiedBoxMetrics, 'booster_box_id')
        assert hasattr(UnifiedBoxMetrics, 'metric_date')
        assert hasattr(UnifiedBoxMetrics, 'unified_volume_7d_ema')
        
        success("Models validated - all required attributes present")
        return True
    except Exception as e:
        error(f"Model test failed: {e}")
        return False

async def test_repositories():
    test("Repository Methods")
    try:
        async with AsyncSessionLocal() as db:
            # Test booster box repository
            boxes = await BoosterBoxRepository.get_all(db, limit=5)
            count = await BoosterBoxRepository.count(db)
            
            success(f"BoosterBoxRepository working: {count} boxes found")
            
            # Test unified metrics repository
            if boxes:
                box_id = boxes[0].id
                from datetime import date
                latest = await UnifiedMetricsRepository.get_latest_for_box(db, box_id)
                
                if latest:
                    success(f"UnifiedMetricsRepository working: latest metrics found for {boxes[0].product_name[:40]}")
                else:
                    warning(f"No metrics found for {boxes[0].product_name[:40]} (this is expected if no data entered)")
            
            return True
    except Exception as e:
        error(f"Repository test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ema_calculator():
    test("EMA Calculator Service")
    try:
        # Test with sample data
        data = [
            Decimal('100'), Decimal('110'), Decimal('105'), 
            Decimal('115'), Decimal('120'), Decimal('118'), Decimal('122')
        ]
        
        ema_7d = EMACalculator.calculate_7day_ema(data)
        sma_7d = EMACalculator.calculate_sma(data, 7)
        
        assert ema_7d is not None
        assert sma_7d is not None
        
        success(f"EMA Calculator working: 7-day EMA={ema_7d}, 7-day SMA={sma_7d}")
        
        # Test with more data
        data_extended = data + [Decimal('125'), Decimal('130')]
        ema_extended = EMACalculator.calculate_7day_ema(data_extended)
        assert ema_extended is not None
        success(f"EMA Calculator handles extended data: EMA={ema_extended}")
        
        return True
    except Exception as e:
        error(f"EMA Calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_leaderboard_service():
    test("Leaderboard Service")
    try:
        async with AsyncSessionLocal() as db:
            service = LeaderboardService(db)
            
            # Get ranked boxes
            ranked = await service.get_ranked_boxes(limit=10)
            
            success(f"LeaderboardService working: {len(ranked)} boxes ranked")
            
            if ranked:
                # Show top 3
                print("\nTop 3 ranked boxes:")
                for box, metrics, rank, change_info in ranked[:3]:
                    volume = metrics.unified_volume_7d_ema or 0
                    print(f"   {rank}. {box.product_name[:50]}")
                    print(f"      Volume EMA: {volume}")
            else:
                warning("No boxes to rank (may need metrics data)")
            
            return True
    except Exception as e:
        error(f"LeaderboardService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "="*60)
    print("BoosterBoxPro - Database & Services Test Suite")
    print("="*60)
    
    results = {
        "Database Connection": await test_db_connection(),
        "SQLAlchemy Models": await test_models(),
        "Repositories": await test_repositories(),
        "EMA Calculator": await test_ema_calculator(),
        "Leaderboard Service": await test_leaderboard_service(),
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    print("\n" + "="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        success("All database and service tests passed! 🎉")
    elif passed >= total * 0.8:
        warning("Most tests passed")
    else:
        error("Multiple failures detected")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

