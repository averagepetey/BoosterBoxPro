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
        
        Args:
            raw_data: Raw response from Apify
            box_id: UUID of the booster box
            target_date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Historical entry dict in our format
        """
        if not raw_data:
            return None
        
        target_date = target_date or datetime.now().strftime('%Y-%m-%d')
        
        # Extract top-level metrics
        avg_daily_sold = float(raw_data.get('averageDailyQuantitySold', 0) or 0)
        total_sold = int(raw_data.get('totalQuantitySold', 0) or 0)
        total_transactions = int(raw_data.get('totalTransactionCount', 0) or 0)
        
        # Get buckets for detailed data
        buckets = raw_data.get('buckets', [])
        
        # Find the bucket for target date (or most recent)
        target_bucket = None
        latest_bucket = None
        
        for bucket in buckets:
            bucket_date = bucket.get('bucketStartDate', '')
            if bucket_date == target_date:
                target_bucket = bucket
                break
            if not latest_bucket or bucket_date > latest_bucket.get('bucketStartDate', ''):
                latest_bucket = bucket
        
        # Use target bucket or fall back to latest
        bucket = target_bucket or latest_bucket
        
        if bucket:
            market_price = float(bucket.get('marketPrice', 0) or 0)
            quantity_sold = int(bucket.get('quantitySold', 0) or 0)
            low_sale_price = float(bucket.get('lowSalePrice', 0) or 0)
            high_sale_price = float(bucket.get('highSalePrice', 0) or 0)
            transaction_count = int(bucket.get('transactionCount', 0) or 0)
            
            # Calculate daily volume
            daily_volume = market_price * quantity_sold
            
            # Use low sale price as floor price approximation
            floor_price = low_sale_price if low_sale_price > 0 else market_price
        else:
            # No bucket data, use top-level metrics
            market_price = 0
            quantity_sold = 0
            floor_price = 0
            daily_volume = 0
            transaction_count = 0
        
        # Build historical entry
        entry = {
            'date': target_date,
            'box_id': box_id,
            'floor_price_usd': floor_price,
            'boxes_sold_per_day': avg_daily_sold if avg_daily_sold > 0 else quantity_sold,
            'boxes_sold_today': quantity_sold,
            'daily_volume_usd': daily_volume,
            'unified_volume_usd': daily_volume * 30,  # 30-day projection
            'active_listings_count': None,  # Not available from this API
            'boxes_added_today': None,  # Not available, calculated separately
            'source': 'apify_tcgplayer',
            'raw_apify_data': {
                'avg_daily_sold': avg_daily_sold,
                'total_sold': total_sold,
                'total_transactions': total_transactions,
                'bucket_date': bucket.get('bucketStartDate') if bucket else None,
                'market_price': market_price,
                'low_sale_price': bucket.get('lowSalePrice') if bucket else None,
                'high_sale_price': bucket.get('highSalePrice') if bucket else None,
            }
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
    
    # Sort buckets by date
    sorted_buckets = sorted(buckets, key=lambda x: x.get('bucketStartDate', ''), reverse=True)
    
    # Get cutoff date (30 days ago)
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    total_volume = 0.0
    for bucket in sorted_buckets:
        bucket_date = bucket.get('bucketStartDate', '')
        if bucket_date < cutoff_date:
            break
        
        market_price = float(bucket.get('marketPrice', 0) or 0)
        quantity_sold = int(bucket.get('quantitySold', 0) or 0)
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
    
    avg_sales = sum(e.get("boxes_sold_per_day", 0) or 0 for e in recent_entries) / len(recent_entries)
    return avg_sales


def calculate_estimated_daily_sales(prev_avg: float, current_avg: float, window: int = 30) -> float:
    """
    Back-calculate estimated actual daily sales from rolling average change.
    
    Formula: new_avg = (old_avg × (window-1) + today_sales) / window
    Solving for today_sales: today_sales = (new_avg × window) - (old_avg × (window-1))
    """
    if prev_avg is None or current_avg is None:
        return current_avg or 0
    
    estimated = (current_avg * window) - (prev_avg * (window - 1))
    return max(0, round(estimated, 1))  # Can't have negative sales


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
    Pull fresh sales data from TCGplayer for all boxes and save to historical_entries.json.
    
    Enhanced with:
    - Day-over-day comparison
    - Estimated actual daily sales (back-calculated from rolling avg)
    - Spike detection (>50% above 7-day baseline)
    
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
    
    # Load existing historical data
    data_dir = Path(__file__).parent.parent.parent / "data"
    historical_file = data_dir / "historical_entries.json"
    
    historical = {}
    if historical_file.exists():
        with open(historical_file) as f:
            historical = json.load(f)
    
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
            
            # Extract metrics from API
            avg_daily = float(data.get("averageDailyQuantitySold") or 0)
            buckets = data.get("buckets") or []
            
            if buckets:
                market_price = float(buckets[0].get("marketPrice") or 0)
                low_sale = float(buckets[0].get("lowSalePrice") or 0)
                # Use market_price as floor proxy (more accurate than lowSalePrice)
                # lowSalePrice is the lowest sale in the bucket (often old/outlier)
                # marketPrice is the average sale price (closer to current floor)
                floor = market_price if market_price > 0 else low_sale
            else:
                market_price = 0
                floor = 0
            
            # Get previous entry for comparison
            prev_entry = get_previous_entry(historical, box_id, today)
            prev_avg = prev_entry.get("boxes_sold_per_day") if prev_entry else None
            prev_price = prev_entry.get("market_price_usd") if prev_entry else None
            
            # Calculate estimated actual daily sales from rolling avg change
            estimated_today_sales = calculate_estimated_daily_sales(prev_avg, avg_daily)
            
            # Get 7-day baseline for spike detection
            baseline_7d = get_7day_baseline(historical, box_id, today)
            
            # Check for volume spike
            spike = detect_spike(estimated_today_sales, baseline_7d) if baseline_7d else None
            if spike:
                spike["box"] = name
                spike["box_id"] = box_id
                alerts.append(spike)
                logger.warning(f"🔥 {name}: {spike['type']} - {spike['change_pct']:+.1f}% vs baseline")
            
            # Calculate day-over-day changes
            avg_change = round(avg_daily - prev_avg, 2) if prev_avg else None
            avg_change_pct = round(((avg_daily - prev_avg) / prev_avg) * 100, 1) if prev_avg and prev_avg > 0 else None
            price_change = round(market_price - prev_price, 2) if prev_price else None
            price_change_pct = round(((market_price - prev_price) / prev_price) * 100, 1) if prev_price and prev_price > 0 else None
            
            daily_vol = round(avg_daily * market_price, 2)
            volume_7d = round(daily_vol * 7, 2)
            volume_30d = round(daily_vol * 30, 2)
            
            # Create enriched entry
            new_entry = {
                "date": today,
                "source": "apify_tcgplayer",
                # Raw API data
                "boxes_sold_per_day": avg_daily,  # TCGplayer's rolling average
                "floor_price_usd": floor,
                "market_price_usd": market_price,
                "daily_volume_usd": daily_vol,
                # Calculated rolling volumes (extrapolated from daily average)
                "volume_7d": volume_7d,
                "unified_volume_usd": volume_30d,
                # Derived metrics (our calculations)
                "estimated_actual_sales_today": estimated_today_sales,
                "baseline_7d_avg": round(baseline_7d, 2) if baseline_7d else None,
                # Day-over-day changes
                "avg_change_from_yesterday": avg_change,
                "avg_change_pct": avg_change_pct,
                "price_change_from_yesterday": price_change,
                "price_change_pct": price_change_pct,
                # Spike detection
                "spike_detected": spike["type"] if spike else None,
                "spike_magnitude_pct": spike["change_pct"] if spike else None,
                # Metadata
                "timestamp": datetime.now().isoformat(),
            }
            
            # Add to historical data
            if box_id not in historical:
                historical[box_id] = []
            
            # Remove existing entry for today (update mode)
            historical[box_id] = [e for e in historical[box_id] if e.get("date") != today]
            historical[box_id].append(new_entry)

            # Write to DB so live site updates without commits.
            # Use leaderboard UUID (same as booster_boxes.id and listings scraper) so FK passes
            # and the same row gets both Apify sales and scraper listings for today.
            try:
                from app.services.box_metrics_writer import upsert_daily_metrics
                from app.services.historical_data import DB_TO_LEADERBOARD_UUID_MAP
                booster_box_id_for_db = DB_TO_LEADERBOARD_UUID_MAP.get(box_id, box_id)
                upsert_daily_metrics(
                    booster_box_id=booster_box_id_for_db,
                    metric_date=today,
                    floor_price_usd=floor,
                    boxes_sold_per_day=avg_daily,
                    unified_volume_usd=volume_30d,
                    boxes_sold_30d_avg=avg_daily,
                )
            except Exception as e:
                logger.warning(f"DB upsert skipped for {name}: {e}")
            
            # Log with day-over-day context
            change_str = f" ({avg_change_pct:+.1f}%)" if avg_change_pct else ""
            logger.info(f"✅ {name}: {avg_daily}/day{change_str} @ ${market_price:.2f}")
            
            results.append({
                "name": name, 
                "box_id": box_id,
                "sold": avg_daily, 
                "estimated_today": estimated_today_sales,
                "price": market_price, 
                "vol": daily_vol,
                "change_pct": avg_change_pct
            })
            success_count += 1
            
        except Exception as e:
            logger.error(f"Error fetching {name}: {str(e)}")
            error_count += 1
    
    # Save updated data to JSON (legacy/backup - optional, don't fail if directory doesn't exist)
    # Primary storage is now database (box_metrics_unified) via upsert_daily_metrics above
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(historical_file, "w") as f:
            json.dump(historical, f, indent=2)
        logger.debug(f"Saved historical data to {historical_file} (backup)")
    except Exception as e:
        logger.warning(f"Could not save to JSON backup (non-fatal): {e}")
    
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
                "sales_per_day": r["sold"],
                "estimated_today": r["estimated_today"],
                "price": r["price"],
                "change_pct": r.get("change_pct")
            }
            for r in top_5
        ],
        "top_gainers": [
            {"name": r["name"], "change_pct": r["change_pct"], "sales_per_day": r["sold"]}
            for r in top_gainers if r["change_pct"] and r["change_pct"] > 0
        ],
        "top_losers": [
            {"name": r["name"], "change_pct": r["change_pct"], "sales_per_day": r["sold"]}
            for r in top_losers if r["change_pct"] and r["change_pct"] < 0
        ],
        "alerts": alerts,
        "alert_count": len(alerts)
    }
