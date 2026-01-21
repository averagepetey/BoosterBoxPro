"""
Chrome Extension API Endpoints
Provides market data for the BoosterBoxPro Chrome extension
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from sqlalchemy import select, desc
from app.database import AsyncSessionLocal
from app.models.booster_box import BoosterBox
from app.models.unified_box_metrics import UnifiedBoxMetrics

router = APIRouter(prefix="/extension", tags=["Extension"])


def get_box_image_url(product_name: str | None) -> str | None:
    """Generate image URL for a booster box"""
    if not product_name:
        return None
    
    import re
    set_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
    if not set_match:
        return None
    
    set_code = set_match.group(0).upper()
    filename = f"{set_code.lower()}.png"
    return f"/images/boxes/{filename}"


@router.get("/box/{set_code}")
async def get_box_by_set_code(
    set_code: str,
    listing_price: Optional[float] = Query(None, description="Current marketplace listing price")
):
    """
    Get full box data by set code (e.g., OP-01, OP-13, EB-01)
    Returns all metrics shown in box detail page for extension sidebar.
    """
    # Normalize set code (OP01 -> OP-01)
    set_code = set_code.upper()
    if not '-' in set_code:
        # Insert dash after prefix
        if set_code.startswith('OP'):
            set_code = f"OP-{set_code[2:].zfill(2)}"
        elif set_code.startswith('EB'):
            set_code = f"EB-{set_code[2:].zfill(2)}"
        elif set_code.startswith('PRB'):
            set_code = f"PRB-{set_code[3:].zfill(2)}"
    
    async with AsyncSessionLocal() as db:
        # Find box by set code in product name
        # Use first() instead of one_or_none() to handle variants (Blue, White, etc.)
        stmt = select(BoosterBox).where(
            BoosterBox.product_name.ilike(f"%{set_code}%")
        ).limit(1)
        result = await db.execute(stmt)
        db_box = result.scalar_one_or_none()
        
        if not db_box:
            return {"matched": False, "error": f"Box {set_code} not found"}
        
        # Get latest metrics
        metrics_stmt = select(UnifiedBoxMetrics).where(
            UnifiedBoxMetrics.booster_box_id == db_box.id
        ).order_by(desc(UnifiedBoxMetrics.metric_date)).limit(1)
        
        metrics_result = await db.execute(metrics_stmt)
        latest_metrics = metrics_result.scalar_one_or_none()
        
        # Build metrics dict
        metrics = {}
        if latest_metrics:
            metrics = {
                "floor_price_usd": float(latest_metrics.floor_price_usd) if latest_metrics.floor_price_usd else None,
                "floor_price_1d_change_pct": float(latest_metrics.floor_price_1d_change_pct) if latest_metrics.floor_price_1d_change_pct else 0.0,
                "floor_price_30d_change_pct": None,  # Need to calculate from historical
                "daily_volume_usd": float(latest_metrics.unified_volume_usd / 30) if latest_metrics.unified_volume_usd else None,
                "unified_volume_usd": float(latest_metrics.unified_volume_usd) if latest_metrics.unified_volume_usd else None,
                "unified_volume_7d_ema": float(latest_metrics.unified_volume_7d_ema) if latest_metrics.unified_volume_7d_ema else None,
                "sales_per_day": float(latest_metrics.boxes_sold_per_day) if latest_metrics.boxes_sold_per_day else None,
                "boxes_sold_30d_avg": float(latest_metrics.boxes_sold_30d_avg) if latest_metrics.boxes_sold_30d_avg else None,
                "active_listings_count": latest_metrics.active_listings_count,
                "boxes_added_today": latest_metrics.boxes_added_today,
                "liquidity_score": float(latest_metrics.liquidity_score) if latest_metrics.liquidity_score else None,
                "days_to_20pct_increase": float(latest_metrics.days_to_20pct_increase) if latest_metrics.days_to_20pct_increase else None,
            }
        
        # Get 30d price change from historical data
        try:
            from app.services.historical_data import get_box_month_over_month_price_change
            price_change_30d = get_box_month_over_month_price_change(str(db_box.id))
            if price_change_30d is not None:
                metrics["floor_price_30d_change_pct"] = price_change_30d
        except:
            pass
        
        # Get price history for mini chart
        price_history = []
        try:
            from app.services.historical_data import get_box_price_history
            history = get_box_price_history(str(db_box.id), days=30)
            price_history = [
                {"date": h.get("date"), "floor_price_usd": h.get("floor_price_usd")}
                for h in history if h.get("floor_price_usd")
            ]
        except:
            pass
        
        # Listing comparison
        listing_comparison = None
        if listing_price and metrics.get("floor_price_usd"):
            floor = metrics["floor_price_usd"]
            diff = listing_price - floor
            diff_pct = (diff / floor) * 100 if floor > 0 else 0
            
            if diff_pct <= 0:
                verdict = "good"
            elif diff_pct <= 10:
                verdict = "fair"
            else:
                verdict = "overpriced"
            
            listing_comparison = {
                "listing_price": listing_price,
                "difference_usd": round(diff, 2),
                "difference_pct": round(diff_pct, 1),
                "verdict": verdict
            }
        
        return {
            "matched": True,
            "box": {
                "id": str(db_box.id),
                "product_name": db_box.product_name,
                "set_code": set_code,
                "set_name": db_box.set_name,
                "game_type": db_box.game_type or "One Piece",
                "image_url": get_box_image_url(db_box.product_name),
                "reprint_risk": db_box.reprint_risk or "UNKNOWN",
                "dashboard_url": f"http://localhost:3000/box/{db_box.id}"
            },
            "metrics": metrics,
            "price_history": price_history,
            "listing_comparison": listing_comparison
        }


@router.get("/compare")
async def compare_boxes(
    box1: str = Query(..., description="First box set code"),
    box2: str = Query(..., description="Second box set code")
):
    """
    Compare two boxes side-by-side.
    """
    # Fetch both boxes
    data1 = await get_box_by_set_code(box1)
    data2 = await get_box_by_set_code(box2)
    
    if not data1.get("matched") or not data2.get("matched"):
        return {"error": "One or both boxes not found"}
    
    m1 = data1.get("metrics", {})
    m2 = data2.get("metrics", {})
    
    # Determine winners for each metric
    def get_winner(val1, val2, higher_is_better=True):
        if val1 is None and val2 is None:
            return "tie"
        if val1 is None:
            return "box2"
        if val2 is None:
            return "box1"
        if val1 == val2:
            return "tie"
        if higher_is_better:
            return "box1" if val1 > val2 else "box2"
        else:
            return "box1" if val1 < val2 else "box2"
    
    comparison = {
        "floor_price_winner": get_winner(m1.get("floor_price_usd"), m2.get("floor_price_usd"), higher_is_better=False),
        "growth_winner": get_winner(m1.get("floor_price_30d_change_pct"), m2.get("floor_price_30d_change_pct")),
        "volume_winner": get_winner(m1.get("daily_volume_usd"), m2.get("daily_volume_usd")),
        "sales_winner": get_winner(m1.get("sales_per_day"), m2.get("sales_per_day")),
        "liquidity_winner": get_winner(m1.get("liquidity_score"), m2.get("liquidity_score")),
        "investment_winner": get_winner(m1.get("days_to_20pct_increase"), m2.get("days_to_20pct_increase"), higher_is_better=False),
    }
    
    return {
        "box1": data1,
        "box2": data2,
        "comparison": comparison
    }


@router.get("/search")
async def search_boxes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for boxes (for Compare dropdown).
    """
    async with AsyncSessionLocal() as db:
        stmt = select(BoosterBox).where(
            BoosterBox.product_name.ilike(f"%{q}%")
        ).limit(limit)
        
        result = await db.execute(stmt)
        boxes = result.scalars().all()
        
        # Get basic info for each
        results = []
        for box in boxes:
            # Extract set code
            import re
            match = re.search(r'(OP|EB|PRB)-\d+', box.product_name, re.IGNORECASE)
            set_code = match.group(0).upper() if match else None
            
            # Get latest price
            metrics_stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id
            ).order_by(desc(UnifiedBoxMetrics.metric_date)).limit(1)
            
            metrics_result = await db.execute(metrics_stmt)
            metrics = metrics_result.scalar_one_or_none()
            
            results.append({
                "set_code": set_code,
                "name": box.set_name or box.product_name,
                "floor_price": float(metrics.floor_price_usd) if metrics and metrics.floor_price_usd else None
            })
        
        return {"results": results}


@router.get("/top-movers")
async def get_top_movers():
    """
    Get top gainers and losers for extension popup.
    """
    async with AsyncSessionLocal() as db:
        # Get all boxes with metrics
        stmt = select(BoosterBox, UnifiedBoxMetrics).join(
            UnifiedBoxMetrics,
            BoosterBox.id == UnifiedBoxMetrics.booster_box_id
        ).order_by(desc(UnifiedBoxMetrics.metric_date))
        
        result = await db.execute(stmt)
        rows = result.all()
        
        # Deduplicate by box (keep latest metrics)
        seen = set()
        boxes_with_metrics = []
        for box, metrics in rows:
            if box.id not in seen:
                seen.add(box.id)
                
                # Extract set code
                import re
                match = re.search(r'(OP|EB|PRB)-\d+', box.product_name, re.IGNORECASE)
                set_code = match.group(0).upper() if match else None
                
                if set_code and metrics.floor_price_1d_change_pct is not None:
                    boxes_with_metrics.append({
                        "set_code": set_code,
                        "name": box.set_name or box.product_name,
                        "price": float(metrics.floor_price_usd) if metrics.floor_price_usd else None,
                        "change_pct": float(metrics.floor_price_1d_change_pct) if metrics.floor_price_1d_change_pct else 0
                    })
        
        # Sort by change
        gainers = sorted(
            [b for b in boxes_with_metrics if b["change_pct"] > 0],
            key=lambda x: x["change_pct"],
            reverse=True
        )[:3]
        
        losers = sorted(
            [b for b in boxes_with_metrics if b["change_pct"] < 0],
            key=lambda x: x["change_pct"]
        )[:2]
        
        return {
            "gainers": gainers,
            "losers": losers
        }

