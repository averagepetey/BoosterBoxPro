#!/usr/bin/env python3
"""
TCGplayer Listings Scraper
--------------------------
Gentle, stealth scraper for extracting active listings data.
Reference: Setup Guides/LISTINGS_SCRAPER_RULES.md
"""

import asyncio
import json
import random
import logging
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import Stealth

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Target products (18 One Piece booster boxes) - URLs from tcgplayer_apify.py
TCGPLAYER_URLS = {
    # Main Sets OP-01 to OP-13
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": "https://www.tcgplayer.com/product/450086/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-1-blue?Language=English",
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": "https://www.tcgplayer.com/product/557280/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-2-white?Language=English",
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": "https://www.tcgplayer.com/product/455866/one-piece-card-game-paramount-war-paramount-war-booster-box?Language=English",
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": "https://www.tcgplayer.com/product/477176/one-piece-card-game-pillars-of-strength-pillars-of-strength-booster-box?Language=English",
    "526c28b7-bc13-449b-a521-e63bdd81811a": "https://www.tcgplayer.com/product/485833/one-piece-card-game-kingdoms-of-intrigue-kingdoms-of-intrigue-booster-box?Language=English",
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": "https://www.tcgplayer.com/product/498734/one-piece-card-game-awakening-of-the-new-era-awakening-of-the-new-era-booster-box?Language=English",
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": "https://www.tcgplayer.com/product/515080/one-piece-card-game-wings-of-the-captain-wings-of-the-captain-booster-box?Language=English",
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": "https://www.tcgplayer.com/product/532106/one-piece-card-game-500-years-in-the-future-500-years-in-the-future-booster-box?Language=English",
    "d0faf871-a930-4c80-a981-9df8741c90a9": "https://www.tcgplayer.com/product/542504/one-piece-card-game-two-legends-two-legends-booster-box?Language=English",
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": "https://www.tcgplayer.com/product/563834/one-piece-card-game-emperors-in-the-new-world-emperors-in-the-new-world-booster-box?Language=English",
    "3429708c-43c3-4ed8-8be3-706db8b062bd": "https://www.tcgplayer.com/product/586671/one-piece-card-game-royal-blood-royal-blood-booster-box?Language=English",
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": "https://www.tcgplayer.com/product/620180/one-piece-card-game-a-fist-of-divine-speed-a-fist-of-divine-speed-booster-box?Language=English",
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": "https://www.tcgplayer.com/product/628346/one-piece-card-game-legacy-of-the-master-legacy-of-the-master-booster-box?Language=English",
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": "https://www.tcgplayer.com/product/628352/one-piece-card-game-carrying-on-his-will-carrying-on-his-will-booster-box?Language=English",
    # Extra Boosters
    "3b17b708-b35b-4008-971e-240ade7afc9c": "https://www.tcgplayer.com/product/521161/one-piece-card-game-extra-booster-memorial-collection-memorial-collection-booster-box?Language=English",
    "7509a855-f6da-445e-b445-130824d81d04": "https://www.tcgplayer.com/product/594069/one-piece-card-game-extra-booster-anime-25th-collection-extra-booster-anime-25th-collection-box?Language=English",
    # Premium Boosters
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": "https://www.tcgplayer.com/product/545399/one-piece-card-game-premium-booster-the-best-premium-booster-booster-box?Language=English",
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": "https://www.tcgplayer.com/product/628452/one-piece-card-game-premium-booster-the-best-vol-2-premium-booster-vol-2-booster-box?Language=English",
}

# Noise products (random products to mix in)
NOISE_PRODUCTS = [
    "https://www.tcgplayer.com/product/514893/pokemon-scarlet-and-violet-surging-sparks-booster-box",
    "https://www.tcgplayer.com/product/529442/pokemon-scarlet-and-violet-prismatic-evolutions-booster-box",
    "https://www.tcgplayer.com/product/509876/magic-the-gathering-foundations-play-booster-box",
    "https://www.tcgplayer.com/product/519234/yugioh-rage-of-the-abyss-booster-box",
    "https://www.tcgplayer.com/product/489234/pokemon-scarlet-and-violet-151-booster-box",
    "https://www.tcgplayer.com/product/478123/magic-the-gathering-murders-at-karlov-manor-play-booster-box",
    "https://www.tcgplayer.com/product/512345/one-piece-card-game-starter-deck-straw-hat-crew",
    "https://www.tcgplayer.com/product/498765/one-piece-card-game-starter-deck-worst-generation",
    "https://www.tcgplayer.com/product/487654/pokemon-sword-and-shield-crown-zenith-booster-box",
    "https://www.tcgplayer.com/product/476543/magic-the-gathering-bloomburrow-play-booster-box",
    "https://www.tcgplayer.com/product/501234/yugioh-legacy-of-destruction-booster-box",
    "https://www.tcgplayer.com/product/523456/dragon-ball-super-fusion-world-booster-box",
    "https://www.tcgplayer.com/product/534567/one-piece-card-game-double-pack-set-vol-1",
    "https://www.tcgplayer.com/product/545678/pokemon-scarlet-and-violet-obsidian-flames-booster-box",
    "https://www.tcgplayer.com/product/556789/magic-the-gathering-duskmourn-play-booster-box",
]

# Browser profiles (pick one per session)
BROWSER_PROFILES = [
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "MacIntel"
    },
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "MacIntel"
    },
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "viewport": {"width": 1536, "height": 864},
        "platform": "MacIntel"
    },
]

# Filtering configuration
JAPANESE_INDICATORS = [
    'japanese', 'japan', 'jp version', 'jp ver',
    '日本', '日本語', 'japanese language',
    'asian english', 'asia', 'asian'
]

SUSPICIOUS_KEYWORDS = [
    'damaged', 'opened', 'no shrink', 'loose',
    'played', 'heavy play', 'poor condition',
    'missing', 'incomplete', 'resealed',
    'no seal', 'unsealed', 'box only',
    'empty', 'display', 'for display'
]

# Thresholds
OUTLIER_THRESHOLD_PCT = 0.75  # 75% of market price
MIN_CLUSTER_SIZE = 5  # Need 5+ clean low-priced to confirm pullback
WITHIN_20PCT_THRESHOLD = 1.20  # Floor × 1.20

# Timing
DELAY_MIN = 5
DELAY_MAX = 15
DELAY_MEAN = 8

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def human_delay():
    """Generate human-like delay using normal distribution"""
    delay = max(DELAY_MIN, np.random.normal(DELAY_MEAN, 3))
    delay = min(delay, DELAY_MAX)
    logger.debug(f"Waiting {delay:.1f} seconds...")
    return delay


def get_random_profile() -> Dict:
    """Get random browser profile for this session"""
    return random.choice(BROWSER_PROFILES)


def get_daily_products() -> List[tuple]:
    """Get shuffled list of products with noise"""
    # Core 18 targets
    core = list(TCGPLAYER_URLS.items())
    
    # Random noise (2-8 products)
    noise_count = random.randint(2, 8)
    noise_urls = random.sample(NOISE_PRODUCTS, k=min(noise_count, len(NOISE_PRODUCTS)))
    noise = [(f"noise_{i}", url) for i, url in enumerate(noise_urls)]
    
    # Combine and shuffle
    all_products = core + noise
    random.shuffle(all_products)
    
    logger.info(f"Today's run: {len(core)} targets + {noise_count} noise = {len(all_products)} total")
    return all_products


def is_japanese_listing(listing: Dict) -> bool:
    """Check if listing is Japanese version"""
    text = (
        listing.get('title', '') +
        listing.get('description', '') +
        listing.get('condition', '') +
        listing.get('variant', '')
    ).lower()
    return any(indicator in text for indicator in JAPANESE_INDICATORS)


def is_suspicious_listing(listing: Dict) -> bool:
    """Check if listing has suspicious keywords"""
    text = (
        listing.get('title', '') +
        listing.get('description', '') +
        listing.get('condition', '')
    ).lower()
    return any(keyword in text for keyword in SUSPICIOUS_KEYWORDS)


def filter_outlier_prices(listings: List[Dict], market_price: float) -> List[Dict]:
    """
    Smart outlier detection:
    - If 1-4 clean low-priced listings → filter as outliers
    - If 5+ clean low-priced listings → keep as legitimate pullback
    """
    if not market_price or market_price <= 0:
        return listings
    
    min_valid_price = market_price * OUTLIER_THRESHOLD_PCT
    
    low_priced = [l for l in listings if l.get('price', 0) < min_valid_price]
    normal_priced = [l for l in listings if l.get('price', 0) >= min_valid_price]
    
    if len(low_priced) == 0:
        return listings
    
    # Categorize low-priced listings
    suspicious_low = [l for l in low_priced if is_suspicious_listing(l)]
    clean_low = [l for l in low_priced if not is_suspicious_listing(l)]
    
    logger.info(f"  Low-priced listings (<${min_valid_price:.2f}): {len(low_priced)}")
    logger.info(f"    - Suspicious (filtered): {len(suspicious_low)}")
    logger.info(f"    - Clean descriptions: {len(clean_low)}")
    
    if len(clean_low) >= MIN_CLUSTER_SIZE:
        # 5+ clean low-priced = legitimate pullback
        logger.info(f"  ✓ Keeping {len(clean_low)} low-priced (likely real pullback)")
        return normal_priced + clean_low
    else:
        # Only 1-4 clean = probably outliers
        logger.info(f"  ✗ Filtering {len(clean_low)} low-priced (likely outliers)")
        return normal_priced


def process_listings(raw_listings: List[Dict], market_price: float) -> Dict:
    """Full filtering pipeline"""
    logger.info(f"  Raw listings: {len(raw_listings)}")
    
    # Step 1: Remove Japanese listings
    listings = [l for l in raw_listings if not is_japanese_listing(l)]
    jp_removed = len(raw_listings) - len(listings)
    if jp_removed > 0:
        logger.info(f"  After Japanese filter: {len(listings)} ({jp_removed} removed)")
    
    # Step 2: Remove suspicious listings
    clean_listings = [l for l in listings if not is_suspicious_listing(l)]
    suspicious_removed = len(listings) - len(clean_listings)
    if suspicious_removed > 0:
        logger.info(f"  After suspicious filter: {len(clean_listings)} ({suspicious_removed} removed)")
    listings = clean_listings
    
    # Step 3: Smart outlier detection
    listings = filter_outlier_prices(listings, market_price)
    
    if not listings:
        return {
            'total_listings': 0,
            'floor_price': None,
            'listings_within_20pct': 0,
            'filters_applied': {
                'japanese_removed': jp_removed,
                'suspicious_removed': suspicious_removed,
            }
        }
    
    # Step 4: Calculate floor price
    floor_price = min(l['price'] for l in listings)
    
    # Step 5: Count within 20% of floor
    threshold = floor_price * WITHIN_20PCT_THRESHOLD
    within_20pct = [l for l in listings if l['price'] <= threshold]
    
    logger.info(f"  Floor: ${floor_price:.2f}, Within 20% (to ${threshold:.2f}): {len(within_20pct)}")
    
    return {
        'total_listings': len(listings),
        'floor_price': floor_price,
        'listings_within_20pct': len(within_20pct),
        'filters_applied': {
            'japanese_removed': jp_removed,
            'suspicious_removed': suspicious_removed,
        }
    }


# ============================================================================
# SCRAPING FUNCTIONS
# ============================================================================

async def scrape_listings_page(page: Page, min_price: float) -> List[Dict]:
    """Extract listings from current page using JavaScript for reliability"""
    listings = []
    
    try:
        # Wait for listing items to load
        await page.wait_for_selector('.listing-item', timeout=10000)
        
        # Use JavaScript to extract listing data (more reliable than individual queries)
        listings_data = await page.evaluate('''
            () => {
                const listings = [];
                const listingElements = document.querySelectorAll('.listing-item');
                
                listingElements.forEach(el => {
                    try {
                        // Get full text first to check if it's a box
                        const fullText = (el.innerText || '').toLowerCase();
                        
                        // Skip if it's clearly a single pack (look for pack indicators)
                        if (fullText.includes('single pack') || 
                            fullText.includes('1 pack') ||
                            (fullText.includes(' pack') && !fullText.includes('box') && !fullText.includes('booster'))) {
                            return; // Skip this listing
                        }
                        
                        // Skip Japanese listings
                        if (fullText.includes(' japanese ') || 
                            fullText.includes('japanese version') ||
                            fullText.includes('japanese language') ||
                            fullText.includes('(jpn)') ||
                            fullText.includes('(jp)') ||
                            fullText.startsWith('japanese') ||
                            (fullText.includes('jpn') && (fullText.includes('version') || fullText.includes('language')))) {
                            return; // Skip Japanese listings
                        }
                        
                        // Skip suspicious listings (damaged, opened, etc.)
                        // Be careful - "unopened" is good, "opened" is bad
                        if (fullText.includes('damaged') ||
                            fullText.includes('resealed') ||
                            fullText.includes('repack') ||
                            fullText.includes('not sealed') ||
                            fullText.includes('used') ||
                            fullText.includes('played') ||
                            fullText.includes('poor condition') ||
                            (fullText.includes('opened') && !fullText.includes('unopened'))) {
                            return; // Skip suspicious listings
                        }
                        
                        // Find price - try common TCGplayer price locations first
                        let price = 0;
                        const priceSelectors = [
                            '[class*="price"]',
                            '[class*="Price"]',
                            '[data-price]',
                            '[class*="amount"]',
                        ];
                        
                        for (const sel of priceSelectors) {
                            const priceEl = el.querySelector(sel);
                            if (priceEl) {
                                const text = (priceEl.innerText || priceEl.textContent || '').trim();
                                const match = text.match(/\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/);
                                if (match) {
                                    price = parseFloat(match[1].replace(',', ''));
                                    break;
                                }
                            }
                        }
                        
                        // Fallback: search all text in element
                        if (price === 0) {
                            const allText = el.innerText || '';
                            const match = allText.match(/\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/);
                            if (match) {
                                price = parseFloat(match[1].replace(',', ''));
                            }
                        }
                        
                        // Get condition text
                        const conditionEl = el.querySelector('[class*="condition"], [class*="Condition"]');
                        const condition = conditionEl ? conditionEl.innerText.trim() : '';
                        
                        // Get seller info
                        const sellerEl = el.querySelector('[class*="seller"], [class*="Seller"]');
                        const seller = sellerEl ? sellerEl.innerText.trim() : '';
                        
                        // Extract quantity/stock available
                        let quantity = 1; // Default to 1 if not found
                        const quantityText = el.innerText || '';
                        // Look for patterns like "of 12", "12 available", "qty: 12", etc.
                        const quantityPatterns = [
                            /of\s+(\d+)/i,  // "of 12"
                            /(\d+)\s+available/i,  // "12 available"
                            /qty[:.]?\s*(\d+)/i,  // "qty: 12" or "qty 12"
                            /quantity[:.]?\s*(\d+)/i,  // "quantity: 12"
                        ];
                        
                        for (const pattern of quantityPatterns) {
                            const match = quantityText.match(pattern);
                            if (match) {
                                quantity = parseInt(match[1], 10);
                                break;
                            }
                        }
                        
                        // Also check for quantity selector/input
                        const qtyInput = el.querySelector('input[type="number"], select[name*="qty"], select[name*="quantity"]');
                        if (qtyInput) {
                            const max = qtyInput.getAttribute('max') || qtyInput.getAttribute('data-max');
                            if (max) {
                                quantity = parseInt(max, 10);
                            } else {
                                // Check option values in select
                                const options = qtyInput.querySelectorAll('option');
                                if (options.length > 0) {
                                    const lastOption = options[options.length - 1];
                                    const maxVal = parseInt(lastOption.value || lastOption.textContent, 10);
                                    if (!isNaN(maxVal)) {
                                        quantity = maxVal;
                                    }
                                }
                            }
                        }
                        
                        // Extract shipping cost
                        let shipping = 0;
                        const allText = el.innerText || '';
                        
                        // Look for shipping patterns: "+ $X.XX Shipping", "Shipping: $X.XX", etc.
                        const shippingPatterns = [
                            /\\+\\s*\\$([\\d,]+(?:\\.\\d{2})?)\\s*Shipping/i,  // "+ $10.99 Shipping"
                            /Shipping[:.]?\\s*\\$([\\d,]+(?:\\.\\d{2})?)/i,  // "Shipping: $10.99"
                            /Shipping[:.]?\\s*Included/i,  // "Shipping: Included" = $0
                        ];
                        
                        for (const pattern of shippingPatterns) {
                            const match = allText.match(pattern);
                            if (match) {
                                if (match[0].toLowerCase().includes('included')) {
                                    shipping = 0;  // Free shipping
                                } else if (match[1]) {
                                    shipping = parseFloat(match[1].replace(',', ''));
                                }
                                break;
                            }
                        }
                        
                        // Calculate total cost (price + shipping)
                        const total_cost = price + shipping;
                        
                        // Only include if price is valid
                        if (price > 0) {
                            listings.push({
                                price: price,
                                shipping: shipping,
                                total_cost: total_cost,
                                quantity: quantity,
                                condition: condition,
                                seller: seller,
                                title: fullText.substring(0, 200),
                                description: '',
                                variant: ''
                            });
                        }
                    } catch (e) {
                        // Skip this listing
                    }
                });
                
                return listings;
            }
        ''')
        
        listings = listings_data if listings_data else []
        
        # Filter by minimum price (exclude listings 19%+ below market price)
        if min_price > 0:
            listings = [l for l in listings if l.get('price', 0) >= min_price]
        
        logger.debug(f"  Extracted {len(listings)} listings from page (min ${min_price:.2f}, ≥81% of market)")
                
    except Exception as e:
        logger.warning(f"Error extracting listings: {e}")
    
    return listings


def get_recent_sales_floor(box_id: str, days: int = 14) -> Optional[float]:
    """
    Get a floor price estimate from recent Apify market price data.
    
    NOTE: Apify provides aggregated weekly buckets, not individual sales transactions.
    We use market_price_usd (average sale price from the bucket) as a proxy for the floor.
    This is not perfect, but helps validate listings floor against recent market activity.
    
    Args:
        box_id: UUID of the booster box
        days: How many days back to look for sales data
        
    Returns:
        Market price (used as floor proxy) from recent Apify data, or None if not available
    """
    try:
        hist_file = Path('data/historical_entries.json')
        if not hist_file.exists():
            return None
        
        with open(hist_file, 'r') as f:
            hist = json.load(f)
        
        if box_id not in hist or not hist[box_id]:
            return None
        
        # Get entries from the last N days
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        recent_entries = []
        
        for entry in hist[box_id]:
            try:
                entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d').date()
                if entry_date >= cutoff_date and entry.get('source') == 'apify_tcgplayer':
                    # Apify provides aggregated weekly buckets, not individual sales
                    # We have market_price_usd (average sale price) and floor_price_usd
                    # Note: floor_price_usd is set to market_price (not lowSalePrice) because
                    # lowSalePrice is often old/outlier data
                    market_price = entry.get('market_price_usd') or entry.get('floor_price_usd')
                    
                    if market_price and market_price > 0:
                        recent_entries.append({
                            'date': entry_date,
                            'market_price': float(market_price),
                            # Use market_price as proxy for sales floor (it's the average sale price)
                            'sales_floor_proxy': float(market_price)
                        })
            except (ValueError, KeyError):
                continue
        
        if not recent_entries:
            return None
        
        # Sort by date (most recent first)
        recent_entries.sort(key=lambda x: x['date'], reverse=True)
        
        # Strategy: Use the market price (average sale price) from recent entries
        # Since Apify only provides aggregated weekly buckets, we use market_price as a proxy
        # for the sales floor (it represents the average sale price, which is closer to floor than outliers)
        if len(recent_entries) == 1:
            return recent_entries[0]['sales_floor_proxy']
        
        # For multiple entries, use the minimum market price from the most recent 7 days
        # This gives us a conservative estimate of the floor from recent sales
        most_recent_week = [e for e in recent_entries if (datetime.now().date() - e['date']).days <= 7]
        if most_recent_week:
            min_price = min(e['sales_floor_proxy'] for e in most_recent_week)
            return min_price
        
        # Fallback: use minimum from all recent entries
        return min(e['sales_floor_proxy'] for e in recent_entries)
        
    except Exception as e:
        logger.warning(f"  Could not load recent sales data: {e}")
        return None


def discover_floor_price_with_sales_validation(
    listings_prices: List[float], 
    sales_floor: Optional[float],
    box_id: str
) -> float:
    """
    Discover floor price from listings, validated against recent Apify market price.
    
    NOTE: sales_floor is actually market_price_usd from Apify (average sale price),
    not individual sales. It's used as a proxy to validate listings floor.
    
    Strategy:
    1. Find floor from listings (lowest price with 3+ listings = cluster)
    2. Compare with recent Apify market price (proxy for sales floor)
    3. If market price is significantly higher, it might indicate listings have bad data
    4. Use conservative approach: prefer the higher of the two, or listings if close
    
    Args:
        listings_prices: List of prices from legitimate listings
        sales_floor: Market price from recent Apify data (used as floor proxy), or None
        box_id: UUID for logging
        
    Returns:
        Discovered and validated floor price
    """
    if not listings_prices:
        # No listings, use sales floor if available
        if sales_floor:
            logger.info(f"  No listings found, using sales floor: ${sales_floor:.2f}")
            return sales_floor
        return 0
    
    # Sort prices
    prices = sorted(listings_prices)
    
    # Start with lowest price
    discovered_floor = prices[0]
    
    # Validate it's legitimate (not an outlier)
    # Only reject the lowest price if it's a clear outlier (>20% below next price)
    # AND there are no other listings close to it
    if len(prices) > 1:
        next_price = prices[1]  # Second lowest price
        diff_pct = ((next_price - discovered_floor) / discovered_floor) * 100
        
        # If lowest price is >20% below next price, it might be an outlier
        if diff_pct > 20:
            # Check if there's a cluster at a higher price (3+ listings)
            # If so, use the cluster instead
            for price in prices[:10]:  # Check first 10 unique prices
                price_listings = [p for p in prices if p == price]
                if len(price_listings) >= 3:  # Found a cluster
                    # Only use cluster if it's not too far from the lowest
                    cluster_diff = ((price - discovered_floor) / discovered_floor) * 100
                    if cluster_diff < 15:  # Cluster is within 15% of lowest
                        discovered_floor = price
                        logger.info(f"  Lowest price (${prices[0]:.2f}) is {diff_pct:.1f}% below next, but cluster found at ${price:.2f} - using cluster")
                        break
                    else:
                        # Cluster is too far, lowest might be legitimate
                        logger.info(f"  Lowest price (${prices[0]:.2f}) is {diff_pct:.1f}% below next, but cluster at ${price:.2f} is too far - using lowest")
                        discovered_floor = prices[0]
                        break
            else:
                # No cluster found, use lowest price (it's the floor)
                logger.info(f"  Lowest price (${prices[0]:.2f}) is {diff_pct:.1f}% below next, but no cluster found - using lowest as floor")
                discovered_floor = prices[0]
        else:
            # Lowest price is within 20% of next price - it's legitimate
            logger.info(f"  Lowest price (${discovered_floor:.2f}) is within {diff_pct:.1f}% of next price - using as floor")
    
    # Now validate against sales data
    if sales_floor and sales_floor > 0:
        # Compare listings floor with sales floor
        diff_pct = abs(discovered_floor - sales_floor) / sales_floor * 100
        
        if diff_pct <= 10:
            # Close match (within 10%) - listings are accurate, use listings (more current)
            logger.info(f"  Listings floor (${discovered_floor:.2f}) matches market price (${sales_floor:.2f}) - using listings")
            return discovered_floor
        elif discovered_floor < sales_floor:
            # Listings floor is lower - could be bad data (Japanese/unsealed slipping through)
            # If difference is >15%, market price is more trustworthy
            if diff_pct > 15:
                logger.warning(f"  Listings floor (${discovered_floor:.2f}) is {diff_pct:.1f}% below market price (${sales_floor:.2f})")
                logger.warning(f"  Using market price (more trustworthy - listings may have bad data)")
                return sales_floor
            else:
                # Within 15%, use listings (more current) but log the difference
                logger.info(f"  Listings floor (${discovered_floor:.2f}) is {diff_pct:.1f}% below market price, but within tolerance - using listings")
                return discovered_floor
        else:
            # Listings floor is higher - listings are more current, use listings
            logger.info(f"  Listings floor (${discovered_floor:.2f}) is higher than market price (${sales_floor:.2f}) - using listings (more current)")
            return discovered_floor
    else:
        # No Apify data available, use listings floor
        logger.info(f"  No recent Apify data available, using listings floor: ${discovered_floor:.2f}")
        return discovered_floor


async def scrape_box(page: Page, box_id: str, url: str, market_price_hint: float) -> Optional[Dict]:
    """
    Scrape all listings for a single box.
    
    Strategy:
    1. First, discover the actual floor price from current listings
    2. Use that floor price as the market price (more accurate than historical data)
    3. Calculate range: floor_price * 0.85 to floor_price * 1.20
    4. Count listings within that range
    """
    logger.info(f"Scraping: {url[:60]}...")
    
    all_listings_raw = []  # All legitimate listings (before price range filtering)
    all_listings_in_range = []  # Listings within -15% to +20% of discovered floor
    current_page = 1
    max_pages = 20
    
    # Use historical market price as a hint for initial filtering (to avoid packs)
    # But we'll discover the actual floor price from listings
    initial_min_price = 100  # Basic filter to exclude packs
    if market_price_hint and market_price_hint > 0:
        initial_min_price = market_price_hint * 0.50  # Use 50% of hint to catch legitimate listings
        logger.info(f"  Using historical market price hint: ${market_price_hint:.2f} (for initial filtering)")
    else:
        logger.warning(f"  No historical market price available, using basic filter: ${initial_min_price:.2f}")
    
    try:
        # Navigate to product page
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)  # Wait for Vue app to render
        
        # Scroll to trigger lazy loading
        for i in range(5):
            await page.evaluate(f'window.scrollTo(0, {(i+1) * 400})')
            await asyncio.sleep(0.3)
        
        # Click on "Listings" tab to show all listings
        try:
            listings_tab = await page.query_selector('text=Listings')
            if listings_tab:
                await listings_tab.click()
                await asyncio.sleep(2)  # Wait for listings to load
                logger.debug("  Clicked Listings tab")
        except Exception as e:
            logger.debug(f"  No Listings tab: {e}")
        
        await asyncio.sleep(1)
        
        # Phase 1: Discover floor price from first few pages
        discovered_floor_price = None
        min_box_price = None
        max_box_price = None
        discovery_pages = 3  # Scrape first 3 pages to discover floor
        
        while current_page <= max_pages:
            # Scroll down to listings section (page resets to top after pagination click)
            await page.evaluate('window.scrollTo(0, 2000)')
            await asyncio.sleep(2)
            
            # Additional scrolls to ensure listings are loaded
            for i in range(3):
                await page.evaluate(f'window.scrollTo(0, {(i+1) * 600})')
                await asyncio.sleep(0.5)
            
            # Scrape current page (filter only for Japanese/suspicious/packs, not price range yet)
            page_listings_raw = await scrape_listings_page(page, min_price=initial_min_price)
            all_listings_raw.extend(page_listings_raw)
            
            # After discovery phase, calculate floor price and range
            if current_page >= discovery_pages and discovered_floor_price is None:
                if all_listings_raw:
                    # Get listings prices (use total_cost = price + shipping for floor calculation)
                    listings_prices = [l.get('total_cost', l.get('price', 0)) for l in all_listings_raw]
                    
                    # Get recent market price from Apify data (used as floor proxy)
                    sales_floor = get_recent_sales_floor(box_id, days=14)
                    if sales_floor:
                        logger.info(f"  Found recent market price (floor proxy): ${sales_floor:.2f} (from Apify data)")
                    
                    # Discover floor price from listings, validated against sales data
                    discovered_floor_price = discover_floor_price_with_sales_validation(
                        listings_prices, 
                        sales_floor, 
                        box_id
                    )
                    
                    if discovered_floor_price <= 0:
                        logger.error(f"  Could not discover valid floor price")
                        return None
                    
                    # Calculate price range from discovered floor price
                    min_box_price = discovered_floor_price * 0.85  # 15% below floor
                    max_box_price = discovered_floor_price * 1.20  # 20% above floor
                    
                    logger.info(f"  Final floor price: ${discovered_floor_price:.2f} (from {len(all_listings_raw)} listings + sales validation)")
                    logger.info(f"  Price range: ${min_box_price:.2f} - ${max_box_price:.2f} (floor: ${discovered_floor_price:.2f}, -15% to +20%)")
                    
                    # Now filter existing listings by the discovered range and expand by quantity (use total_cost = price + shipping)
                    filtered_listings = [
                        l for l in all_listings_raw
                        if min_box_price <= l.get('total_cost', l.get('price', 0)) <= max_box_price
                    ]
                    # Expand by quantity - each unit = 1 listing
                    all_listings_in_range = []
                    for listing in filtered_listings:
                        quantity = listing.get('quantity', 1)
                        for i in range(quantity):
                            expanded_listing = listing.copy()
                            expanded_listing['quantity'] = 1
                            expanded_listing['unit_number'] = i + 1
                            all_listings_in_range.append(expanded_listing)
                else:
                    logger.warning(f"  No listings found after {current_page} pages, cannot discover floor price")
                    return None
            
            # Phase 2: Filter by discovered price range and count
            if discovered_floor_price is not None:
                # Filter current page listings by discovered range (use total_cost = price + shipping)
                page_listings = [
                    l for l in page_listings_raw 
                    if min_box_price <= l.get('total_cost', l.get('price', 0)) <= max_box_price
                ]
                
                if not page_listings:
                    logger.info(f"  Page {current_page}: 0 listings in range (${min_box_price:.2f} - ${max_box_price:.2f})")
                    
                    # Check if all listings exceed max_price (stop pagination)
                    if page_listings_raw:
                        min_listing_price = min([l.get('total_cost', l.get('price', 0)) for l in page_listings_raw])
                        if min_listing_price > max_box_price:
                            logger.info(f"  All listings exceed 20% threshold (${max_box_price:.2f}), stopping pagination")
                            break
                else:
                    # Expand listings by quantity - each unit counts as a separate listing
                    expanded_listings = []
                    for listing in page_listings:
                        quantity = listing.get('quantity', 1)
                        for i in range(quantity):
                            expanded_listing = listing.copy()
                            expanded_listing['quantity'] = 1
                            expanded_listing['unit_number'] = i + 1
                            expanded_listings.append(expanded_listing)
                    
                    logger.info(f"  Page {current_page}: Found {len(expanded_listings)} unit listings in range! (first: ${expanded_listings[0]['price']:.2f})")
                    all_listings_in_range.extend(expanded_listings)
            else:
                # Still in discovery phase, just collecting raw listings
                logger.info(f"  Page {current_page}: Collected {len(page_listings_raw)} listings (discovering floor price...)")
            
            # Try to go to next page - click numbered pagination buttons (1, 2, 3, etc.)
            next_page_num = current_page + 1
            
            # Get all pagination buttons and find the one with the exact page number (skip active)
            page_button = None
            
            try:
                pagination_buttons = await page.query_selector_all('[class*="pagination"] button, [class*="pagination"] a')
                
                for btn in pagination_buttons:
                    try:
                        text = (await btn.inner_text()).strip()
                        classes = await btn.get_attribute('class') or ''
                        
                        # Skip if it's the active/current page (blue button)
                        is_active = 'is-active' in classes or 'active' in classes.lower()
                        bg_color = await btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
                        is_blue = 'rgb' in bg_color and ('0, 123' in bg_color or '0, 0, 255' in bg_color or 'rgb(0' in bg_color)
                        
                        if is_active or is_blue:
                            continue
                        
                        # Check if it matches the next page number (exact match)
                        if text == str(next_page_num):
                            page_button = btn
                            logger.debug(f"  Found page {next_page_num} button")
                            break
                    except:
                        pass
                
                # Fallback: Try the right arrow (>) button
                if not page_button:
                    for btn in pagination_buttons:
                        try:
                            text = (await btn.inner_text()).strip()
                            if text == '>' or text == '»' or 'next' in (await btn.get_attribute('aria-label') or '').lower():
                                page_button = btn
                                logger.debug(f"  Using right arrow button")
                                break
                        except:
                            pass
            except Exception as e:
                logger.debug(f"  Error finding pagination buttons: {e}")
            
            if page_button:
                # Check if disabled
                is_disabled = await page_button.get_attribute('disabled')
                aria_disabled = await page_button.get_attribute('aria-disabled')
                classes = await page_button.get_attribute('class') or ''
                
                if is_disabled or aria_disabled == 'true' or 'disabled' in classes.lower():
                    logger.info(f"  No more pages available (page {next_page_num} button disabled)")
                    break
                
                # Click page number button
                try:
                    logger.debug(f"  Clicking page {next_page_num} button...")
                    await page_button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await page_button.click()
                    
                    # Wait for new page to load
                    await asyncio.sleep(human_delay() + 2)  # Extra wait for page load
                    
                    # Scroll to trigger lazy loading
                    await page.evaluate('window.scrollTo(0, 500)')
                    await asyncio.sleep(1)
                    
                    current_page = next_page_num
                    logger.debug(f"  Navigated to page {current_page}")
                except Exception as e:
                    logger.warning(f"  Error clicking page {next_page_num} button: {e}")
                    break
            else:
                logger.info(f"  No page {next_page_num} button found (reached end)")
                break
        
        # If we didn't discover a floor price, we can't proceed
        if discovered_floor_price is None:
            logger.error(f"  Could not discover floor price - no legitimate listings found")
            return None
        
        # all_listings_in_range only contains listings within the price range (-15% to +20%)
        # Each listing represents 1 unit (already expanded by quantity)
        listings_count_in_range = len(all_listings_in_range)
        
        # Calculate day-over-day change (only for listings within price range)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        yesterday_count = None
        listings_change = None
        
        try:
            # Load historical data
            hist_file = Path('data/historical_entries.json')
            if hist_file.exists():
                with open(hist_file, 'r') as f:
                    hist = json.load(f)
                
                if box_id in hist and hist[box_id]:
                    # Find yesterday's entry (look for listings_count_in_range or listings_count)
                    for entry in sorted(hist[box_id], key=lambda x: x.get('date', ''), reverse=True):
                        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                        if entry_date == yesterday:
                            # Try to get the count within price range
                            yesterday_count = entry.get('listings_count_in_range', 
                                                       entry.get('listings_count', 
                                                               entry.get('active_listings_count', None)))
                            break
                        elif entry_date < yesterday:
                            # No entry for yesterday, stop looking
                            break
                    
                    # Calculate change
                    if yesterday_count is not None:
                        listings_change = listings_count_in_range - yesterday_count
        except Exception as e:
            logger.warning(f"  Could not load historical data for comparison: {e}")
        
        # Log day-over-day change
        if yesterday_count is not None:
            change_sign = "+" if listings_change >= 0 else ""
            logger.info(f"  Day-over-day change (within range): {change_sign}{listings_change} listings ({yesterday_count} yesterday → {listings_count_in_range} today)")
        else:
            logger.info(f"  Day-over-day change: No previous data available (first run or no data for {yesterday})")
        
        # Save today's listings count to historical data
        try:
            hist_file = Path('data/historical_entries.json')
            if hist_file.exists():
                with open(hist_file, 'r') as f:
                    hist = json.load(f)
            else:
                hist = {}
            
            if box_id not in hist:
                hist[box_id] = []
            
            # Check if today's entry already exists
            today_str = today.strftime('%Y-%m-%d')
            today_entry = None
            for entry in hist[box_id]:
                if entry.get('date') == today_str:
                    today_entry = entry
                    break
            
            # Update or create today's entry
            if today_entry:
                today_entry['listings_count_in_range'] = listings_count_in_range
                today_entry['listings_count'] = listings_count_in_range  # Keep for backward compatibility
                today_entry['market_price'] = discovered_floor_price  # Update with discovered floor price
                today_entry['floor_price_usd'] = discovered_floor_price
                today_entry['price_range_min'] = min_box_price
                today_entry['price_range_max'] = max_box_price
                today_entry['discovered_from_listings'] = True
                today_entry['timestamp'] = datetime.now().isoformat()
            else:
                # Create new entry for today
                new_entry = {
                    'date': today_str,
                    'source': 'listings_scraper',
                    'data_type': 'listings',
                    'listings_count_in_range': listings_count_in_range,  # Count within -15% to +20% price range
                    'listings_count': listings_count_in_range,  # Keep for backward compatibility
                    'price_range_min': min_box_price,
                    'price_range_max': max_box_price,
                    'market_price': discovered_floor_price,  # Use discovered floor price as market price
                    'floor_price_usd': discovered_floor_price,  # Also save as floor_price_usd
                    'discovered_from_listings': True,  # Flag to indicate this was discovered, not from Apify
                    'timestamp': datetime.now().isoformat()
                }
                hist[box_id].append(new_entry)
                # Sort by date
                hist[box_id].sort(key=lambda x: x.get('date', ''))
            
            # Save back to file
            with open(hist_file, 'w') as f:
                json.dump(hist, f, indent=2)
        except Exception as e:
            logger.warning(f"  Could not save listings count to historical data: {e}")
        
        # Process listings (for other metrics) - use discovered floor price
        result = process_listings(all_listings_in_range, discovered_floor_price)
        result['box_id'] = box_id
        result['url'] = url
        result['pages_scraped'] = current_page
        result['scrape_timestamp'] = datetime.now().isoformat()
        result['listings_count_in_range'] = listings_count_in_range  # Add count within range
        result['day_over_day_change'] = listings_change  # Add day-over-day change
        result['discovered_floor_price'] = discovered_floor_price  # The floor price we discovered
        result['price_range_min'] = min_box_price
        result['price_range_max'] = max_box_price
        
        return result
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


async def run_scraper():
    """Main scraper entry point"""
    logger.info("=" * 60)
    logger.info("Starting TCGplayer Listings Scraper")
    logger.info("=" * 60)
    
    # Get browser profile for this session
    profile = get_random_profile()
    logger.info(f"Browser profile: {profile['user_agent'][:50]}...")
    
    # Get products to scrape
    products = get_daily_products()
    
    # Load market prices from historical data (for price range calculation)
    # Find the most recent entry that has a market price (not just the latest entry)
    market_prices = {}
    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
        for box_id in TCGPLAYER_URLS.keys():
            if box_id in hist and hist[box_id]:
                # Sort by date descending and find first entry with market price
                sorted_entries = sorted(hist[box_id], key=lambda x: x.get('date', ''), reverse=True)
                for entry in sorted_entries:
                    market_price = entry.get('market_price_usd') or entry.get('floor_price_usd', 0)
                    if market_price and market_price > 0:
                        market_prices[box_id] = market_price
                        logger.debug(f"  {box_id[:8]}...: Using market price ${market_price:.2f} from {entry.get('date')}")
                        break
                if box_id not in market_prices:
                    logger.warning(f"  {box_id[:8]}...: No market price found in historical data")
    except Exception as e:
        logger.warning(f"Could not load market prices: {e}")
    
    results = []
    errors = []
    
    async with async_playwright() as p:
        # Launch browser with stealth - use real Chrome for better fingerprint
        browser = await p.chromium.launch(
            headless=False,  # Headed mode for better fingerprint
            channel="chrome",  # Use installed Chrome (better TLS fingerprint)
            args=['--start-minimized']
        )
        
        context = await browser.new_context(
            user_agent=profile['user_agent'],
            viewport=profile['viewport'],
        )
        
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        # Visit homepage first (natural behavior)
        logger.info("Visiting TCGplayer homepage...")
        await page.goto('https://www.tcgplayer.com', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(human_delay())
        
        # Scrape each product
        for box_id, url in products:
            if box_id.startswith('noise_'):
                # Noise product - just visit, don't extract data
                logger.info(f"Visiting noise product: {url[:50]}...")
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    await asyncio.sleep(human_delay())
                except:
                    pass
                continue
            
            # Real target - scrape data
            market_price = market_prices.get(box_id, 0)
            result = await scrape_box(page, box_id, url, market_price)
            
            if result:
                results.append(result)
            else:
                errors.append(box_id)
            
            await asyncio.sleep(human_delay())
        
        await browser.close()
    
    # Save results
    logger.info("=" * 60)
    logger.info(f"Scraping complete: {len(results)} success, {len(errors)} errors")
    
    if results:
        save_results(results)
        
        # Summary of day-over-day changes
        logger.info("\n" + "=" * 60)
        logger.info("DAY-OVER-DAY LISTINGS CHANGES (within -15% to +20% range)")
        logger.info("=" * 60)
        for result in results:
            box_id = result['box_id']
            count = result.get('listings_count_in_range', 0)
            change = result.get('day_over_day_change')
            if change is not None:
                change_sign = "+" if change >= 0 else ""
                logger.info(f"  {box_id[:8]}...: {change_sign}{change} listings (now: {count})")
            else:
                logger.info(f"  {box_id[:8]}...: {count} listings (no previous data)")
    
    return results, errors


def save_results(results: List[Dict]):
    """Save scraped data to historical_entries.json"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
    except:
        hist = {}
    
    for result in results:
        box_id = result['box_id']
        
        if box_id not in hist:
            hist[box_id] = []
        
        # Create entry (but don't overwrite if listings_count_in_range was already saved)
        # Check if entry already exists with listings_count_in_range
        existing_entry = None
        for e in hist[box_id]:
            if e.get('date') == today:
                existing_entry = e
                break
        
        if existing_entry and 'listings_count_in_range' in existing_entry:
            # Update existing entry with additional metrics
            existing_entry.update({
                'floor_price_usd': result.get('floor_price'),
                'active_listings_count': result.get('listings_within_20pct'),
                'total_listings': result.get('total_listings'),
                'scrape_timestamp': result.get('scrape_timestamp'),
                'pages_scraped': result.get('pages_scraped'),
                'filters_applied': result.get('filters_applied'),
                'day_over_day_change': result.get('day_over_day_change'),
            })
            logger.info(f"Updated {box_id}: {existing_entry.get('listings_count_in_range')} listings in range @ ${result.get('floor_price', 0):.2f}")
        else:
            # Create new entry
            entry = {
                'date': today,
                'source': 'tcgplayer_scraper',
                'floor_price_usd': result.get('floor_price'),
                'active_listings_count': result.get('listings_within_20pct'),
                'total_listings': result.get('total_listings'),
                'listings_count_in_range': result.get('listings_count_in_range', result.get('listings_within_20pct')),
                'scrape_timestamp': result.get('scrape_timestamp'),
                'pages_scraped': result.get('pages_scraped'),
                'filters_applied': result.get('filters_applied'),
                'day_over_day_change': result.get('day_over_day_change'),
            }
            
            # Remove existing entry for today (update mode)
            hist[box_id] = [e for e in hist[box_id] if e.get('date') != today]
            hist[box_id].append(entry)
            
            logger.info(f"Saved {box_id}: {entry.get('listings_count_in_range')} listings in range @ ${result.get('floor_price', 0):.2f}")
    
    # Backup and save
    backup_path = Path(f'data/historical_entries_backup_{today}.json')
    with open('data/historical_entries.json', 'r') as f:
        backup_path.write_text(f.read())
    
    with open('data/historical_entries.json', 'w') as f:
        json.dump(hist, f, indent=2)
    
    logger.info(f"Saved {len(results)} entries to historical_entries.json")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    # Run scraper
    asyncio.run(run_scraper())

