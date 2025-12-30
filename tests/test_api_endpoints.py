"""
Integration tests for API endpoints
Tests all public API endpoints with realistic scenarios

Note: These tests require a running database connection.
Run with: pytest tests/test_api_endpoints.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import asyncio
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_db
from app.config import settings
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.metrics_calculator import MetricsCalculator
from app.services.ranking_calculator import RankingCalculator

# Import shared fixtures
from tests.conftest import TestSessionLocal


async def override_get_db():
    """Override database dependency for testing"""
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture(scope="function")
async def test_box(db_session):
    """Create a test booster box for testing"""
    box_data = {
        "product_name": "Test Box OP-01",
        "set_name": "Test Set",
        "game_type": "One Piece",
        "release_date": date(2023, 1, 1),
        "reprint_risk": "LOW",
        "estimated_total_supply": 10000,
    }
    box = await BoosterBoxRepository.create(db_session, box_data)
    yield box


@pytest.fixture(scope="function")
async def test_metrics(db_session, test_box):
    """Create test metrics for the test box"""
    today = date.today()
    metrics_calculator = MetricsCalculator(db_session)
    
    # Create 7 days of metrics for EMA calculation
    for i in range(7):
        metric_date = today - timedelta(days=6 - i)
        metrics_data = {
            "booster_box_id": test_box.id,
            "metric_date": metric_date,
            "floor_price_usd": Decimal("200.00") + Decimal(str(i * 5)),
            "active_listings_count": 1000 + (i * 10),
            "unified_volume_usd": Decimal("10000.00") + Decimal(str(i * 1000)),
            "boxes_sold_per_day": Decimal(str(10 + i)),
            "boxes_sold_30d_avg": Decimal(str(10 + i)),
        }
        await UnifiedMetricsRepository.create_or_update(db_session, metrics_data)
        await metrics_calculator.update_metrics_with_calculations(test_box.id, metric_date)
    
    # Calculate ranks for today
    ranking_calculator = RankingCalculator(db_session)
    await ranking_calculator.update_ranks_for_date(today)
    
    yield


def test_leaderboard_endpoint(client):
    """Test GET /api/v1/booster-boxes endpoint"""
    response = client.get("/api/v1/booster-boxes", params={"limit": 10})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)
    # Note: May be empty if no data in database
    if len(data["data"]) > 0:
        first_box = data["data"][0]
        assert "id" in first_box
        assert "product_name" in first_box
        assert "rank" in first_box
        assert "metrics" in first_box


def test_leaderboard_endpoint_with_limit(client):
    """Test leaderboard endpoint with limit parameter"""
    response = client.get("/api/v1/booster-boxes", params={"limit": 5})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 5


def test_leaderboard_endpoint_with_date(client):
    """Test leaderboard endpoint with date parameter"""
    today = date.today()
    response = client.get("/api/v1/booster-boxes", params={"date": today.isoformat(), "limit": 10})
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_box_detail_endpoint(client, db_session, test_box, test_metrics):
    """Test GET /api/v1/booster-boxes/{box_id} endpoint"""
    response = client.get(f"/api/v1/booster-boxes/{test_box.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == str(test_box.id)
    assert "product_name" in data
    assert "metrics" in data
    assert "time_series_data" in data
    assert "rank_history" in data


def test_box_detail_endpoint_not_found(client):
    """Test box detail endpoint with non-existent box ID"""
    fake_id = uuid4()
    response = client.get(f"/api/v1/booster-boxes/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "detail" in data


@pytest.mark.asyncio
async def test_time_series_endpoint(client, db_session, test_box, test_metrics):
    """Test GET /api/v1/booster-boxes/{box_id}/time-series endpoint"""
    response = client.get(f"/api/v1/booster-boxes/{test_box.id}/time-series")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        first_point = data[0]
        assert "date" in first_point
        assert "floor_price_usd" in first_point or first_point["floor_price_usd"] is None


@pytest.mark.asyncio
async def test_time_series_endpoint_with_date_range(client, db_session, test_box, test_metrics):
    """Test time-series endpoint with custom date range"""
    today = date.today()
    start = today - timedelta(days=7)
    
    response = client.get(
        f"/api/v1/booster-boxes/{test_box.id}/time-series",
        params={
            "start_date": start.isoformat(),
            "end_date": today.isoformat()
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_sparkline_endpoint(client, db_session, test_box, test_metrics):
    """Test GET /api/v1/booster-boxes/{box_id}/sparkline endpoint"""
    response = client.get(f"/api/v1/booster-boxes/{test_box.id}/sparkline", params={"days": 7})
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        first_point = data[0]
        assert "timestamp" in first_point
        assert "price" in first_point or first_point["price"] is None


@pytest.mark.asyncio
async def test_sparkline_endpoint_invalid_days(client, db_session, test_box):
    """Test sparkline endpoint with invalid days parameter"""
    # Days > 30 should fail validation
    response = client.get(f"/api/v1/booster-boxes/{test_box.id}/sparkline", params={"days": 100})
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_leaderboard_invalid_limit(client):
    """Test leaderboard endpoint with invalid limit"""
    # Limit > 100 should fail validation
    response = client.get("/api/v1/booster-boxes", params={"limit": 200})
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_error_response_format(client):
    """Test that error responses have consistent format"""
    fake_id = uuid4()
    response = client.get(f"/api/v1/booster-boxes/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    
    # Check error response structure
    assert "error" in data
    assert "detail" in data
    assert "path" in data


def test_health_endpoint(client):
    """Test GET /health endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test GET / endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data

