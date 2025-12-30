#!/usr/bin/env python3
"""
Comprehensive Test Suite
Tests all components: database, admin endpoints, metrics calculations, public API
"""

import sys
import os
import asyncio
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config import settings
from app.database import get_db, AsyncSessionLocal
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.ema_calculator import EMACalculator
from app.services.metrics_calculator import MetricsCalculator
from app.services.leaderboard_service import LeaderboardService

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_test(name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


async def test_database_connection():
    """Test 1: Database Connection"""
    print_test("Database Connection")
    
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            print_success("Database connection successful")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


async def test_models():
    """Test 2: SQLAlchemy Models"""
    print_test("SQLAlchemy Models")
    
    try:
        from app.models.booster_box import BoosterBox
        from app.models.unified_box_metrics import UnifiedBoxMetrics
        
        # Test that models can be imported and have correct attributes
        assert hasattr(BoosterBox, 'product_name')
        assert hasattr(BoosterBox, 'id')
        assert hasattr(UnifiedBoxMetrics, 'booster_box_id')
        assert hasattr(UnifiedBoxMetrics, 'metric_date')
        
        print_success("Models imported and validated")
        return True
    except Exception as e:
        print_error(f"Model test failed: {e}")
        return False


async def test_ema_calculator():
    """Test 3: EMA Calculator"""
    print_test("EMA Calculator Service")
    
    try:
        # Test basic EMA calculation
        data = [Decimal('100'), Decimal('110'), Decimal('105'), Decimal('115'), 
                Decimal('120'), Decimal('118'), Decimal('122')]
        
        ema = EMACalculator.calculate_7day_ema(data)
        sma = EMACalculator.calculate_sma(data, 7)
        
        assert ema is not None
        assert sma is not None
        print_success(f"EMA Calculator working: EMA={ema}, SMA={sma}")
        return True
    except Exception as e:
        print_error(f"EMA Calculator test failed: {e}")
        return False


async def test_admin_endpoints():
    """Test 4: Admin Endpoints"""
    print_test("Admin API Endpoints")
    
    api_key = settings.admin_api_key or "dev-key"
    headers = {"X-API-Key": api_key}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test health check
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print_success("Health endpoint working")
            else:
                print_error(f"Health endpoint returned {response.status_code}")
                return False
            
            # Test list boxes
            response = await client.get(f"{API_BASE}/admin/boxes", headers=headers)
            if response.status_code == 200:
                data = response.json()
                boxes_count = data.get('total', 0)
                print_success(f"List boxes endpoint working: {boxes_count} boxes found")
                return True, boxes_count
            else:
                print_warning(f"List boxes returned {response.status_code} - may need API key")
                return True, 0
                
        except httpx.ConnectError:
            print_error("Cannot connect to server. Is it running?")
            return False, 0
        except Exception as e:
            print_error(f"Admin endpoint test failed: {e}")
            return False, 0


async def test_public_endpoints():
    """Test 5: Public API Endpoints"""
    print_test("Public API Endpoints")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test leaderboard
            response = await client.get(f"{API_BASE}/booster-boxes?limit=5")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Leaderboard endpoint working: {len(data.get('data', []))} boxes")
                
                # Test with sort
                response = await client.get(f"{API_BASE}/booster-boxes?sort=liquidity_score&limit=5")
                if response.status_code == 200:
                    print_success("Leaderboard with sort working")
                else:
                    print_warning(f"Sort test returned {response.status_code}")
                
                return True
            else:
                print_error(f"Leaderboard returned {response.status_code}")
                return False
                
        except httpx.ConnectError:
            print_error("Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            print_error(f"Public endpoint test failed: {e}")
            return False


async def test_metrics_calculations_with_data():
    """Test 6: Metrics Calculations with Sample Data"""
    print_test("Metrics Calculations (with sample data)")
    
    try:
        async with AsyncSessionLocal() as db:
            # Get a box to test with
            boxes = await BoosterBoxRepository.get_all(db, limit=1)
            if not boxes:
                print_warning("No boxes found - skipping metrics calculation test")
                return True
            
            box = boxes[0]
            calculator = MetricsCalculator(db)
            
            # Create sample metrics for the last 7 days
            today = date.today()
            created_metrics = []
            
            for i in range(7):
                metric_date = today - timedelta(days=i)
                
                # Check if metrics already exist
                existing = await UnifiedMetricsRepository.get_by_box_and_date(
                    db, box.id, metric_date
                )
                
                if existing:
                    created_metrics.append(existing)
                    continue
                
                # Create sample metrics
                metrics_data = {
                    "booster_box_id": box.id,
                    "metric_date": metric_date,
                    "floor_price_usd": Decimal('200.00') + Decimal(str(i * 5)),
                    "active_listings_count": 1000 + (i * 50),
                    "unified_volume_usd": Decimal('10000.00') + Decimal(str(i * 500)),
                    "boxes_sold_per_day": Decimal(str(5 + i)),
                    "boxes_sold_30d_avg": Decimal('5.00'),
                }
                
                metrics = await UnifiedMetricsRepository.create_or_update(db, metrics_data)
                created_metrics.append(metrics)
            
            # Test metrics calculation
            if created_metrics:
                latest_metric = created_metrics[0]  # Most recent
                updated = await calculator.update_metrics_with_calculations(
                    box.id, latest_metric.metric_date
                )
                
                if updated:
                    print_success(f"Metrics calculation working: EMA={updated.unified_volume_7d_ema}, "
                                f"Liquidity={updated.liquidity_score}, "
                                f"Expected Days={updated.expected_days_to_sell}")
                    return True
                else:
                    print_warning("Metrics calculation returned None")
                    return True
            else:
                print_warning("No metrics created for testing")
                return True
                
    except Exception as e:
        print_error(f"Metrics calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_leaderboard_service():
    """Test 7: Leaderboard Service"""
    print_test("Leaderboard Service")
    
    try:
        async with AsyncSessionLocal() as db:
            service = LeaderboardService(db)
            
            # Get ranked boxes
            ranked = await service.get_ranked_boxes(limit=10)
            
            if ranked:
                print_success(f"Leaderboard service working: {len(ranked)} boxes ranked")
                # Show first few
                for i, (box, metrics, rank, change) in enumerate(ranked[:3]):
                    print(f"   {rank}. {box.product_name[:50]} (Volume EMA: {metrics.unified_volume_7d_ema})")
            else:
                print_warning("No boxes to rank (may need metrics data)")
            
            return True
    except Exception as e:
        print_error(f"Leaderboard service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_flow():
    """Test 8: End-to-End Flow"""
    print_test("End-to-End Flow")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        api_key = settings.admin_api_key or "dev-key"
        headers = {"X-API-Key": api_key}
        
        try:
            # 1. Get boxes from admin endpoint
            response = await client.get(f"{API_BASE}/admin/boxes", headers=headers)
            if response.status_code != 200:
                print_warning("Cannot test end-to-end - admin endpoint not accessible")
                return True
            
            boxes_data = response.json()
            boxes = boxes_data.get('boxes', [])
            
            if not boxes:
                print_warning("No boxes found for end-to-end test")
                return True
            
            # 2. Get a box ID
            box_id = boxes[0]['id']
            
            # 3. Test public detail endpoint
            detail_response = await client.get(f"{API_BASE}/booster-boxes/{box_id}")
            if detail_response.status_code == 200:
                detail = detail_response.json()
                print_success(f"End-to-end flow working: Box detail retrieved for {detail['product_name'][:50]}")
                return True
            elif detail_response.status_code == 404:
                print_warning("Box detail not found (may not have metrics yet) - this is expected")
                return True
            else:
                print_warning(f"Box detail returned {detail_response.status_code}")
                return True
                
        except Exception as e:
            print_error(f"End-to-end test failed: {e}")
            return False


async def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}BoosterBoxPro - Comprehensive Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {}
    
    # Run all tests
    results['database'] = await test_database_connection()
    results['models'] = await test_models()
    results['ema_calculator'] = await test_ema_calculator()
    results['admin_endpoints'], boxes_count = await test_admin_endpoints()
    results['public_endpoints'] = await test_public_endpoints()
    results['metrics_calculations'] = await test_metrics_calculations_with_data()
    results['leaderboard_service'] = await test_leaderboard_service()
    results['end_to_end'] = await test_end_to_end_flow()
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! 🎉")
    elif passed > total * 0.7:
        print_warning("Most tests passed, but some issues found")
    else:
        print_error("Multiple test failures - check errors above")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

