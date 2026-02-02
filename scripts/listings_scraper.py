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


def process_listings(raw_listings: List[Dict], market_price: float, yesterday_floor: float = None) -> Dict:
    """Full filtering pipeline. All counts are total box quantity (sum of listing quantities), not row count."""
    raw_rows = len(raw_listings)
    raw_boxes = sum(l.get('quantity', 1) for l in raw_listings)
    logger.info(f"  Raw: {raw_rows} listing rows, {raw_boxes} boxes total")
    
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
    
    # boxes_within_20pct / boxes_within_10pct are total box quantity (sum of quantities), not row count
    logger.info(f"  Floor: ${floor_price:.2f}, Within 20%: {boxes_within_20pct} boxes, Within 10%: {boxes_within_10pct} boxes (all totals = quantity)")

    # When floor dropped, also count today's listings using yesterday's higher threshold
    # so boxes_added delta is apples-to-apples (same window size)
    comparable_20pct = None
    if yesterday_floor and yesterday_floor > floor_price:
        yesterday_threshold = yesterday_floor * WITHIN_20PCT_THRESHOLD
        comparable_within = [l for l in listings if l['price'] <= yesterday_threshold]
        comparable_20pct = sum(l.get('quantity', 1) for l in comparable_within)
        logger.info(f"  Floor dropped (${yesterday_floor:.2f} -> ${floor_price:.2f}), comparable count using yesterday threshold ${yesterday_threshold:.2f}: {comparable_20pct} boxes")

    return {
        'floor_price': floor_price,
        'listings_within_20pct': boxes_within_20pct,
        'listings_within_10pct_floor': boxes_within_10pct,
        'listings_within_20pct_comparable': comparable_20pct,
        'filters_applied': {
            'japanese_removed': jp_removed,
            'suspicious_removed': suspicious_removed,
        }
    }


# ============================================================================
# SCRAPING FUNCTIONS
# ============================================================================

async def scrape_listings_page(page: Page, min_price: float, debug: bool = False) -> List[Dict]:
    """Extract listings from current page using JavaScript for reliability.

    Three-strategy approach:
      Strategy A (primary): Anchor on "Add to Cart" buttons, walk up DOM to find
        listing container, extract price/condition/seller/quantity.
      Strategy B: Use listing container class selectors (listing-item, etc.)
        with safe quantity parsing (select/option only).
      Strategy C (fallback): Find price elements, require condition-like text nearby.

    Quantity is ONLY parsed from <select>/<option> elements or aria-label
    quantity controls inside the listing card.  Never from arbitrary full text.
    """
    listings = []

    try:
        # Give page a moment to finish rendering listings
        await asyncio.sleep(1)

        # In debug mode, dump DOM diagnostics first
        if debug:
            diag = await page.evaluate('''() => {
                const allBtns = document.querySelectorAll('button, a, [role="button"]');
                const cartBtns = Array.from(allBtns).filter(el => {
                    const t = (el.textContent || '').trim().toLowerCase();
                    return t.includes('cart') || t.includes('add');
                });
                const cartTexts = cartBtns.slice(0, 15).map(el => ({
                    tag: el.tagName,
                    text: (el.textContent || '').trim().substring(0, 60),
                    classes: (el.className || '').toString().substring(0, 80),
                    ariaLabel: el.getAttribute('aria-label') || ''
                }));
                const listingEls = document.querySelectorAll('[class*="listing"], [class*="Listing"], .listing-item');
                const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"]');
                const priceTexts = Array.from(priceEls).slice(0, 10).map(el => (el.textContent || '').trim().substring(0, 50));
                return {
                    totalButtons: allBtns.length,
                    cartButtons: cartBtns.length,
                    cartTexts,
                    listingElements: listingEls.length,
                    priceElements: priceEls.length,
                    priceTexts,
                    bodyTextLength: document.body.innerText.length,
                    pageTitle: document.title
                };
            }''')
            logger.info(f"  [DEBUG] DOM diagnostics:")
            logger.info(f"    Page title: {diag.get('pageTitle', '')[:80]}")
            logger.info(f"    Total buttons/links: {diag.get('totalButtons')}")
            logger.info(f"    Cart-related buttons: {diag.get('cartButtons')}")
            logger.info(f"    Listing class elements: {diag.get('listingElements')}")
            logger.info(f"    Price class elements: {diag.get('priceElements')}")
            for ct in diag.get('cartTexts', [])[:8]:
                logger.info(f"      Cart btn: <{ct['tag']}> text={ct['text']!r} class={ct['classes']!r} aria={ct['ariaLabel']!r}")
            for pt in diag.get('priceTexts', [])[:5]:
                logger.info(f"      Price el: {pt!r}")

        # Return ALL listings (no min_price filter in JS -- Python filters after for logging)
        listings_data = await page.evaluate('''
            () => {
                const results = [];
                const seen = new Set();

                // ── helpers ──────────────────────────────────────────────
                const CONDITIONS = [
                    'near mint', 'lightly played', 'moderately played',
                    'heavily played', 'damaged', 'nm', 'lp', 'mp', 'hp',
                    'mint', 'new', 'sealed', 'factory sealed',
                    'unopened', 'verified'
                ];

                function extractPriceWithShipping(el) {
                    const text = el.innerText || '';
                    // Find the primary listing price
                    const m = text.match(/\\$([\\d,]+\\.\\d{2})/);
                    if (!m) return { price: 0, shipping: 0 };
                    const basePrice = parseFloat(m[1].replace(',', ''));

                    // Find shipping: "+ $X.XX Shipping" or "Free Shipping" or "+ Shipping: $X.XX"
                    let shipping = 0;
                    const shipMatch = text.match(/[\\+]\\s*\\$([\\d,]+\\.\\d{2})\\s*(?:shipping|ship)/i);
                    if (shipMatch) {
                        shipping = parseFloat(shipMatch[1].replace(',', ''));
                    } else if (/free\\s*shipping/i.test(text)) {
                        shipping = 0;
                    } else {
                        // Look for a second dollar amount that might be shipping
                        // (smaller amount after the main price)
                        const allPrices = text.match(/\\$([\\d,]+\\.\\d{2})/g);
                        if (allPrices && allPrices.length >= 2) {
                            const secondPrice = parseFloat(allPrices[1].replace('$', '').replace(',', ''));
                            // Only treat as shipping if it's much smaller than base price
                            if (secondPrice < basePrice * 0.15 && secondPrice > 0) {
                                shipping = secondPrice;
                            }
                        }
                    }
                    return { price: basePrice, shipping };
                }

                function extractCondition(container) {
                    for (const sel of ['[class*="condition"]', '[class*="Condition"]']) {
                        const el = container.querySelector(sel);
                        if (el) return el.innerText.trim();
                    }
                    const text = (container.innerText || '').toLowerCase();
                    for (const c of CONDITIONS) {
                        if (text.includes(c)) return c;
                    }
                    return '';
                }

                function extractSeller(container) {
                    let raw = '';
                    for (const sel of [
                        '[class*="seller"]', '[class*="Seller"]',
                        'a[href*="/seller/"]', 'a[href*="/shop/"]',
                        '[class*="sellerName"]', '[class*="seller-name"]'
                    ]) {
                        const el = container.querySelector(sel);
                        if (el) {
                            const t = el.innerText.trim();
                            if (t && t.length < 100) { raw = t; break; }
                        }
                    }
                    if (!raw) {
                        // Fallback: look for "Sold by X" text pattern
                        const m = (container.innerText || '').match(/Sold\\s+by\\s+([\\w\\s&'-]+)/i);
                        if (m) raw = m[1].trim();
                    }
                    // Normalize: strip "Sold by " prefix, trim stats
                    raw = raw.replace(/^Sold\\s+by\\s+/i, '');
                    // Strip trailing stats like "100% (1234 Sales)" after a newline
                    raw = raw.split(String.fromCharCode(10))[0].trim();
                    return raw;
                }

                function extractQuantity(container) {
                    // Strategy 1: <select> with <option> elements
                    const selects = container.querySelectorAll('select');
                    for (const sel of selects) {
                        const opts = Array.from(sel.options || []);
                        if (opts.length > 0) {
                            const lastVal = parseInt(opts[opts.length - 1].value, 10);
                            if (!isNaN(lastVal) && lastVal >= 1 && lastVal <= 999) return lastVal;
                        }
                        for (const opt of opts) {
                            const m = opt.text.match(/(\\d+)\\s*of\\s*(\\d+)/i);
                            if (m) {
                                const n = parseInt(m[2], 10);
                                if (n >= 1 && n <= 999) return n;
                            }
                        }
                    }
                    // Strategy 2: aria-label quantity
                    const qtyEls = container.querySelectorAll('[aria-label*="uantity"], [aria-label*="qty"], [aria-label*="Qty"]');
                    for (const el of qtyEls) {
                        const val = parseInt(el.value || el.textContent, 10);
                        if (!isNaN(val) && val >= 1 && val <= 999) return val;
                    }
                    // Strategy 3: input[type=number]
                    const inputs = container.querySelectorAll('input[type="number"]');
                    for (const inp of inputs) {
                        const max = parseInt(inp.getAttribute('max'), 10);
                        if (!isNaN(max) && max >= 1 && max <= 999) return max;
                    }
                    return 1;
                }

                function makeListing(container, priceInfo) {
                    const condition = extractCondition(container);
                    const seller = extractSeller(container);
                    const quantity = extractQuantity(container);
                    const title = (container.innerText || '').substring(0, 200);
                    const totalPrice = priceInfo.price + priceInfo.shipping;
                    return {
                        price: totalPrice,
                        base_price: priceInfo.price,
                        shipping: priceInfo.shipping,
                        quantity, condition, seller, title,
                        description: '', variant: ''
                    };
                }

                function dedupKey(listing) {
                    return listing.price.toFixed(2) + '|' + listing.seller.toLowerCase().trim();
                }

                function addListing(listing) {
                    if (listing.price <= 0) return;
                    const key = dedupKey(listing);
                    if (seen.has(key)) return;
                    seen.add(key);
                    results.push(listing);
                }

                // ── Strategy A: "Add to Cart" button anchors ─────────────
                const cartButtons = Array.from(document.querySelectorAll(
                    'button, a, [role="button"], [class*="addToCart"], [class*="add-to-cart"]'
                )).filter(el => {
                    const t = (el.textContent || '').trim().toLowerCase();
                    const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                    const cls = (el.className || '').toString().toLowerCase();
                    return t === 'add to cart' || t === 'add'
                        || t.includes('add to cart')
                        || ariaLabel.includes('add to cart') || ariaLabel.includes('cart')
                        || cls.includes('addtocart') || cls.includes('add-to-cart');
                });

                // Only use REAL "Add to Cart" buttons (with aria-label containing seller)
                // This avoids processing ~100 wrapper divs that also match CSS selectors
                const realCartButtons = cartButtons.filter(el => {
                    const al = (el.getAttribute('aria-label') || '').toLowerCase();
                    return al.includes('add to cart');
                });

                const _cartDebug = [];
                for (const btn of realCartButtons) {
                    const ariaLabel = btn.getAttribute('aria-label') || '';

                    // Walk up from the real button to the listing row
                    // The listing row contains: seller, condition, price, shipping, quantity, cart button
                    let container = btn.parentElement;
                    let bestContainer = null;
                    let bestPrice = null;
                    let bestQty = 1;

                    for (let i = 0; i < 8 && container; i++) {
                        const text = container.innerText || '';
                        // Stop if container is too large (spans multiple listings)
                        const dollarCount = (text.match(/\\$/g) || []).length;
                        if (dollarCount > 6) break;

                        const priceInfo = extractPriceWithShipping(container);
                        if (priceInfo.price > 0) {
                            bestContainer = container;
                            bestPrice = priceInfo;

                            // Check for quantity: "of N" text pattern (e.g. "1 of 3" or "of 3")
                            const ofMatch = text.match(/(\\d+)\\s+of\\s+(\\d+)/i);
                            if (ofMatch) {
                                const n = parseInt(ofMatch[2], 10);
                                if (n >= 1 && n <= 999) bestQty = n;
                            }
                            // Also check extractQuantity (select/input elements)
                            const eqQty = extractQuantity(container);
                            if (eqQty > bestQty) bestQty = eqQty;
                        }
                        container = container.parentElement;
                    }

                    if (bestContainer && bestPrice) {
                        const listing = makeListing(bestContainer, bestPrice);
                        listing.quantity = bestQty;
                        // Extract seller from aria-label: "Add to cart, ... from SELLER_NAME"
                        const fromMatch = ariaLabel.match(/from\\s+(.+)$/i);
                        if (fromMatch && fromMatch[1].trim()) {
                            listing.seller = fromMatch[1].trim();
                        }
                        addListing(listing);
                        _cartDebug.push({ ariaLabel: ariaLabel.substring(0, 80), status: 'ok', price: bestPrice.price, qty: bestQty });
                    } else {
                        _cartDebug.push({ ariaLabel: ariaLabel.substring(0, 80), status: 'no_price_found' });
                    }
                }

                // ── Strategy B: Listing container class selectors ────────
                if (results.length === 0) {
                    const containerSels = [
                        '.listing-item',
                        '[class*="listing-item"]',
                        '[class*="ListingItem"]',
                        '[class*="listingItem"]',
                        '[class*="product-listing"]',
                        '[data-testid*="listing"]',
                    ];
                    for (const sel of containerSels) {
                        const els = document.querySelectorAll(sel);
                        if (els.length === 0) continue;
                        for (const el of els) {
                            const text = el.innerText || '';
                            const dollarCount = (text.match(/\\$/g) || []).length;
                            if (dollarCount > 3) continue;
                            const priceInfo = extractPriceWithShipping(el);
                            if (priceInfo.price > 0) {
                                addListing(makeListing(el, priceInfo));
                            }
                        }
                        if (results.length > 0) break;
                    }
                }

                // ── Strategy C: Broad [class*="listing"] with strict filters ─
                if (results.length === 0) {
                    const els = document.querySelectorAll('[class*="listing"], [class*="Listing"]');
                    for (const el of els) {
                        const text = el.innerText || '';
                        if (text.length > 1000) continue;
                        const dollarCount = (text.match(/\\$/g) || []).length;
                        if (dollarCount > 3 || dollarCount === 0) continue;
                        const priceInfo = extractPriceWithShipping(el);
                        if (priceInfo.price > 0) {
                            addListing(makeListing(el, priceInfo));
                        }
                    }
                }

                // ── Strategy D (last resort): Price-anchored extraction ──
                if (results.length === 0) {
                    const allEls = document.querySelectorAll('*');
                    for (const el of allEls) {
                        const text = el.innerText || '';
                        if (text.length > 500 || text.length < 10) continue;
                        const priceMatches = text.match(/\\$[\\d,]+\\.\\d{2}/g);
                        if (!priceMatches || priceMatches.length !== 1) continue;
                        const priceVal = parseFloat(priceMatches[0].replace('$', '').replace(',', ''));
                        if (priceVal <= 0) continue;
                        const lowerText = text.toLowerCase();
                        const hasCondition = CONDITIONS.some(c => lowerText.includes(c));
                        if (!hasCondition) continue;
                        addListing(makeListing(el, { price: priceVal, shipping: 0 }));
                    }
                }

                return { listings: results, strategy: results.length > 0 ?
                    (cartButtons.length > 0 ? 'A:cart_buttons' : 'B/C/D:fallback') : 'none',
                    cartDebug: _cartDebug };
            }
        ''')

        strategy = listings_data.get('strategy', 'unknown') if isinstance(listings_data, dict) else 'unknown'
        raw_listings = listings_data.get('listings', []) if isinstance(listings_data, dict) else (listings_data or [])

        if debug:
            logger.info(f"  [DEBUG] Strategy used: {strategy}")
            cart_debug = listings_data.get('cartDebug', []) if isinstance(listings_data, dict) else []
            if cart_debug:
                logger.info(f"  [DEBUG] Cart button results ({len(cart_debug)} real Add to Cart buttons):")
                for cd in cart_debug:
                    status = cd.get('status', '?')
                    aria = cd.get('ariaLabel', '')[:70]
                    if status == 'ok':
                        logger.info(f"    OK price=${cd.get('price',0):.2f} qty={cd.get('qty',1)} | {aria}")
                    else:
                        logger.info(f"    MISS | {aria}")
            logger.info(f"  [DEBUG] Raw listings found (before min_price filter): {len(raw_listings)}")
            for i, l in enumerate(raw_listings[:15]):
                ship_str = f" +${l.get('shipping', 0):.2f}ship" if l.get('shipping', 0) > 0 else " (free ship)"
                logger.info(f"    [{i}] ${l.get('base_price', l['price']):.2f}{ship_str} = ${l['price']:.2f} total | qty={l['quantity']} seller={l.get('seller','')[:30]} cond={l.get('condition','')[:20]}")
            if len(raw_listings) > 15:
                logger.info(f"    ... and {len(raw_listings) - 15} more")

        # Apply min_price filter in Python (so we can log what was found vs filtered)
        if min_price > 0:
            before = len(raw_listings)
            listings = [l for l in raw_listings if l.get('price', 0) >= min_price]
            filtered_out = before - len(listings)
            if filtered_out > 0 and debug:
                logger.info(f"  [DEBUG] Filtered {filtered_out} listings below ${min_price:.2f} (kept {len(listings)})")
        else:
            listings = raw_listings

        logger.debug(f"  Extracted {len(listings)} listings from page (min ${min_price:.2f}, ≥81% of market)")

    except Exception as e:
        logger.warning(f"Error extracting listings: {e}")

    return listings


async def scrape_box(page: Page, box_id: str, url: str, market_price: float, yesterday_floor: float = None, debug: bool = False, debug_dir=None) -> Optional[Dict]:
    """Scrape all listings for a single box"""
    logger.info(f"Scraping: {url[:60]}...")
    
    all_listings = []
    seen_keys = set()  # Cross-page dedup by price+seller
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

        # Debug screenshots after navigation + Listings tab (no extra page load)
        if debug and debug_dir:
            try:
                await page.screenshot(path=str(debug_dir / f"{box_id}_01_listings_tab.png"))
                logger.info(f"  [DEBUG] Screenshot saved: {box_id}_01_listings_tab.png")
            except Exception as e:
                logger.warning(f"  [DEBUG] Screenshot error: {e}")
        
        box_start = time.time()
        BOX_TIMEOUT_SEC = 150  # Per-box max so cron doesn't hang
        prev_page_count = None  # Listings on previous page; used to detect "past last page" (e.g. EB-02 has 2 pages, page 3+ returns 1 bogus)
        
        while current_page <= max_pages:
            if (time.time() - box_start) > BOX_TIMEOUT_SEC:
                logger.warning(f"  Box timeout ({BOX_TIMEOUT_SEC}s), saving progress for {box_id}")
                break
            
            # Scrape current page (filter for boxes only - $100+)
            logger.info(f"  Scraping page {current_page}...")
            page_listings = await scrape_listings_page(page, min_price=min_box_price, debug=debug)
            
            if not page_listings:
                logger.info(f"  Page {current_page}: No box listings above ${min_box_price:.2f}, continuing to next page.")
                # Don't stop: valid listings may be on later pages (e.g. sorted by price low→high)
                # Fall through to try next page
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
                duped_this_page = 0
                for l in page_listings:
                    if threshold is not None and l['price'] > threshold:
                        logger.info(f"  Stopping pagination: hit listing at ${l['price']:.2f} (above 20% threshold ${threshold:.2f}); stopping halfway through page {current_page}.")
                        hit_above_threshold = True
                        break
                    # Cross-page dedup by price+seller
                    dedup_key = f"{l['price']:.2f}|{(l.get('seller') or '').lower().strip()}"
                    if dedup_key in seen_keys:
                        duped_this_page += 1
                        continue
                    seen_keys.add(dedup_key)
                    all_listings.append(l)
                    added_this_page += 1
                
                if hit_above_threshold:
                    break
                
                page_units = sum(l.get('quantity', 1) for l in all_listings[-added_this_page:]) if added_this_page > 0 else 0
                dedup_str = f", {duped_this_page} cross-page dupes skipped" if duped_this_page > 0 else ""
                logger.info(f"  Page {current_page}: {added_this_page} box listings, {page_units} units (≥${min_box_price}, within 20% of floor){dedup_str}")
                # Past last real page: many sites (e.g. EB-02) only have 2 pages; page 3+ returns 1–2 bogus/duplicate listings
                if current_page >= 2 and len(page_listings) <= 2:
                    logger.info(f"  Stopping pagination: page {current_page} has ≤2 listings (likely past last page).")
                    break
                # Sharp drop: previous page had many listings, this page has very few = we're past the end (e.g. EB-02: page 2 had 7, page 3 has 1)
                if current_page >= 2 and prev_page_count is not None and prev_page_count >= 3 and len(page_listings) < prev_page_count and len(page_listings) <= 2:
                    logger.info(f"  Stopping pagination: sharp drop from {prev_page_count} to {len(page_listings)} listings (past last page).")
                    break
                prev_page_count = len(page_listings)
            
            # Navigate to next page via URL (?page=N) -- this is reliable on TCGplayer
            # and avoids click-based pagination which can navigate to wrong pages (e.g. card set pages).
            next_page_num = current_page + 1
            logger.info(f"  Navigating to page {next_page_num} via URL...")

            try:
                from urllib.parse import parse_qs, urlencode, urlparse
                # Always build the pagination URL from the ORIGINAL product URL (not current page.url
                # which may have drifted). This keeps us on the product's listings.
                parsed = urlparse(url)
                base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                params = parse_qs(parsed.query) if parsed.query else {}
                params['page'] = [str(next_page_num)]
                # Preserve Language param
                if 'Language' not in params:
                    params['Language'] = ['English']
                new_url = base + '?' + urlencode(params, doseq=True)
                await page.goto(new_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                # Scroll down to trigger lazy-load, then scroll to listings area
                for scroll_y in [400, 800, 1200]:
                    await page.evaluate(f'window.scrollTo(0, {scroll_y})')
                    await asyncio.sleep(0.3)

                # Click Listings tab again (URL navigation may reset to default tab)
                try:
                    for loc in [page.locator('text=Listings').first, page.get_by_text('Listings', exact=True).first]:
                        if await loc.count() > 0:
                            await loc.click()
                            await asyncio.sleep(2)
                            break
                except Exception:
                    pass

                await asyncio.sleep(1)
                current_page = next_page_num
                logger.info(f"  Navigated to page {current_page} via URL: {new_url[:80]}...")
            except Exception as e:
                logger.warning(f"  URL pagination to page {next_page_num} failed: {e}")
                logger.info(f"  Stopping with {len(all_listings)} listings from pages 1-{current_page}")
                break
        
        # Process listings
        result = process_listings(all_listings, market_price, yesterday_floor=yesterday_floor)
        result['box_id'] = box_id
        result['url'] = url
        result['pages_scraped'] = current_page
        result['scrape_timestamp'] = datetime.now().isoformat()

        # ── Result validation warnings ──────────────────────────────
        alc = result.get('listings_within_20pct', 0)
        floor = result.get('floor_price')
        if alc and alc > 500:
            logger.warning(f"  Suspiciously high count ({alc}) for {box_id} -- possible extraction error")
        if floor and market_price and market_price > 0:
            ratio = floor / market_price
            if ratio > 3 or ratio < 0.33:
                logger.warning(f"  Floor ${floor:.2f} differs from market ${market_price:.2f} by >{3}x for {box_id}")

        if debug:
            logger.info(f"  [DEBUG] Final result for {box_id}:")
            logger.info(f"    floor_price={floor}, listings_within_20pct={alc}")
            logger.info(f"    listings_within_10pct={result.get('listings_within_10pct_floor')}")
            logger.info(f"    pages_scraped={current_page}, raw_listings_collected={len(all_listings)}")

        return result
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


async def run_scraper(debug_box_id: Optional[str] = None):
    """Main scraper entry point.

    Args:
        debug_box_id: If set, only scrape this single box in headed mode with
                      screenshots saved to logs/debug_screenshots/.
    """
    debug = debug_box_id is not None

    logger.info("=" * 60)
    if debug:
        logger.info(f"Starting TCGplayer Listings Scraper [DEBUG MODE: {debug_box_id}]")
    else:
        logger.info("Starting TCGplayer Listings Scraper")
    logger.info("=" * 60)

    # Get browser profile for this session
    profile = get_random_profile()
    logger.info(f"Browser profile: {profile['user_agent'][:50]}...")

    # In debug mode, only scrape the specified box (no noise)
    if debug:
        if debug_box_id not in TCGPLAYER_URLS:
            logger.error(f"Box ID {debug_box_id} not found in TCGPLAYER_URLS. Valid IDs:")
            for bid, burl in TCGPLAYER_URLS.items():
                logger.error(f"  {bid}: {burl[:60]}")
            return [], [debug_box_id]
        products = [(debug_box_id, TCGPLAYER_URLS[debug_box_id])]
    else:
        products = get_daily_products()

    # Load market prices and yesterday's floor prices from historical data
    market_prices = {}
    yesterday_floors = {}
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
        for box_id in TCGPLAYER_URLS.keys():
            if box_id in hist and hist[box_id]:
                latest = sorted(hist[box_id], key=lambda x: x.get('date', ''), reverse=True)[0]
                market_prices[box_id] = latest.get('market_price_usd') or latest.get('floor_price_usd', 0)
                # Find yesterday's floor for comparable boxes_added calculation
                for e in hist[box_id]:
                    if e.get('date') == yesterday and e.get('floor_price_usd'):
                        yesterday_floors[box_id] = float(e['floor_price_usd'])
                        break
    except Exception as e:
        logger.warning(f"Could not load market prices: {e}")

    results = []
    errors = []

    # Prepare debug screenshot directory
    if debug:
        debug_dir = Path('logs/debug_screenshots')
        debug_dir.mkdir(parents=True, exist_ok=True)

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
            "headless": not debug,  # headed mode for debug
            "args": launch_args,
        }
        if use_chrome or debug:
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

            # Real target - scrape data (scrape_box handles navigation + Listings tab click)
            market_price = market_prices.get(box_id, 0)
            yfloor = yesterday_floors.get(box_id)
            result = await scrape_box(page, box_id, url, market_price, yesterday_floor=yfloor, debug=debug, debug_dir=debug_dir if debug else None)

            # Debug: screenshot after scraping (may fail if browser crashed during scrape)
            if debug:
                try:
                    await page.screenshot(path=str(debug_dir / f"{box_id}_03_after_scrape.png"))
                    logger.info(f"  [DEBUG] Screenshot saved: {box_id}_03_after_scrape.png")
                except Exception as e:
                    logger.warning(f"  [DEBUG] Could not take after-scrape screenshot: {e}")

            if result:
                results.append(result)
            else:
                errors.append(box_id)

            await asyncio.sleep(human_delay())

        await browser.close()

    # Save results
    logger.info("=" * 60)
    logger.info(f"Scraping complete: {len(results)} success, {len(errors)} errors")

    if debug and results:
        # In debug mode, print a full summary instead of saving
        for r in results:
            logger.info("=" * 60)
            logger.info(f"[DEBUG] RESULT for {r['box_id']}:")
            logger.info(f"  floor_price:              ${r.get('floor_price') or 0:.2f}")
            logger.info(f"  listings_within_20pct:    {r.get('listings_within_20pct', 0)}")
            logger.info(f"  listings_within_10pct:    {r.get('listings_within_10pct_floor', 0)}")
            logger.info(f"  pages_scraped:            {r.get('pages_scraped', 0)}")
            logger.info(f"  filters_applied:          {r.get('filters_applied', {})}")
            logger.info(f"  scrape_timestamp:         {r.get('scrape_timestamp')}")
            logger.info(f"  Screenshots in: logs/debug_screenshots/")
        logger.info("=" * 60)
        logger.info("[DEBUG] Skipping save_results() in debug mode.")
    elif results:
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
        comparable_20pct = result.get('listings_within_20pct_comparable')  # Only set when floor dropped

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

        # Guard: if yesterday's count looks like bad data (>100), don't compute delta
        # This prevents the first correct run from showing a huge negative delta from old inflated data
        if yesterday_alc is not None and yesterday_alc > 100:
            logger.warning(f"Yesterday's count ({yesterday_alc}) for {box_id} looks inflated, skipping delta")
            boxes_added_today = None
            boxes_removed_today = None
        else:
            # When floor dropped, use the comparable count (today's listings counted against
            # yesterday's higher 20% threshold) so the delta is apples-to-apples.
            # When floor rose or stayed same, use today's normal 20% count.
            count_for_delta = comparable_20pct if comparable_20pct is not None else boxes_within_20pct
            delta = (count_for_delta - yesterday_alc) if yesterday_alc is not None else None
            boxes_added_today = delta
            boxes_removed_today = max(0, -delta) if delta is not None else None
            if comparable_20pct is not None and yesterday_alc is not None:
                logger.info(f"  Floor dropped for {box_id}: using comparable count {comparable_20pct} (vs today's {boxes_within_20pct}) for delta against yesterday's {yesterday_alc}")

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
            for key in ('boxes_sold_per_day', 'boxes_sold_today', 'bucket_quantity_sold', 'daily_volume_usd', 'market_price_usd', 'current_bucket_start', 'current_bucket_qty', 'delta_boxes_sold_today', 'delta_source'):
                if existing_today.get(key) is not None and entry.get(key) is None:
                    entry[key] = existing_today[key]

        # Remove existing entry for today (update mode)
        hist[box_id] = [e for e in hist[box_id] if e.get('date') != today]
        hist[box_id].append(entry)

        # Running 30d avg from historical data so DB stays up to date when we only write floor/listings
        boxes_sold_30d_avg = get_box_30d_avg_sales(box_id) if get_box_30d_avg_sales else None
        # Carry Apify sales/volume into DB if Phase 1 wrote them to JSON but DB write failed (so UI gets full data)
        boxes_sold_per_day = entry.get('boxes_sold_per_day') if existing_today else None
        unified_volume_usd = entry.get('unified_volume_usd') if existing_today else None

        # Write to DB using box_id directly (these ARE the DB UUIDs)
        if upsert_daily_metrics:
            ok = upsert_daily_metrics(
                booster_box_id=box_id,
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
        logger.info(f"Saved {box_id}: {boxes_within_20pct} boxes (total quantity within 20% of floor) @ ${result.get('floor_price', 0):.2f}{add_remove}")
    
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
    import argparse

    parser = argparse.ArgumentParser(description='TCGplayer Listings Scraper')
    parser.add_argument('--debug', type=str, metavar='BOX_ID', default=None,
                        help='Run in debug mode for a single box ID (headed browser, screenshots, verbose output)')
    args = parser.parse_args()

    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)

    # Run scraper
    asyncio.run(run_scraper(debug_box_id=args.debug))

