#!/usr/bin/env python3
"""
TCGplayer data pull - fixed version
"""
import json
import os
from datetime import datetime
from pathlib import Path
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# Box configs: (box_id, name, url)
BOX_CONFIGS = [
    ("860ffe3f-9286-42a9-ad4e-d079a6add6f4", "OP-01 Blue", "https://www.tcgplayer.com/product/450086/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-1-blue?Language=English"),
    ("18ade4d4-512b-4261-a119-2b6cfaf1fa2a", "OP-01 White", "https://www.tcgplayer.com/product/557280/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-2-white?Language=English"),
    ("f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320", "OP-02", "https://www.tcgplayer.com/product/455866/one-piece-card-game-paramount-war-paramount-war-booster-box?Language=English"),
    ("d3929fc6-6afa-468a-b7a1-ccc0f392131a", "OP-03", "https://www.tcgplayer.com/product/477176/one-piece-card-game-pillars-of-strength-pillars-of-strength-booster-box?Language=English"),
    ("526c28b7-bc13-449b-a521-e63bdd81811a", "OP-04", "https://www.tcgplayer.com/product/485833/one-piece-card-game-kingdoms-of-intrigue-kingdoms-of-intrigue-booster-box?Language=English"),
    ("6ea1659d-7b86-46c5-8fb2-0596262b8e68", "OP-05", "https://www.tcgplayer.com/product/498734/one-piece-card-game-awakening-of-the-new-era-awakening-of-the-new-era-booster-box?Language=English"),
    ("b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa", "OP-06", "https://www.tcgplayer.com/product/515080/one-piece-card-game-wings-of-the-captain-wings-of-the-captain-booster-box?Language=English"),
    ("9bfebc47-4a92-44b3-b157-8c53d6a6a064", "OP-07", "https://www.tcgplayer.com/product/532106/one-piece-card-game-500-years-in-the-future-500-years-in-the-future-booster-box?Language=English"),
    ("d0faf871-a930-4c80-a981-9df8741c90a9", "OP-08", "https://www.tcgplayer.com/product/542504/one-piece-card-game-two-legends-two-legends-booster-box?Language=English"),
    ("62e94d8d-bde1-4aec-a4f4-98c28d5e98c6", "OP-09", "https://www.tcgplayer.com/product/563834/one-piece-card-game-emperors-in-the-new-world-emperors-in-the-new-world-booster-box?Language=English"),
    ("3429708c-43c3-4ed8-8be3-706db8b062bd", "OP-10", "https://www.tcgplayer.com/product/586671/one-piece-card-game-royal-blood-royal-blood-booster-box?Language=English"),
    ("46039dfc-a980-4bbd-aada-8cc1e124b44b", "OP-11", "https://www.tcgplayer.com/product/620180/one-piece-card-game-a-fist-of-divine-speed-a-fist-of-divine-speed-booster-box?Language=English"),
    ("be5fccb2-a76b-45a4-aff9-46a57fd41d38", "OP-12", "https://www.tcgplayer.com/product/628346/one-piece-card-game-legacy-of-the-master-legacy-of-the-master-booster-box?Language=English"),
    ("0f52ffcc-1e2f-4b4c-9b38-a16d59d0c7a7", "OP-13", "https://www.tcgplayer.com/product/628352/one-piece-card-game-carrying-on-his-will-carrying-on-his-will-booster-box?Language=English"),
    ("3b17b708-b35b-4008-971e-240ade7afc9c", "EB-01", "https://www.tcgplayer.com/product/521161/one-piece-card-game-extra-booster-memorial-collection-memorial-collection-booster-box?Language=English"),
    ("7509a855-f6da-445e-b445-130824d81d04", "EB-02", "https://www.tcgplayer.com/product/594069/one-piece-card-game-extra-booster-anime-25th-collection-extra-booster-anime-25th-collection-box?Language=English"),
    ("743bf253-98ca-49d5-93fe-a3eaef9f72c1", "PRB-01", "https://www.tcgplayer.com/product/545399/one-piece-card-game-premium-booster-the-best-premium-booster-booster-box?Language=English"),
    ("3bda2acb-a55c-4a6e-ae93-dff5bad27e62", "PRB-02", "https://www.tcgplayer.com/product/628452/one-piece-card-game-premium-booster-the-best-vol-2-premium-booster-vol-2-booster-box?Language=English"),
]

DATA_DIR = Path(__file__).parent.parent / "data"
HISTORICAL_FILE = DATA_DIR / "historical_entries.json"


def main():
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("❌ APIFY_API_TOKEN not set!")
        return
    
    client = ApifyClient(api_token)
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n{'='*60}")
    print(f"🚀 PULLING TCGPLAYER DATA")
    print(f"📅 Date: {today}")
    print(f"{'='*60}\n")
    
    # Load existing data (preserve existing structure)
    historical = {}
    if HISTORICAL_FILE.exists():
        with open(HISTORICAL_FILE) as f:
            historical = json.load(f)
    
    results = []
    
    for i, (box_id, name, url) in enumerate(BOX_CONFIGS, 1):
        print(f"[{i}/18] {name}...", end=" ", flush=True)
        
        try:
            # Call Apify
            run = client.actor("scraped/tcgplayer-sales-history").call(run_input={"url": url})
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not items:
                print("⚠️ No data")
                continue
            
            data = items[0]
            
            # Debug: verify data type
            if not isinstance(data, dict):
                print(f"⚠️ Unexpected data type: {type(data)}")
                continue
            
            # Extract metrics (all values are strings in the API response)
            avg_daily = float(data.get("averageDailyQuantitySold") or 0)
            
            # Get price from latest bucket (top-level marketPrice/trendingMarketPrice aren't reliable)
            buckets = data.get("buckets") or []
            if buckets:
                market_price = float(buckets[0].get("marketPrice") or 0)
                floor = float(buckets[0].get("lowSalePrice") or 0) or market_price
            else:
                market_price = 0
                floor = 0
            
            daily_vol = round(avg_daily * market_price, 2)
            
            # Create new entry for today
            new_entry = {
                "date": today,
                "source": "apify_tcgplayer",
                "boxes_sold_per_day": avg_daily,
                "floor_price_usd": floor,
                "market_price_usd": market_price,
                "daily_volume_usd": daily_vol,
                "unified_volume_usd": daily_vol * 30,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Add to historical data
            if box_id not in historical:
                historical[box_id] = []
            
            # Remove any existing entry for today
            historical[box_id] = [e for e in historical[box_id] if e.get("date") != today]
            historical[box_id].append(new_entry)
            
            print(f"✅ {avg_daily}/day @ ${market_price:.2f}")
            results.append({"name": name, "sold": avg_daily, "price": market_price, "vol": daily_vol})
            
        except Exception as e:
            print(f"❌ {str(e)[:60]}")
            import traceback
            traceback.print_exc()
    
    # Save updated data
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(historical, f, indent=2)
    
    print(f"\n{'='*60}")
    print("📊 TOP 5 BY DAILY VOLUME:")
    for r in sorted(results, key=lambda x: x["vol"], reverse=True)[:5]:
        print(f"   {r['name']}: ${r['vol']:,.0f}/day ({r['sold']:.0f} @ ${r['price']:.0f})")
    print(f"{'='*60}")
    print(f"✅ Saved {len(results)} entries to {HISTORICAL_FILE}")


if __name__ == "__main__":
    main()

