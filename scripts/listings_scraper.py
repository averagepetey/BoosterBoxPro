#!/usr/bin/env python3
"""
TCGplayer Listings Scraper
--------------------------
Gentle, stealth scraper for extracting active listings data.
Reference: Setup Guides/LISTINGS_SCRAPER_RULES.md
"""

import asyncio
import json
import logging
import os
import random
import sys
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
                            (fullText.includes('pack') && !fullText.includes('box'))) {
                            return; // Skip this listing
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
                        
                        // Only include if price is valid
                        if (price > 0) {
                            listings.push({
                                price: price,
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


async def scrape_box(page: Page, box_id: str, url: str, market_price: float) -> Optional[Dict]:
    """Scrape all listings for a single box"""
    logger.info(f"Scraping: {url[:60]}...")
    
    all_listings = []
    current_page = 1
    max_pages = 15  # Increased - boxes might be on later pages
    
    # Filter: Don't count listings 19% or more below market price
    # Keep listings that are at least 81% of market price
    if market_price and market_price > 0:
        min_box_price = market_price * 0.81  # 81% of market price (19% below = filter out)
        logger.info(f"  Using minimum box price filter: ${min_box_price:.2f} (market: ${market_price:.2f}, keeping ≥81%)")
    else:
        # Fallback: if no market price, use a conservative estimate
        min_box_price = 100  # Default fallback
        logger.warning(f"  No market price available, using fallback: ${min_box_price:.2f}")
    
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
        
        while current_page <= max_pages:
            # Scrape current page (filter for boxes only - $100+)
            page_listings = await scrape_listings_page(page, min_price=min_box_price)
            
            if not page_listings:
                logger.info(f"  Page {current_page}: No box listings found (all < ${min_box_price}), continuing...")
                # Keep going - boxes might be on later pages
            else:
                logger.info(f"  Page {current_page}: {len(page_listings)} box listings (≥${min_box_price})")
                all_listings.extend(page_listings)
            
            # Check if we've passed the 20% threshold (only if we have listings)
            if all_listings:
                floor = min(l['price'] for l in all_listings)
                threshold = floor * WITHIN_20PCT_THRESHOLD
                highest_on_page = max(l['price'] for l in page_listings) if page_listings else 0
                
                if highest_on_page > threshold:
                    logger.info(f"  Reached 20% threshold (${threshold:.2f}), stopping pagination")
                    break
            
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
                        
                        # Skip if it's the active/current page
                        if 'is-active' in classes or 'active' in classes.lower():
                            continue
                        
                        # Check if it matches the next page number
                        if text == str(next_page_num):
                            page_button = btn
                            logger.debug(f"  Found page {next_page_num} button")
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
        
        # Process listings
        result = process_listings(all_listings, market_price)
        result['box_id'] = box_id
        result['url'] = url
        result['pages_scraped'] = current_page
        result['scrape_timestamp'] = datetime.now().isoformat()
        
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
    
    # Load market prices from historical data (for outlier detection)
    market_prices = {}
    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
        for box_id in TCGPLAYER_URLS.keys():
            if box_id in hist and hist[box_id]:
                latest = sorted(hist[box_id], key=lambda x: x.get('date', ''), reverse=True)[0]
                market_prices[box_id] = latest.get('market_price_usd') or latest.get('floor_price_usd', 0)
    except Exception as e:
        logger.warning(f"Could not load market prices: {e}")
    
    results = []
    errors = []
    
    async with async_playwright() as p:
        # Use Playwright's Chromium (works in Docker). Use channel="chrome" only when Chrome is installed (e.g. local).
        use_chrome = os.environ.get("SCRAPER_USE_CHROME", "").lower() in ("1", "true", "yes")
        launch_options = {
            "headless": True,  # Required in Docker; set SCRAPER_USE_CHROME=1 locally for headed Chrome
            "args": ["--no-sandbox", "--disable-setuid-sandbox"],
        }
        if use_chrome:
            launch_options["channel"] = "chrome"
            launch_options["headless"] = False
        browser = await p.chromium.launch(**launch_options)
        
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
    
    return results, errors


def save_results(results: List[Dict]):
    """Save scraped data to historical_entries.json and to box_metrics_unified (DB)."""
    today = datetime.now().strftime('%Y-%m-%d')
    # Ensure project root on path so we can import app.services
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
    except Exception:
        hist = {}

    try:
        from app.services.box_metrics_writer import upsert_daily_metrics
    except ImportError:
        upsert_daily_metrics = None

    for result in results:
        box_id = result['box_id']

        if box_id not in hist:
            hist[box_id] = []

        # Create entry
        entry = {
            'date': today,
            'source': 'tcgplayer_scraper',
            'floor_price_usd': result.get('floor_price'),
            'active_listings_count': result.get('listings_within_20pct'),
            'total_listings': result.get('total_listings'),
            'scrape_timestamp': result.get('scrape_timestamp'),
            'pages_scraped': result.get('pages_scraped'),
            'filters_applied': result.get('filters_applied'),
        }

        # Remove existing entry for today (update mode)
        hist[box_id] = [e for e in hist[box_id] if e.get('date') != today]
        hist[box_id].append(entry)

        if upsert_daily_metrics:
            ok = upsert_daily_metrics(
                booster_box_id=box_id,
                metric_date=today,
                floor_price_usd=result.get('floor_price'),
                active_listings_count=result.get('listings_within_20pct'),
            )
            if ok:
                logger.debug(f"DB upsert ok for {box_id}")
            else:
                logger.warning(f"DB upsert failed for {box_id} (e.g. missing FK)")

        logger.info(f"Saved {box_id}: {result.get('listings_within_20pct')} listings @ ${result.get('floor_price', 0):.2f}")
    
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

