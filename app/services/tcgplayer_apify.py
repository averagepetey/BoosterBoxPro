"""
TCGplayer Apify Service
Fetches sales history data from TCGplayer via Apify actor
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from apify_client import ApifyClient

from app.config import settings

logger = logging.getLogger(__name__)

# TCGplayer Product URLs for all 18 One Piece Booster Boxes
# These need to be filled in with actual URLs
TCGPLAYER_URLS = {
    # Main sets
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {  # OP-01 Blue
        "name": "OP-01 Romance Dawn (Blue)",
        "url": "https://www.tcgplayer.com/product/450086/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-1-blue?Language=English",
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {  # OP-01 White
        "name": "OP-01 Romance Dawn (White)", 
        "url": "https://www.tcgplayer.com/product/557280/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-2-white?Language=English",
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {  # OP-02
        "name": "OP-02 Paramount War",
        "url": "https://www.tcgplayer.com/product/455866/one-piece-card-game-paramount-war-paramount-war-booster-box?Language=English",
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {  # OP-03
        "name": "OP-03 Pillars of Strength",
        "url": "https://www.tcgplayer.com/product/477176/one-piece-card-game-pillars-of-strength-pillars-of-strength-booster-box?Language=English",
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {  # OP-04
        "name": "OP-04 Kingdoms of Intrigue",
        "url": "https://www.tcgplayer.com/product/485833/one-piece-card-game-kingdoms-of-intrigue-kingdoms-of-intrigue-booster-box?Language=English",
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {  # OP-05
        "name": "OP-05 Awakening of the New Era",
        "url": "https://www.tcgplayer.com/product/498734/one-piece-card-game-awakening-of-the-new-era-awakening-of-the-new-era-booster-box?Language=English",
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {  # OP-06
        "name": "OP-06 Wings of the Captain",
        "url": "https://www.tcgplayer.com/product/515080/one-piece-card-game-wings-of-the-captain-wings-of-the-captain-booster-box?Language=English",
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {  # OP-07
        "name": "OP-07 500 Years in the Future",
        "url": "https://www.tcgplayer.com/product/532106/one-piece-card-game-500-years-in-the-future-500-years-in-the-future-booster-box?Language=English",
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {  # OP-08
        "name": "OP-08 Two Legends",
        "url": "https://www.tcgplayer.com/product/542504/one-piece-card-game-two-legends-two-legends-booster-box?Language=English",
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {  # OP-09
        "name": "OP-09 Emperors in the New World",
        "url": "https://www.tcgplayer.com/product/563834/one-piece-card-game-emperors-in-the-new-world-emperors-in-the-new-world-booster-box?Language=English",
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {  # OP-10
        "name": "OP-10 Royal Blood",
        "url": "https://www.tcgplayer.com/product/586671/one-piece-card-game-royal-blood-royal-blood-booster-box?Language=English",
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {  # OP-11
        "name": "OP-11 A Fist of Divine Speed",
        "url": "https://www.tcgplayer.com/product/620180/one-piece-card-game-a-fist-of-divine-speed-a-fist-of-divine-speed-booster-box?Language=English",
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {  # OP-12
        "name": "OP-12 Legacy of the Master",
        "url": "https://www.tcgplayer.com/product/628346/one-piece-card-game-legacy-of-the-master-legacy-of-the-master-booster-box?Language=English",
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {  # OP-13
        "name": "OP-13 Carrying on His Will",
        "url": "https://www.tcgplayer.com/product/628352/one-piece-card-game-carrying-on-his-will-carrying-on-his-will-booster-box?Language=English",
    },
    # Extra Boosters
    "3b17b708-b35b-4008-971e-240ade7afc9c": {  # EB-01
        "name": "EB-01 Memorial Collection",
        "url": "https://www.tcgplayer.com/product/521161/one-piece-card-game-extra-booster-memorial-collection-memorial-collection-booster-box?Language=English",
    },
    "7509a855-f6da-445e-b445-130824d81d04": {  # EB-02
        "name": "EB-02 Anime 25th Collection",
        "url": "https://www.tcgplayer.com/product/594069/one-piece-card-game-extra-booster-anime-25th-collection-extra-booster-anime-25th-collection-box?Language=English",
    },
    # Premium Boosters
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {  # PRB-01
        "name": "PRB-01 Premium Booster",
        "url": "https://www.tcgplayer.com/product/545399/one-piece-card-game-premium-booster-the-best-premium-booster-booster-box?Language=English",
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {  # PRB-02
        "name": "PRB-02 Premium Booster Vol. 2",
        "url": "https://www.tcgplayer.com/product/628452/one-piece-card-game-premium-booster-the-best-vol-2-premium-booster-vol-2-booster-box?Language=English",
    },
}


class TCGplayerApifyService:
    """Service for fetching TCGplayer sales data via Apify"""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the service with Apify API token"""
        self.api_token = api_token or settings.apify_api_token
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN not configured. Set it in .env file.")
        
        self.client = ApifyClient(self.api_token)
        self.actor_id = "scraped/tcgplayer-sales-history"
    
    def fetch_sales_history(self, tcgplayer_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch sales history for a TCGplayer product.
        
        Args:
            tcgplayer_url: Full TCGplayer product URL
            
        Returns:
            Raw API response data or None if failed
        """
        try:
            logger.info(f"Fetching sales history from: {tcgplayer_url}")
            
            # Run the actor
            run = self.client.actor(self.actor_id).call(
                run_input={"url": tcgplayer_url}
            )
            
            # Get results from dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not items:
                logger.warning(f"No data returned for URL: {tcgplayer_url}")
                return None
            
            # Return first item (should be only one)
            return items[0]
            
        except Exception as e:
            logger.error(f"Error fetching sales history: {e}")
            return None
    
    def transform_to_historical_entry(
        self,
        raw_data: Dict[str, Any],
        box_id: str,
        target_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transform Apify response to our historical entry format.

        Sales are computed from weekly bucket data, not averageDailyQuantitySold.
        """
        if not raw_data:
            return None

        target_date = target_date or datetime.now().strftime('%Y-%m-%d')

        buckets = raw_data.get('buckets', [])
        buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

        # Market price from most recent bucket
        if buckets:
            market_price = _safe_float(buckets[0].get('marketPrice'))
            low_sale_price = _safe_float(buckets[0].get('lowSalePrice'))
            floor_price = market_price if market_price > 0 else low_sale_price
        else:
            market_price = 0
            floor_price = 0

        # Compute daily sales from weekly buckets
        _weekly_fallback = compute_daily_sales_from_buckets(buckets, today=target_date) or 0
        boxes_sold_today = compute_this_week_daily_rate(buckets, today=target_date) or _weekly_fallback
        daily_volume = round(boxes_sold_today * market_price, 2) if market_price else 0

        # Track current incomplete bucket for delta computation on next run
        incomplete_bucket = get_current_incomplete_bucket(buckets, target_date)
        current_bucket_start = incomplete_bucket.get("bucketStartDate", "")[:10] if incomplete_bucket else None
        current_bucket_qty = _safe_int(incomplete_bucket.get("quantitySold")) if incomplete_bucket else None

        entry = {
            'date': target_date,
            'box_id': box_id,
            'floor_price_usd': floor_price,
            'market_price_usd': market_price,
            'boxes_sold_today': boxes_sold_today,
            'daily_volume_usd': daily_volume,
            'active_listings_count': None,
            'boxes_added_today': None,
            'source': 'apify_tcgplayer',
            'total_quantity_sold': _safe_int(raw_data.get('totalQuantitySold')),
            'apify_lifetime_avg': _safe_float(raw_data.get('averageDailyQuantitySold')),
            'current_bucket_start': current_bucket_start,
            'current_bucket_qty': current_bucket_qty,
        }

        return entry
    
    def fetch_box_sales(self, box_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch sales data for a specific box by ID.
        
        Args:
            box_id: UUID of the booster box
            
        Returns:
            Transformed historical entry or None
        """
        if box_id not in TCGPLAYER_URLS:
            logger.error(f"Unknown box_id: {box_id}")
            return None
        
        box_config = TCGPLAYER_URLS[box_id]
        url = box_config.get('url')
        
        if not url:
            logger.warning(f"No TCGplayer URL configured for {box_config['name']}")
            return None
        
        raw_data = self.fetch_sales_history(url)
        if not raw_data:
            return None
        
        return self.transform_to_historical_entry(raw_data, box_id)
    
    def fetch_all_boxes(self) -> List[Dict[str, Any]]:
        """
        Fetch sales data for all configured boxes.
        
        Returns:
            List of historical entries for all boxes with URLs
        """
        results = []
        
        for box_id, config in TCGPLAYER_URLS.items():
            if not config.get('url'):
                logger.info(f"Skipping {config['name']} - no URL configured")
                continue
            
            logger.info(f"Fetching data for {config['name']}...")
            entry = self.fetch_box_sales(box_id)
            
            if entry:
                results.append(entry)
                logger.info(f"✅ Got data for {config['name']}")
            else:
                logger.warning(f"❌ Failed to get data for {config['name']}")
        
        return results


def _safe_int(val) -> int:
    """Safely convert a value to int (handles str/None)."""
    try:
        return int(val) if val else 0
    except (ValueError, TypeError):
        return 0


def _safe_float(val) -> float:
    """Safely convert a value to float (handles str/None)."""
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def get_complete_weekly_buckets(buckets: List[Dict], today: Optional[str] = None) -> List[Dict]:
    """
    Return weekly buckets sorted newest-first, excluding today's incomplete bucket.

    Apify returns weekly buckets (7-day intervals). The most recent bucket
    (matching today's date) is always incomplete/partial, so we skip it.
    """
    if not buckets:
        return []

    today = today or datetime.now().strftime("%Y-%m-%d")
    sorted_buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

    # Skip the current (incomplete) week bucket
    return [b for b in sorted_buckets if b.get("bucketStartDate", "") < today]


def compute_daily_sales_from_buckets(
    buckets: List[Dict],
    weeks: Optional[int] = None,
    today: Optional[str] = None,
) -> Optional[float]:
    """
    Compute average daily sales from complete weekly buckets.

    Each bucket's quantitySold is the total units sold in that 7-day period.

    By default (weeks=None), uses ALL complete buckets that have non-zero sales
    to compute the average over the product's active selling period. This avoids
    understating sales for products with declining trends, and avoids inflating
    with pre-launch zero-sale weeks.

    If weeks is specified, uses only the last N complete weeks.

    Args:
        buckets: Raw bucket list from Apify
        weeks: Number of complete weeks to average over, or None for all active
        today: Date string to determine "current" incomplete bucket

    Returns:
        Average daily sales rate, or None if no complete buckets
    """
    complete = get_complete_weekly_buckets(buckets, today)
    if not complete:
        return None

    if weeks is not None:
        # Fixed window: last N weeks
        recent = complete[:weeks]
    else:
        # All active weeks: find the oldest bucket with non-zero sales and
        # include everything from that point forward (including any zero weeks
        # in between, since those are real lull periods, not pre-launch)
        first_sale_idx = None
        for i in range(len(complete) - 1, -1, -1):
            if _safe_int(complete[i].get("quantitySold", 0)) > 0:
                first_sale_idx = i
                break
        if first_sale_idx is None:
            return None
        recent = complete[: first_sale_idx + 1]

    total_qty = sum(_safe_int(b.get("quantitySold", 0)) for b in recent)
    days = len(recent) * 7

    return round(total_qty / days, 2) if days > 0 else None


def compute_this_week_daily_rate(
    buckets: List[Dict],
    today: Optional[str] = None,
) -> Optional[float]:
    """
    Get the daily sales rate from the most recent complete weekly bucket.

    Returns:
        Daily sales rate for the most recent complete week, or None
    """
    complete = get_complete_weekly_buckets(buckets, today)
    if not complete:
        return None

    qty = _safe_int(complete[0].get("quantitySold", 0))
    return round(qty / 7, 2)


def get_current_incomplete_bucket(
    buckets: List[Dict],
    today: Optional[str] = None,
) -> Optional[Dict]:
    """
    Find the current week's incomplete bucket (the one whose 7-day window contains today).

    A bucket covers [bucketStartDate, bucketStartDate + 7 days).
    Returns the bucket dict or None if no match.
    """
    if not buckets:
        return None

    today_str = today or datetime.now().strftime("%Y-%m-%d")
    today_dt = datetime.strptime(today_str, "%Y-%m-%d")

    sorted_buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

    for b in sorted_buckets:
        start_str = b.get("bucketStartDate", "")
        if not start_str:
            continue
        start_dt = datetime.strptime(start_str[:10], "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=7)
        if start_dt <= today_dt < end_dt:
            return b

    return None


def compute_delta_sold_today(
    current_bucket_qty: int,
    current_bucket_start: str,
    prev_entry: Optional[Dict],
) -> tuple:
    """
    Compute daily sales delta from incomplete bucket tracking.

    Compares today's incomplete bucket qty against the value stored in the previous entry.

    Returns:
        (delta, source) where source is one of:
        - "same_week": normal delta within the same bucket week
        - "rollover_partial": new bucket week started, using new bucket qty as partial estimate
        - "no_data": no previous data available (caller should fall back to weekly rate)
    """
    if prev_entry is None:
        return (None, "no_data")

    prev_bucket_start = prev_entry.get("current_bucket_start")
    prev_bucket_qty = prev_entry.get("current_bucket_qty")

    if prev_bucket_start is None or prev_bucket_qty is None:
        return (None, "no_data")

    if prev_bucket_start == current_bucket_start:
        # Same week: delta = today_qty - yesterday_qty, clamped to 0
        delta = max(0, current_bucket_qty - prev_bucket_qty)
        return (delta, "same_week")
    else:
        # Rollover: new bucket week started, use new bucket qty as partial estimate
        delta = max(0, current_bucket_qty)
        return (delta, "rollover_partial")


def calculate_30d_volume_from_buckets(buckets: List[Dict]) -> float:
    """
    Calculate actual 30-day volume by summing bucket data.

    Args:
        buckets: List of bucket dictionaries from Apify

    Returns:
        Total volume over ~30 days
    """
    if not buckets:
        return 0.0

    sorted_buckets = sorted(buckets, key=lambda x: x.get('bucketStartDate', ''), reverse=True)
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    total_volume = 0.0
    for bucket in sorted_buckets:
        bucket_date = bucket.get('bucketStartDate', '')
        if bucket_date < cutoff_date:
            break

        market_price = _safe_float(bucket.get('marketPrice', 0))
        quantity_sold = _safe_int(bucket.get('quantitySold', 0))
        total_volume += market_price * quantity_sold

    return total_volume


def set_box_url(box_id: str, url: str) -> bool:
    """
    Set the TCGplayer URL for a box.
    
    Args:
        box_id: UUID of the box
        url: TCGplayer product URL
        
    Returns:
        True if successful
    """
    if box_id not in TCGPLAYER_URLS:
        return False
    
    TCGPLAYER_URLS[box_id]['url'] = url
    return True


def get_configured_boxes() -> List[Dict[str, Any]]:
    """Get list of boxes with their configuration status"""
    return [
        {
            'box_id': box_id,
            'name': config['name'],
            'url_configured': config['url'] is not None,
            'url': config['url']
        }
        for box_id, config in TCGPLAYER_URLS.items()
    ]


def get_previous_entry(historical: Dict, box_id: str, current_date: str) -> Optional[Dict]:
    """Get the most recent entry before current_date for a box."""
    if box_id not in historical:
        return None
    
    entries = sorted(
        [e for e in historical[box_id] if e.get("date", "") < current_date],
        key=lambda x: x.get("date", ""),
        reverse=True
    )
    return entries[0] if entries else None


def get_7day_baseline(historical: Dict, box_id: str, current_date: str) -> Optional[float]:
    """Calculate 7-day average sales baseline for spike detection."""
    if box_id not in historical:
        return None
    
    cutoff = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
    recent_entries = [
        e for e in historical[box_id] 
        if cutoff <= e.get("date", "") < current_date
    ]
    
    if not recent_entries:
        return None
    
    avg_sales = sum(e.get("boxes_sold_today", 0) or 0 for e in recent_entries) / len(recent_entries)
    return avg_sales



def detect_spike(current_value: float, baseline: float, threshold_pct: float = 50) -> Optional[Dict]:
    """
    Detect if current value is significantly above baseline.
    
    Returns spike info if detected, None otherwise.
    """
    if not baseline or baseline <= 0:
        return None
    
    change_pct = ((current_value - baseline) / baseline) * 100
    
    if change_pct >= threshold_pct:
        return {
            "type": "VOLUME_SPIKE",
            "change_pct": round(change_pct, 1),
            "baseline": round(baseline, 1),
            "current": round(current_value, 1)
        }
    elif change_pct <= -threshold_pct:
        return {
            "type": "VOLUME_DROP",
            "change_pct": round(change_pct, 1),
            "baseline": round(baseline, 1),
            "current": round(current_value, 1)
        }
    
    return None


def refresh_all_boxes_sales_data() -> Dict[str, Any]:
    """
    Pull fresh sales data from TCGplayer for all boxes and save to DB.

    Sales computation uses actual weekly bucket data from Apify:
    - boxes_sold_today: daily rate from the most recent complete weekly bucket (or delta from incomplete bucket)

    The old approach of using averageDailyQuantitySold (a lifetime avg) is removed.

    Returns:
        Dict with success_count, error_count, date, top_5 results, and alerts
    """
    import json
    from pathlib import Path
    from apify_client import ApifyClient

    api_token = settings.apify_api_token
    if not api_token:
        raise ValueError("APIFY_API_TOKEN not configured")

    client = ApifyClient(api_token)
    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing historical data from DB (source of truth)
    historical = {}
    try:
        from app.services.db_historical_reader import _get_sync_engine
        from sqlalchemy import text as _text
        _engine = _get_sync_engine()
        with _engine.connect() as conn:
            cutoff_30d = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            rows = conn.execute(_text("""
                SELECT booster_box_id, metric_date, floor_price_usd, boxes_sold_per_day,
                       current_bucket_start, current_bucket_qty
                FROM box_metrics_unified
                WHERE metric_date >= :cutoff
                ORDER BY booster_box_id, metric_date ASC
            """), {"cutoff": cutoff_30d}).fetchall()
        for r in rows:
            d = r._mapping if hasattr(r, "_mapping") else dict(r)
            bid = str(d["booster_box_id"])
            date_str = d["metric_date"].isoformat() if hasattr(d["metric_date"], "isoformat") else str(d["metric_date"])
            entry = {
                "date": date_str,
                "floor_price_usd": float(d["floor_price_usd"]) if d.get("floor_price_usd") is not None else None,
                "boxes_sold_today": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else None,
                "current_bucket_start": d.get("current_bucket_start"),
                "current_bucket_qty": int(d["current_bucket_qty"]) if d.get("current_bucket_qty") is not None else None,
            }
            historical.setdefault(bid, []).append(entry)
        logger.info(f"Loaded {len(historical)} boxes with history from DB")
    except Exception as e:
        logger.warning(f"Could not load historical data from DB: {e}")

    results = []
    alerts = []
    success_count = 0
    error_count = 0

    for box_id, config in TCGPLAYER_URLS.items():
        url = config.get("url")
        name = config.get("name", box_id)

        if not url:
            logger.info(f"Skipping {name} - no URL configured")
            continue

        logger.info(f"Fetching {name}...")

        try:
            # Call Apify
            run = client.actor("scraped/tcgplayer-sales-history").call(run_input={"url": url})
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            if not items:
                logger.warning(f"No data returned for {name}")
                error_count += 1
                continue

            data = items[0]
            if not isinstance(data, dict):
                logger.warning(f"Unexpected data type for {name}: {type(data)}")
                error_count += 1
                continue

            # Extract top-level metrics (for reference only)
            apify_lifetime_avg = _safe_float(data.get("averageDailyQuantitySold"))
            total_quantity_sold = _safe_int(data.get("totalQuantitySold"))
            total_transaction_count = _safe_int(data.get("totalTransactionCount"))

            buckets = data.get("buckets") or []

            # Sort buckets newest-first
            buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

            # Get market price from the most recent bucket (even if incomplete)
            if buckets:
                market_price = _safe_float(buckets[0].get("marketPrice"))
                low_sale = _safe_float(buckets[0].get("lowSalePrice"))
                floor = market_price if market_price > 0 else low_sale
                bucket_date = buckets[0].get("bucketStartDate", "")
            else:
                market_price = 0
                floor = 0
                bucket_date = ""

            # ── Compute daily sales from weekly bucket data ──
            _weekly_fallback = compute_daily_sales_from_buckets(buckets, today=today) or 0
            # boxes_sold_today: most recent complete week's daily rate
            boxes_sold_today = compute_this_week_daily_rate(buckets, today=today) or _weekly_fallback

            # Store complete bucket data for the most recent complete week (reference)
            complete_buckets = get_complete_weekly_buckets(buckets, today)
            recent_bucket_qty = _safe_int(complete_buckets[0].get("quantitySold")) if complete_buckets else 0

            # ── Delta tracking from incomplete bucket ──
            incomplete_bucket = get_current_incomplete_bucket(buckets, today)
            current_bucket_start = incomplete_bucket.get("bucketStartDate", "")[:10] if incomplete_bucket else None
            current_bucket_qty = _safe_int(incomplete_bucket.get("quantitySold")) if incomplete_bucket else None

            # Get previous entry for comparison
            prev_entry = get_previous_entry(historical, box_id, today)

            # Compute delta sold today from incomplete bucket tracking
            delta_boxes_sold_today = None
            delta_source = None
            if current_bucket_qty is not None and current_bucket_start:
                delta_boxes_sold_today, delta_source = compute_delta_sold_today(
                    current_bucket_qty, current_bucket_start, prev_entry
                )
                if delta_boxes_sold_today is not None:
                    boxes_sold_today = delta_boxes_sold_today
                    logger.info(f"  Delta tracking: {delta_boxes_sold_today} sold today ({delta_source})")

            prev_sold_per_day = prev_entry.get("boxes_sold_today") if prev_entry else None
            prev_price = prev_entry.get("market_price_usd") if prev_entry else None

            # Get 7-day baseline for spike detection
            baseline_7d = get_7day_baseline(historical, box_id, today)

            # Check for volume spike
            spike = detect_spike(boxes_sold_today, baseline_7d) if baseline_7d else None
            if spike:
                spike["box"] = name
                spike["box_id"] = box_id
                alerts.append(spike)
                logger.warning(f"🔥 {name}: {spike['type']} - {spike['change_pct']:+.1f}% vs baseline")

            # Day-over-day changes
            avg_change = round(boxes_sold_today - prev_sold_per_day, 2) if prev_sold_per_day is not None else None
            avg_change_pct = round(((boxes_sold_today - prev_sold_per_day) / prev_sold_per_day) * 100, 1) if prev_sold_per_day and prev_sold_per_day > 0 else None
            price_change = round(market_price - prev_price, 2) if prev_price else None
            price_change_pct = round(((market_price - prev_price) / prev_price) * 100, 1) if prev_price and prev_price > 0 else None

            # Daily volume = daily sales rate × market price
            daily_vol = round(boxes_sold_today * market_price, 2) if market_price and boxes_sold_today else 0

            # 30-day volume from buckets (actual weekly totals × market prices)
            volume_30d = calculate_30d_volume_from_buckets(buckets)

            # Create enriched entry
            new_entry = {
                "date": today,
                "source": "apify_tcgplayer",
                # Sales metrics (computed from weekly bucket data)
                "boxes_sold_today": boxes_sold_today,  # Delta from incomplete bucket, or weekly rate fallback
                "bucket_quantity_sold": recent_bucket_qty,  # Raw qty from most recent complete week
                # Incomplete bucket delta tracking
                "current_bucket_start": current_bucket_start,
                "current_bucket_qty": current_bucket_qty,
                "delta_boxes_sold_today": delta_boxes_sold_today,
                "delta_source": delta_source,
                "floor_price_usd": floor,
                "market_price_usd": market_price,
                "daily_volume_usd": daily_vol,
                "bucket_date": bucket_date,
                # Reference fields from API (not used for computations)
                "apify_lifetime_avg": apify_lifetime_avg,
                "total_quantity_sold": total_quantity_sold,
                "total_transaction_count": total_transaction_count,
                # Day-over-day changes
                "avg_change_from_yesterday": avg_change,
                "avg_change_pct": avg_change_pct,
                "price_change_from_yesterday": price_change,
                "price_change_pct": price_change_pct,
                # Spike detection
                "spike_detected": spike["type"] if spike else None,
                "spike_magnitude_pct": spike["change_pct"] if spike else None,
                "baseline_7d_avg": round(baseline_7d, 2) if baseline_7d else None,
                # Metadata
                "timestamp": datetime.now().isoformat(),
            }

            # Add to historical data
            if box_id not in historical:
                historical[box_id] = []

            # Remove existing entry for today (update mode)
            historical[box_id] = [e for e in historical[box_id] if e.get("date") != today]
            historical[box_id].append(new_entry)

            # Running 30d avg from last 30 days of daily sold
            entries_30d = sorted(historical[box_id], key=lambda e: e.get("date", ""))
            cutoff_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            recent_30 = [e for e in entries_30d if (e.get("date") or "") >= cutoff_30]
            boxes_sold_30d_avg = None
            if recent_30:
                vals = [_safe_float(e.get("boxes_sold_today") or 0) for e in recent_30]
                boxes_sold_30d_avg = round(sum(vals) / len(vals), 2) if vals else None

            # Write to DB: use daily delta (actual sales today) not weekly average
            try:
                from app.services.box_metrics_writer import upsert_daily_metrics
                upsert_daily_metrics(
                    booster_box_id=box_id,
                    metric_date=today,
                    floor_price_usd=floor,
                    boxes_sold_today=boxes_sold_today,
                    unified_volume_usd=volume_30d,
                    boxes_sold_30d_avg=boxes_sold_30d_avg,
                    current_bucket_start=current_bucket_start,
                    current_bucket_qty=current_bucket_qty,
                )
            except Exception as e:
                logger.warning(f"DB upsert skipped for {name}: {e}")

            # Log with context
            change_str = f" ({avg_change_pct:+.1f}%)" if avg_change_pct else ""
            logger.info(f"✅ {name}: {boxes_sold_today}/day (this week){change_str} @ ${market_price:.2f}")

            results.append({
                "name": name,
                "box_id": box_id,
                "sold_today": boxes_sold_today,
                "price": market_price,
                "vol": daily_vol,
                "change_pct": avg_change_pct,
            })
            success_count += 1

        except Exception as e:
            logger.error(f"Error fetching {name}: {str(e)}")
            error_count += 1

    # DB is source of truth — skip JSON write

    # Get top 5 by volume
    top_5 = sorted(results, key=lambda x: x["vol"], reverse=True)[:5]

    # Get biggest movers (by change %)
    movers = [r for r in results if r.get("change_pct") is not None]
    top_gainers = sorted(movers, key=lambda x: x["change_pct"], reverse=True)[:3]
    top_losers = sorted(movers, key=lambda x: x["change_pct"])[:3]

    return {
        "success_count": success_count,
        "error_count": error_count,
        "date": today,
        "top_5_by_volume": [
            {
                "name": r["name"],
                "daily_volume": r["vol"],
                "sales_today": r["sold_today"],
                "price": r["price"],
                "change_pct": r.get("change_pct"),
            }
            for r in top_5
        ],
        "top_gainers": [
            {"name": r["name"], "change_pct": r["change_pct"], "sales_today": r["sold_today"]}
            for r in top_gainers if r["change_pct"] and r["change_pct"] > 0
        ],
        "top_losers": [
            {"name": r["name"], "change_pct": r["change_pct"], "sales_today": r["sold_today"]}
            for r in top_losers if r["change_pct"] and r["change_pct"] < 0
        ],
        "alerts": alerts,
        "alert_count": len(alerts),
    }
