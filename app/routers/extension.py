"""
Chrome Extension API Endpoints
Provides market data for the BoosterBoxPro Chrome extension.
Uses same source of truth as box detail: app.services.box_detail_service.build_box_detail_data.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from sqlalchemy import select, desc
from app.database import AsyncSessionLocal
from app.models.booster_box import BoosterBox
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.services.box_detail_service import build_box_detail_data

# Extension endpoints work without auth so the Chrome extension can fetch data.
async def optional_extension_user():
    return None

router = APIRouter(prefix="/extension", tags=["Extension"])


def _normalize_set_code(set_code: str) -> str:
    set_code = set_code.upper()
    if "-" not in set_code:
        if set_code.startswith("OP"):
            set_code = f"OP-{set_code[2:].zfill(2)}"
        elif set_code.startswith("EB"):
            set_code = f"EB-{set_code[2:].zfill(2)}"
        elif set_code.startswith("PRB"):
            set_code = f"PRB-{set_code[3:].zfill(2)}"
    return set_code


async def _get_extension_box_response(db, set_code: str, listing_price: Optional[float] = None):
    """Internal: fetch box by set_code using shared box detail service. Returns extension response shape."""
    set_code = _normalize_set_code(set_code)
    stmt = select(BoosterBox).where(BoosterBox.product_name.ilike(f"%{set_code}%")).limit(1)
    result = await db.execute(stmt)
    db_box = result.scalar_one_or_none()
    if not db_box:
        return {"matched": False, "error": f"Box {set_code} not found"}
    data = await build_box_detail_data(db, db_box)
    metrics = data["metrics"]
    listing_comparison = None
    if listing_price is not None and metrics.get("floor_price_usd"):
        floor = metrics["floor_price_usd"]
        diff = listing_price - floor
        diff_pct = (diff / floor) * 100 if floor > 0 else 0
        verdict = "good" if diff_pct <= 0 else ("fair" if diff_pct <= 10 else "overpriced")
        listing_comparison = {
            "listing_price": listing_price,
            "difference_usd": round(diff, 2),
            "difference_pct": round(diff_pct, 1),
            "verdict": verdict,
        }
    return {
        "matched": True,
        "box": {
            "id": data["id"],
            "product_name": data["product_name"],
            "set_code": set_code,
            "set_name": data["set_name"],
            "game_type": data["game_type"],
            "image_url": data["image_url"],
            "reprint_risk": data["reprint_risk"],
            "dashboard_url": f"http://localhost:3000/boxes/{data['id']}",
        },
        "metrics": metrics,
        "price_history": [],
        "listing_comparison": listing_comparison,
    }


@router.get("/box/{set_code}")
async def get_box_by_set_code(
    set_code: str,
    listing_price: Optional[float] = Query(None, description="Current marketplace listing price"),
    current_user=Depends(optional_extension_user),
):
    """
    Get full box data by set code (e.g., OP-01, OP-13, EB-01).
    Returns the same metrics as the box detail page (single source of truth).
    """
    async with AsyncSessionLocal() as db:
        return await _get_extension_box_response(db, set_code, listing_price)


@router.get("/compare")
async def compare_boxes(
    box1: str = Query(..., description="First box set code"),
    box2: str = Query(..., description="Second box set code"),
    current_user=Depends(optional_extension_user),
):
    """
    Compare two boxes side-by-side.
    """
    async with AsyncSessionLocal() as db:
        data1 = await _get_extension_box_response(db, box1)
        data2 = await _get_extension_box_response(db, box2)

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
        "sales_winner": get_winner(m1.get("boxes_sold_per_day") or m1.get("sales_per_day"), m2.get("boxes_sold_per_day") or m2.get("sales_per_day")),
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
async def get_top_movers(
    current_user=Depends(optional_extension_user),
):
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
