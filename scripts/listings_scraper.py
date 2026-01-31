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
import time
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
    # Clear damage/condition issues
    'damaged', 'opened', 'no shrink wrap',  # no shrink wrap = unsealed
    'heavy play', 'poor condition',
    'missing', 'incomplete', 'resealed',
    'no seal', 'unsealed',
    # Only flag "box only" if it's NOT a booster box (context-dependent, handled in function)
    'box only',
    # Only flag "empty" if it's "empty box" (context-dependent)
    'empty',
    # Only flag "display" if it's "for display" or "display only" (context-dependent)
    'display', 'for display',
    # Exclude loose packs / not booster box (phrases only)
    'loose packs', 'loose pack', 'unsealed box', 'no box',
    'packs only', 'pack only', 'unsealed or no box', 'no box.',
]

# Thresholds
OUTLIER_THRESHOLD_PCT = 0.75  # 75% of market price
MIN_CLUSTER_SIZE = 5  # Need 5+ clean low-priced to confirm pullback
WITHIN_20PCT_THRESHOLD = 1.20  # Floor × 1.20
WITHIN_10PCT_THRESHOLD = 1.10  # Floor × 1.10 (for expected time to sale)

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


def get_suspicious_keyword(listing: Dict) -> Optional[str]:
    """Return the first matching suspicious keyword, or None if listing is clean."""
    import re
    title = (listing.get('title', '') or '').lower()
    description = (listing.get('description', '') or '').lower()
    condition = (listing.get('condition', '') or '').lower()
    variant = (listing.get('variant', '') or '').lower()
    full_text = title + ' ' + description + ' ' + condition + ' ' + variant
    
    # Skip if this is clearly a legitimate booster box listing
    # Check for legitimate booster box indicators first
    legitimate_indicators = [
        'booster box', 'premium booster', 'extra booster', 'premium box',
        'factory sealed', 'sealed', 'mint', 'near mint', 'new'
    ]
    has_legitimate_indicator = any(indicator in full_text for indicator in legitimate_indicators)
    
    # Only apply suspicious filter if we don't have strong legitimate indicators
    # OR if we have both legitimate AND suspicious indicators (then suspicious wins)
    
    for keyword in SUSPICIOUS_KEYWORDS:
        escaped = re.escape(keyword)
        if ' ' in keyword:
            pattern = r'\b' + escaped + r'\b'
        else:
            pattern = r'\b' + escaped + r'\b'
        
        if re.search(pattern, full_text):
            # Skip ambiguous matches if we have legitimate indicators
            if has_legitimate_indicator:
                # These keywords are too ambiguous when we have legitimate indicators
                ambiguous_keywords = ['display', 'empty', 'box only']
                if keyword in ambiguous_keywords:
                    # Only flag if it's clearly suspicious context
                    if keyword == 'display':
                        # Only flag if it's "for display" or "display only", not "display case"
                        if not re.search(r'\b(for\s+)?display\s+(only|purposes?)\b', full_text):
                            continue
                    elif keyword == 'empty':
                        # Only flag if it's "empty box" explicitly, not just "empty"
                        if not re.search(r'\bempty\s+box\b', full_text):
                            continue
                    elif keyword == 'box only':
                        # Skip if it's part of legitimate booster box text
                        if 'booster box' in full_text or 'premium box' in full_text:
                            continue
            
            # Additional context checks
            if keyword == 'display':
                # Skip "display case" (legitimate storage)
                if 'display case' in full_text:
                    continue
            elif keyword == 'box only':
                # Skip if it's clearly a booster box listing
                if 'booster box' in full_text or 'premium box' in full_text:
                    continue
            
            return keyword
    return None


def is_suspicious_listing(listing: Dict) -> bool:
    """Check if listing has suspicious keywords (title, description, condition, variant)"""
    return get_suspicious_keyword(listing) is not None


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
        # Log examples to debug - show first 3 removed listings and their matching keywords
        removed_count = 0
        keyword_counts = {}
        for l in listings:
            kw = get_suspicious_keyword(l)
            if kw:
                if removed_count < 3:
                    snippet = (l.get('title', '') or l.get('condition', '') or l.get('variant', ''))[:100]
                    logger.info(f"    Removed #{removed_count+1}: keyword '{kw}' in: {snippet!r}")
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
                removed_count += 1
        
        # Show summary of which keywords matched most
        if keyword_counts:
            logger.info(f"    Keyword matches: {dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))}")
    listings = clean_listings
    
    # Step 3: Smart outlier detection
    listings = filter_outlier_prices(listings, market_price)
    
    if not listings:
        return {
            'floor_price': None,
            'listings_within_20pct': 0,
            'listings_within_10pct_floor': 0,
            'filters_applied': {
                'japanese_removed': jp_removed,
                'suspicious_removed': suspicious_removed,
            }
        }
    
    # Step 4: Calculate floor price; ensure quantity exists (default 1)
    for l in listings:
        if 'quantity' not in l or l.get('quantity', 0) < 1:
            l['quantity'] = 1
    floor_price = min(l['price'] for l in listings)
    
    # Step 5: Boxes within 20% above floor (primary listings metric) and within 10% (for expected time to sale)
    threshold_20pct = floor_price * WITHIN_20PCT_THRESHOLD
    threshold_10pct = floor_price * WITHIN_10PCT_THRESHOLD
    within_20pct = [l for l in listings if l['price'] <= threshold_20pct]
    within_10pct = [l for l in listings if l['price'] <= threshold_10pct]
    boxes_within_20pct = sum(l.get('quantity', 1) for l in within_20pct)
    boxes_within_10pct = sum(l.get('quantity', 1) for l in within_10pct)
    
    logger.info(f"  Floor: ${floor_price:.2f}, Within 20% (to ${threshold_20pct:.2f}): {boxes_within_20pct} boxes; Within 10% (to ${threshold_10pct:.2f}): {boxes_within_10pct} boxes")
    
    return {
        'floor_price': floor_price,
        'listings_within_20pct': boxes_within_20pct,
        'listings_within_10pct_floor': boxes_within_10pct,
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
        # Wait for listings to appear - try multiple selectors (TCGplayer DOM varies)
        listing_selector = None
        for selector, timeout_ms in [
            ('.listing-item', 8000),
            ('[class*="listing"]', 5000),
            ('[class*="Listing"]', 5000),
            ('[data-testid*="listing"]', 3000),
            ('[class*="listing-item"]', 3000),
        ]:
            try:
                await page.wait_for_selector(selector, timeout=timeout_ms)
                listing_selector = selector
                logger.debug(f"  Listings container found: {selector}")
                break
            except Exception:
                continue
        if not listing_selector:
            logger.warning("  No listing container found (tried .listing-item, [class*='listing'], etc.) - extracting with broad selector")
        
        # Use JavaScript to extract listing data; try multiple selectors if primary missing
        selector_js = listing_selector or '.listing-item, [class*="listing"], [class*="Listing"]'
        listings_data = await page.evaluate('''
            (sel) => {
                const listings = [];
                const listingElements = document.querySelectorAll(sel);
                
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
                        
                        // Parse quantity ONLY when it looks like the quantity selector: "1" (dropdown) "of 9" = 9 boxes
                        // Ignore pagination ("Page 1 of 4"), total count ("1 of 24 listings"), and other patterns
                        let quantity = 1;
                        const looksLikePagination = /page\s*\d|per\s*page|showing\s*\d+\s*of|\d+\s*of\s*\d+\s*listings/i.test(fullText);
                        const ofMatch = fullText.match(/(\d+)\s*of\s*(\d+)/i);
                        if (ofMatch && !looksLikePagination) {
                            const n = parseInt(ofMatch[2], 10);
                            if (n >= 1 && n <= 9999) quantity = n;
                        }
                        
                        // Only include if price is valid
                        if (price > 0) {
                            listings.push({
                                price: price,
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
        ''', selector_js)
        
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
    max_pages = 10  # Cap so we don't run forever; real last page is detected by ≤2 listings or sharp drop
    
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
        
        # Click on "Listings" tab to show all listings (required for pagination to exist)
        try:
            for loc in [page.locator('text=Listings').first, page.get_by_text('Listings', exact=True).first]:
                if await loc.count() > 0:
                    await loc.click()
                    await asyncio.sleep(2)  # Wait for listings to load
                    logger.debug("  Clicked Listings tab")
                    break
        except Exception as e:
            logger.debug(f"  Listings tab: {e}")
        
        await asyncio.sleep(1)
        
        box_start = time.time()
        BOX_TIMEOUT_SEC = 150  # Per-box max so cron doesn't hang
        prev_page_count = None  # Listings on previous page; used to detect "past last page" (e.g. EB-02 has 2 pages, page 3+ returns 1 bogus)
        
        while current_page <= max_pages:
            if (time.time() - box_start) > BOX_TIMEOUT_SEC:
                logger.warning(f"  Box timeout ({BOX_TIMEOUT_SEC}s), saving progress for {box_id}")
                break
            
            # Scrape current page (filter for boxes only - $100+)
            logger.info(f"  Scraping page {current_page}...")
            page_listings = await scrape_listings_page(page, min_price=min_box_price)
            
            if not page_listings:
                logger.info(f"  Page {current_page}: No box listings found (all < ${min_box_price}), stopping pagination.")
                break
            else:
                # Establish floor + 20% threshold from existing all_listings so we can stop when we hit listings above it (e.g. halfway through page 2)
                threshold = None
                if len(all_listings) >= 3:
                    filtered = [l for l in all_listings if not is_japanese_listing(l)]
                    filtered = [l for l in filtered if not is_suspicious_listing(l)]
                    if filtered:
                        floor = min(l['price'] for l in filtered)
                        threshold = floor * WITHIN_20PCT_THRESHOLD
                
                hit_above_threshold = False
                added_this_page = 0
                for l in page_listings:
                    if threshold is not None and l['price'] > threshold:
                        logger.info(f"  Stopping pagination: hit listing at ${l['price']:.2f} (above 20% threshold ${threshold:.2f}); stopping halfway through page {current_page}.")
                        hit_above_threshold = True
                        break
                    all_listings.append(l)
                    added_this_page += 1
                
                if hit_above_threshold:
                    break
                
                page_units = sum(l.get('quantity', 1) for l in page_listings[:added_this_page])
                logger.info(f"  Page {current_page}: {added_this_page} box listings, {page_units} units (≥${min_box_price}, within 20% of floor)")
                # Past last real page: many sites (e.g. EB-02) only have 2 pages; page 3+ returns 1–2 bogus/duplicate listings
                if current_page >= 2 and len(page_listings) <= 2:
                    logger.info(f"  Stopping pagination: page {current_page} has ≤2 listings (likely past last page).")
                    break
                # Sharp drop: previous page had many listings, this page has very few = we're past the end (e.g. EB-02: page 2 had 7, page 3 has 1)
                if current_page >= 2 and prev_page_count is not None and prev_page_count >= 3 and len(page_listings) < prev_page_count and len(page_listings) <= 2:
                    logger.info(f"  Stopping pagination: sharp drop from {prev_page_count} to {len(page_listings)} listings (past last page).")
                    break
                prev_page_count = len(page_listings)
            
            # Try to go to next page - scroll to bottom so pagination "1, 2, 3" is in view (TCGplayer)
            next_page_num = current_page + 1
            page_button = None
            logger.info(f"  Trying to go to page {next_page_num}...")

            # Scroll to bottom and wait so pagination is visible and stable (TCGplayer often lazy-loads)
            for _ in range(2):
                try:
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(2)
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight - 300)')
                    await asyncio.sleep(1)
                except Exception:
                    pass

            # Strategy 4: URL with page param (TCGplayer may use ?page=2 or no query on first load)
            try:
                from urllib.parse import parse_qs, urlencode, urlparse
                parsed = urlparse(page.url)
                base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                params = parse_qs(parsed.query) if parsed.query else {}
                page_param = next((k for k in ('page', 'pageNumber', 'p', 'pageNum') if k in params), 'page')
                params[page_param] = [str(next_page_num)]
                new_url = base + '?' + urlencode(params, doseq=True)
                await page.goto(new_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(human_delay() + 2)
                await page.evaluate('window.scrollTo(0, 500)')
                await asyncio.sleep(1)
                current_page = next_page_num
                logger.info(f"  Navigated to page {current_page} via URL")
                continue
            except Exception as e:
                logger.debug(f"  URL pagination failed: {e}")

            # Strategy 0: TCGplayer-style numbered buttons "1", "2", "3" at bottom - find and click
            # Prefer Playwright locator with longer timeout so we wait for pagination to be visible
            clicked = False
            try:
                for loc in [
                    page.get_by_role('link', name=str(next_page_num)),
                    page.get_by_role('button', name=str(next_page_num)),
                    page.get_by_text(str(next_page_num), exact=True),
                ]:
                    if await loc.count() > 0:
                        await loc.first.scroll_into_view_if_needed(timeout=10000)
                        await asyncio.sleep(0.5)
                        await loc.first.click(timeout=5000)
                        clicked = True
                        logger.debug(f"  Clicked page {next_page_num} via get_by_role/get_by_text")
                        break
            except Exception as e:
                logger.debug(f"  Playwright locator click: {e}")
            if not clicked:
                try:
                    clicked = await page.evaluate('''(nextPageNum) => {
                        const want = String(nextPageNum);
                        const sel = "button, a[href], [role=\\"button\\"]";
                        const all = Array.from(document.querySelectorAll(sel)).filter(el => {
                            const t = (el.textContent || "").trim();
                            return t === want;
                        });
                        const notDisabled = all.filter(el => !el.disabled && el.getAttribute("aria-disabled") !== "true");
                        const withSiblings = (arr) => arr.filter(el => {
                            const parent = el.parentElement;
                            if (!parent) return false;
                            const sibs = Array.from(parent.children).map(c => (c.textContent || "").trim());
                            return sibs.some(t => /^\\d+$/.test(t));
                        });
                        const toClick = (withSiblings(notDisabled).length ? withSiblings(notDisabled)[0] : notDisabled[0])
                            || (withSiblings(all).length ? withSiblings(all)[0] : all[0]);
                        if (toClick) {
                            toClick.scrollIntoView({ block: "center" });
                            toClick.click();
                            return true;
                        }
                        return false;
                    }''', next_page_num)
                except Exception as e:
                    logger.debug(f"  Numbered-buttons JS error: {e}")
            if clicked:
                await asyncio.sleep(human_delay() + 2)
                await page.evaluate('window.scrollTo(0, 500)')
                await asyncio.sleep(1)
                current_page = next_page_num
                logger.info(f"  Navigated to page {current_page} via pagination click")
                continue

            # Strategy 1: class*="pagination" or "Page" (button/link with page number)
            try:
                for selector in (
                    '[class*="pagination"] button, [class*="pagination"] a',
                    '[class*="Page"] button, [class*="Page"] a',
                    'button[class*="page"], a[class*="page"]',
                    '[data-page]',
                    'nav button, nav a',
                ):
                    els = await page.query_selector_all(selector)
                    for btn in els:
                        try:
                            text = (await btn.inner_text()).strip()
                            classes = (await btn.get_attribute('class') or '').lower()
                            if 'active' in classes or 'current' in classes or 'selected' in classes:
                                continue
                            if text == str(next_page_num):
                                page_button = btn
                                logger.debug(f"  Found page {next_page_num} via selector: {selector[:40]}...")
                                break
                        except Exception:
                            pass
                    if page_button:
                        break
            except Exception as e:
                logger.debug(f"  Pagination selector error: {e}")

            # Strategy 2: any button/link with exact text = page number (e.g. "2") - no nav requirement
            if not page_button:
                try:
                    all_buttons = await page.query_selector_all('button, a[href]')
                    for btn in all_buttons:
                        try:
                            text = (await btn.inner_text()).strip()
                            if text != str(next_page_num):
                                continue
                            if await btn.get_attribute('disabled') or await btn.get_attribute('aria-disabled') == 'true':
                                continue
                            # Prefer if it has a sibling that is also a single digit (1, 3) = pagination row
                            has_sibling_number = await btn.evaluate('''el => {
                                const p = el.parentElement;
                                if (!p) return false;
                                return Array.from(p.children).some(c => /^\\d+$/.test((c.textContent||"").trim()));
                            }''')
                            if has_sibling_number or not page_button:
                                page_button = btn
                                logger.debug(f"  Found page {next_page_num} via text match (1,2,3)")
                                if has_sibling_number:
                                    break
                        except Exception:
                            pass
                except Exception as e:
                    logger.debug(f"  Text match pagination error: {e}")

            # Strategy 3: "Next" or ">" (use locator - no :has-text in query_selector)
            if not page_button:
                try:
                    for label in ('Next', 'next', '>', '›', '»'):
                        loc = page.locator('button, a').filter(has_text=label).first
                        n = await loc.count()
                        if n > 0:
                            el = await loc.element_handle()
                            if el:
                                is_disabled = await el.get_attribute('disabled') or await el.get_attribute('aria-disabled')
                                if not is_disabled:
                                    page_button = el
                                    logger.debug(f"  Found next page via label: {label}")
                                    break
                    if not page_button:
                        for sel in ('[aria-label*="next"]', '[aria-label*="Next"]'):
                            aria_next = await page.query_selector(sel)
                            if aria_next and await aria_next.get_attribute('aria-disabled') != 'true':
                                page_button = aria_next
                                logger.debug("  Found next page via aria-label")
                                break
                except Exception as e:
                    logger.debug(f"  Next button error: {e}")

            # Strategy 3b: Playwright get_by_role / get_by_text for "2" - short timeout to avoid 30s scroll hang
            SCROLL_TIMEOUT_MS = 8000
            if not page_button:
                try:
                    for loc in [
                        page.get_by_role('button', name=str(next_page_num)),
                        page.get_by_role('link', name=str(next_page_num)),
                        page.get_by_text(str(next_page_num), exact=True),
                    ]:
                        if await loc.count() > 0:
                            await loc.first.scroll_into_view_if_needed(timeout=SCROLL_TIMEOUT_MS)
                            await asyncio.sleep(0.3)
                            await loc.first.click()
                            page_button = True  # mark as handled
                            logger.debug(f"  Clicked page {next_page_num} via get_by_role/get_by_text")
                            break
                    if page_button:
                        await asyncio.sleep(human_delay() + 2)
                        await page.evaluate('window.scrollTo(0, 500)')
                        await asyncio.sleep(1)
                        current_page = next_page_num
                        continue
                except Exception as e:
                    logger.debug(f"  get_by_role/get_by_text pagination: {e}")

            if page_button:
                # Click page number button (try even if marked disabled - some sites use it for styling)
                is_disabled = await page_button.get_attribute('disabled')
                aria_disabled = await page_button.get_attribute('aria-disabled')
                classes = await page_button.get_attribute('class') or ''
                marked_disabled = is_disabled or aria_disabled == 'true' or 'disabled' in classes.lower()

                try:
                    logger.debug(f"  Clicking page {next_page_num} button..." + (" (marked disabled, trying anyway)" if marked_disabled else ""))
                    await page_button.scroll_into_view_if_needed(timeout=8000)
                    await asyncio.sleep(0.5)
                    # Use force=True if marked disabled so Playwright doesn't refuse the click
                    await page_button.click(force=marked_disabled)
                    
                    # Wait for new page to load
                    await asyncio.sleep(human_delay() + 2)  # Extra wait for page load
                    
                    # Scroll to trigger lazy loading
                    await page.evaluate('window.scrollTo(0, 500)')
                    await asyncio.sleep(1)
                    
                    current_page = next_page_num
                    logger.debug(f"  Navigated to page {current_page}")
                except Exception as e:
                    if marked_disabled:
                        logger.info(f"  No more pages available (page {next_page_num} button disabled, click failed)")
                    else:
                        logger.warning(f"  Error clicking page {next_page_num} button: {e}")
                    break
            else:
                logger.warning(f"  Could not navigate to page {next_page_num} (URL and click strategies failed); stopping with {len(all_listings)} listings from page(s) 1–{current_page}")
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
        low_mem = os.environ.get("CRON_LOW_MEMORY", "").lower() in ("1", "true", "yes")  # Render 512Mi cron
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",  # Avoid /dev/shm in Docker/low-mem
            "--disable-gpu",
            "--no-zygote",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-sync",
            "--metrics-recording-only",
            "--mute-audio",
        ]
        launch_options = {
            "headless": True,
            "args": launch_args,
        }
        if use_chrome:
            launch_options["channel"] = "chrome"
            launch_options["headless"] = False
        browser = await p.chromium.launch(**launch_options)
        
        # Smaller viewport in low-memory (e.g. Render 512Mi) to reduce rendering memory
        viewport = profile['viewport']
        if low_mem:
            viewport = {"width": 1280, "height": 720}
            logger.info("Low-memory mode: using 1280x720 viewport")
        context = await browser.new_context(
            user_agent=profile['user_agent'],
            viewport=viewport,
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
    """Save scraped data to historical_entries.json and to box_metrics_unified (DB).
    Computes boxes_added_today = max(0, today_count - yesterday_count) from yesterday's
    refresh to today's so the daily cron records how many listings were added since last run.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
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
    try:
        from app.services.historical_data import DB_TO_LEADERBOARD_UUID_MAP, get_box_30d_avg_sales
    except ImportError:
        DB_TO_LEADERBOARD_UUID_MAP = {}
        get_box_30d_avg_sales = None

    for result in results:
        box_id = result['box_id']
        boxes_within_20pct = result.get('listings_within_20pct') or 0

        if box_id not in hist:
            hist[box_id] = []

        # Added/removed from yesterday's refresh to today's (daily cron: yesterday count vs today count)
        yesterday_alc = None
        for e in hist[box_id]:
            if e.get('date') == yesterday:
                yesterday_alc = e.get('active_listings_count')
                if yesterday_alc is not None:
                    yesterday_alc = int(yesterday_alc)
                break
        delta = (boxes_within_20pct - yesterday_alc) if yesterday_alc is not None else None
        boxes_added_today = max(0, delta) if delta is not None else None
        boxes_removed_today = max(0, -delta) if delta is not None else None

        # Build scraper entry; preserve Apify sales/volume from existing today entry if present
        # (Phase 1 Apify runs first and writes sales/volume; we must not wipe them from JSON)
        existing_today = next((e for e in hist[box_id] if e.get('date') == today), None)
        entry = {
            'date': today,
            'source': 'tcgplayer_scraper',
            'floor_price_usd': result.get('floor_price'),
            'active_listings_count': boxes_within_20pct,
            'listings_within_10pct_floor': result.get('listings_within_10pct_floor'),
            'scrape_timestamp': result.get('scrape_timestamp'),
            'pages_scraped': result.get('pages_scraped'),
            'filters_applied': result.get('filters_applied'),
            'boxes_added_today': boxes_added_today,
            'boxes_removed_today': boxes_removed_today,
        }
        if existing_today:
            for key in ('boxes_sold_per_day', 'boxes_sold_today', 'unified_volume_usd', 'daily_volume_usd', 'market_price_usd', 'volume_7d'):
                if existing_today.get(key) is not None and entry.get(key) is None:
                    entry[key] = existing_today[key]

        # Remove existing entry for today (update mode)
        hist[box_id] = [e for e in hist[box_id] if e.get('date') != today]
        hist[box_id].append(entry)

        # Running 30d avg from historical data so DB stays up to date when we only write floor/listings
        boxes_sold_30d_avg = get_box_30d_avg_sales(DB_TO_LEADERBOARD_UUID_MAP.get(box_id, box_id)) if get_box_30d_avg_sales else None
        # Carry Apify sales/volume into DB if Phase 1 wrote them to JSON but DB write failed (so UI gets full data)
        boxes_sold_per_day = entry.get('boxes_sold_per_day') if existing_today else None
        unified_volume_usd = entry.get('unified_volume_usd') if existing_today else None

        # Write to DB using the ID that exists in booster_boxes (leaderboard UUID).
        # TCGPLAYER_URLS use TCGPlayer/DB UUIDs; booster_boxes.id may be leaderboard UUIDs.
        booster_box_id_for_db = DB_TO_LEADERBOARD_UUID_MAP.get(box_id, box_id)
        if upsert_daily_metrics:
            ok = upsert_daily_metrics(
                booster_box_id=booster_box_id_for_db,
                metric_date=today,
                floor_price_usd=result.get('floor_price'),
                boxes_sold_per_day=boxes_sold_per_day,
                active_listings_count=boxes_within_20pct,
                unified_volume_usd=unified_volume_usd,
                boxes_sold_30d_avg=boxes_sold_30d_avg,
                boxes_added_today=boxes_added_today,
            )
            if ok:
                logger.debug(f"DB upsert ok for {box_id}")
            else:
                logger.warning(f"DB upsert failed for {box_id} (e.g. missing FK)")

        add_remove = ""
        if boxes_added_today is not None or boxes_removed_today is not None:
            add_remove = f" | added={boxes_added_today or 0}, removed={boxes_removed_today or 0} (vs yesterday)"
        logger.info(f"Saved {box_id}: listings={boxes_within_20pct} (boxes within 20% of floor) @ ${result.get('floor_price', 0):.2f}{add_remove}")
    
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

