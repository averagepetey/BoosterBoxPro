#!/usr/bin/env python3
"""
Phase 1b: eBay Sold Listings Playwright Scraper
------------------------------------------------
Custom Playwright-based scraper to fetch eBay sold listings for 18 TCG booster boxes.
Replaces Apify eBay scraper ($54/month) with $0 operational cost.

Anti-detection architecture (6 layers):
  1. Browser Fingerprint Consistency - Coherent profiles (UA + sec-ch-ua + viewport + platform)
  2. Stealth Mode - playwright_stealth patches navigator.webdriver, plugins, etc.
  3. Human-Like Timing - Gaussian delays with distraction pauses
  4. Session Warming - Visit homepage/category before real searches
  5. Noise Searches - Intersperse decoy searches every 3-4 boxes
  6. Browser Launch Args - Disable automation flags

Run standalone:  python scripts/ebay_playwright.py [--debug <box_id>] [--dump-html]
Called by daily_refresh.py as Phase 1b replacement.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

HISTORICAL_FILE = project_root / "data" / "historical_entries.json"
DEBUG_HTML_DIR = project_root / "data" / "debug_html"

# ============================================================================
# BROWSER PROFILES (reused from ebay_scraper.py)
# ============================================================================
# Each profile is a complete, internally-consistent browser identity.
# UA string, sec-ch-ua headers, Accept-Language, platform all match.

# Per-box timeout (seconds) - prevents infinite hangs on single box
PER_BOX_TIMEOUT = 180  # 3 minutes max per box

# Helper function timeout (seconds) - for warmup, noise searches, etc.
HELPER_TIMEOUT = 45  # 45 seconds for helper operations

# Retry configuration
MAX_RETRIES_PER_BOX = 2  # Retry failed boxes up to 2 times
RETRY_DELAY_MIN = 30  # Minimum delay before retry (seconds)
RETRY_DELAY_MAX = 90  # Maximum delay before retry (seconds)

# Suspicious results threshold - 0 results for popular products may indicate soft block
MIN_EXPECTED_RESULTS = 3  # If fewer results, flag as suspicious

# Only use Chrome profiles since we're using Chromium browser.
# Firefox/Safari profiles cause fingerprint mismatch (Chromium behavior + Firefox UA = bot detection)
BROWSER_PROFILES = [
    {
        "name": "Chrome 131 macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"',
        "viewport": {"width": 1920, "height": 1080},
        "platform": "macOS",
    },
    {
        "name": "Chrome 130 macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"',
        "viewport": {"width": 1440, "height": 900},
        "platform": "macOS",
    },
    {
        "name": "Chrome 131 Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Windows",
    },
    {
        "name": "Chrome 130 Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
        "viewport": {"width": 1366, "height": 768},
        "platform": "Windows",
    },
    {
        "name": "Chrome 131 Linux",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Linux"',
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Linux",
    },
]

# ============================================================================
# HUMAN-LIKE TIMING (enhanced anti-detection)
# ============================================================================
# Key insight: Real humans have HIGH variance. Sometimes fast, sometimes slow.
# Bots are detected by being TOO consistent, even with randomness.

DELAY_MEAN = 10.0
DELAY_SIGMA = 5.0
DELAY_MIN = 1.5          # Sometimes humans click fast
DELAY_MAX = 45.0         # Sometimes humans get distracted
DISTRACTION_PAUSE_EVERY = (5, 15)   # Wider range
DISTRACTION_PAUSE_RANGE = (15, 90)  # Sometimes check phone for 90s

# Occasional "micro-pauses" (human hesitation) and "long pauses" (got distracted)
MICRO_PAUSE_CHANCE = 0.15   # 15% chance of quick 0.5-2s pause
LONG_PAUSE_CHANCE = 0.08    # 8% chance of 60-180s "went to get coffee" pause

_request_counter = 0
_next_distraction_at = random.randint(*DISTRACTION_PAUSE_EVERY)


def _gaussian_delay() -> float:
    """Return a human-like delay with realistic variance."""
    # Base gaussian
    delay = random.gauss(DELAY_MEAN, DELAY_SIGMA)
    delay = max(DELAY_MIN, min(DELAY_MAX, delay))

    # Random chance of micro-pause (human hesitation)
    if random.random() < MICRO_PAUSE_CHANCE:
        delay += random.uniform(0.5, 2.0)

    # Random chance of long pause (checking phone, etc.)
    if random.random() < LONG_PAUSE_CHANCE:
        long_pause = random.uniform(60, 180)
        logger.info(f"  Long pause: {long_pause:.0f}s (simulating distraction)")
        return long_pause

    return delay


def _maybe_distraction_pause() -> Optional[float]:
    """Check if it's time for a distraction pause. Returns pause duration or None."""
    global _request_counter, _next_distraction_at
    _request_counter += 1

    if _request_counter >= _next_distraction_at:
        _request_counter = 0
        _next_distraction_at = random.randint(*DISTRACTION_PAUSE_EVERY)
        delay = random.uniform(*DISTRACTION_PAUSE_RANGE)
        logger.info(f"  Distraction pause: {delay:.1f}s (next in ~{_next_distraction_at} requests)")
        return delay
    return None


def _random_scroll_pattern() -> List[int]:
    """Generate random scroll positions (not always 500, 1000, 1500)."""
    num_scrolls = random.randint(2, 6)
    positions = []
    current = 0
    for _ in range(num_scrolls):
        current += random.randint(200, 600)
        positions.append(current)
    return positions


# ============================================================================
# EBAY SEARCH CONFIG - 18 boxes with search queries
# ============================================================================
# Simplified queries matching user's preferred format.
# No "one piece", no "english" - rely on US-only filter + post-filtering.
# Negative keywords: -case -korean -japanese -display

# Negative keywords always included in searches
NEGATIVE_KEYWORDS = "-case -korean -japanese -display"

# Optional prefixes to randomly add (makes searches look more human)
OPTIONAL_PREFIXES = ["one piece", "one piece tcg", "bandai", ""]

# Optional suffixes to randomly add
OPTIONAL_SUFFIXES = ["english", "sealed", "new", ""]


def _generate_random_query(set_code: str, set_name_words: List[str], variant: str = "") -> str:
    """
    Generate a randomized search query that looks human but returns same results.

    Always includes: booster box + negative keywords
    Randomizes: word order, optional prefixes/suffixes
    """
    # Core components
    components = [set_code] + set_name_words
    if variant:
        components.append(variant)

    # Shuffle the core components
    random.shuffle(components)

    # Maybe add a prefix (50% chance)
    prefix = random.choice(OPTIONAL_PREFIXES) if random.random() > 0.5 else ""

    # Maybe add a suffix (30% chance)
    suffix = random.choice(OPTIONAL_SUFFIXES) if random.random() > 0.7 else ""

    # Build query: [prefix] [shuffled components] booster box [suffix] [negative keywords]
    parts = []
    if prefix:
        parts.append(prefix)
    parts.extend(components)
    parts.append("booster box")
    if suffix:
        parts.append(suffix)

    query = " ".join(parts) + " " + NEGATIVE_KEYWORDS
    return query


EBAY_SEARCH_CONFIG: Dict[str, Dict[str, Any]] = {
    # NOTE: max_price should be ~150% of typical market price to catch all valid sales
    # min_price in URL is just to filter junk; actual floor uses MIN_PRICE_RATIO (75%)
    # "query_parts" used by _generate_random_query for randomized searches
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {
        "name": "OP-01 Romance Dawn (Blue)",
        "set_code": "op-01",
        "set_name_words": ["romance", "dawn"],
        "variant": "blue",
        "min_price": 100,
        "max_price": 8000,
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {
        "name": "OP-01 Romance Dawn (White)",
        "set_code": "op-01",
        "set_name_words": ["romance", "dawn"],
        "variant": "white",
        "min_price": 100,
        "max_price": 2500,
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {
        "name": "OP-02 Paramount War",
        "set_code": "op-02",
        "set_name_words": ["paramount", "war"],
        "variant": "",
        "min_price": 50,
        "max_price": 800,
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {
        "name": "OP-03 Pillars of Strength",
        "set_code": "op-03",
        "set_name_words": ["pillars", "of", "strength"],
        "variant": "",
        "min_price": 100,
        "max_price": 1200,
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {
        "name": "OP-04 Kingdoms of Intrigue",
        "set_code": "op-04",
        "set_name_words": ["kingdoms", "of", "intrigue"],
        "variant": "",
        "min_price": 75,
        "max_price": 900,
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {
        "name": "OP-05 Awakening of the New Era",
        "set_code": "op-05",
        "set_name_words": ["awakening", "of", "the", "new", "era"],
        "variant": "",
        "min_price": 150,
        "max_price": 1600,
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {
        "name": "OP-06 Wings of the Captain",
        "set_code": "op-06",
        "set_name_words": ["wings", "of", "the", "captain"],
        "variant": "",
        "min_price": 50,
        "max_price": 600,
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {
        "name": "OP-07 500 Years in the Future",
        "set_code": "op-07",
        "set_name_words": ["500", "years", "in", "the", "future"],
        "variant": "",
        "min_price": 50,
        "max_price": 500,
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {
        "name": "OP-08 Two Legends",
        "set_code": "op-08",
        "set_name_words": ["two", "legends"],
        "variant": "",
        "min_price": 50,
        "max_price": 400,
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {
        "name": "OP-09 Emperors in the New World",
        "set_code": "op-09",
        "set_name_words": ["emperors", "in", "the", "new", "world"],
        "variant": "",
        "min_price": 100,
        "max_price": 1000,
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {
        "name": "OP-10 Royal Blood",
        "set_code": "op-10",
        "set_name_words": ["royal", "blood"],
        "variant": "",
        "min_price": 50,
        "max_price": 400,
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {
        "name": "OP-11 A Fist of Divine Speed",
        "set_code": "op-11",
        "set_name_words": ["fist", "of", "divine", "speed"],
        "variant": "",
        "min_price": 75,
        "max_price": 700,
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {
        "name": "OP-12 Legacy of the Master",
        "set_code": "op-12",
        "set_name_words": ["legacy", "of", "the", "master"],
        "variant": "",
        "min_price": 50,
        "max_price": 400,
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {
        "name": "OP-13 Carrying on His Will",
        "set_code": "op-13",
        "set_name_words": ["carrying", "on", "his", "will"],
        "variant": "",
        "min_price": 150,
        "max_price": 1200,
    },
    "3b17b708-b35b-4008-971e-240ade7afc9c": {
        "name": "EB-01 Memorial Collection",
        "set_code": "eb-01",
        "set_name_words": ["memorial", "collection"],
        "variant": "",
        "min_price": 150,
        "max_price": 1400,
    },
    "7509a855-f6da-445e-b445-130824d81d04": {
        "name": "EB-02 Anime 25th Collection",
        "set_code": "eb-02",
        "set_name_words": ["anime", "25th", "collection"],
        "variant": "",
        "min_price": 100,
        "max_price": 900,
    },
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {
        "name": "PRB-01 Premium Booster",
        "set_code": "prb-01",
        "set_name_words": ["premium", "booster"],
        "variant": "",
        "min_price": 150,
        "max_price": 1500,
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {
        "name": "PRB-02 Premium Booster Vol. 2",
        "set_code": "prb-02",
        "set_name_words": ["premium", "booster", "vol", "2"],
        "variant": "",
        "min_price": 75,
        "max_price": 600,
    },
}

# Noise search queries - DIVERSE categories to look like a real browsing session
# Mix of collectibles (related) + completely unrelated items (electronics, home, fashion)
NOISE_QUERIES = [
    # Collectibles (related-ish)
    "vintage baseball cards",
    "pokemon plush toy",
    "magic the gathering deck",
    "funko pop vinyl",
    # Electronics (unrelated)
    "iphone 15 case",
    "wireless earbuds bluetooth",
    "laptop stand aluminum",
    "usb c hub",
    "mechanical keyboard rgb",
    # Home/Fashion (very unrelated - breaks the pattern)
    "nike air max shoes",
    "coffee maker machine",
    "backpack travel",
    "watch band replacement",
    "sunglasses polarized",
    # Random trending
    "vintage t shirt",
    "vinyl records classic rock",
    "camping tent 2 person",
]

# Categories to browse during session warming (randomized)
WARMUP_CATEGORIES = [
    "https://www.ebay.com/b/Collectibles/1",
    "https://www.ebay.com/b/Electronics/bn_7000259124",
    "https://www.ebay.com/b/Toys-Hobbies/220",
    "https://www.ebay.com/b/Sports-Mem-Cards-Fan-Shop/64482",
    "https://www.ebay.com/b/Video-Games-Consoles/1249",
    "https://www.ebay.com/b/Clothing-Shoes-Accessories/11450",
    "https://www.ebay.com/b/Home-Garden/11700",
]

# ============================================================================
# TITLE EXCLUSIONS AND FILTERS (reused from ebay_scraper.py)
# ============================================================================
TITLE_EXCLUSIONS = [
    "japanese", "jp", "single", "card lot", "bundle",
    "damaged", "opened", "resealed", "display",
    "playmat", "sleeve", "deck box", "promo",
    "empty", "no cards", "custom", "repack",
    "check description", "check dis", "korean", "chinese",
    "thai", "taiwan", "case",  # case = wholesale multi-box
    "booster pack",  # single packs, not boxes (but "24 packs" in box titles is OK)
    "loose pack", "single pack",
    # Live breaks - someone opens box on stream, not a sealed box sale
    "live break", "box break", "open live", "live open",
    "break live", "personal break", "random break", "spot break",
]

# Country/region exclusions - filter non-US sellers
COUNTRY_EXCLUSIONS = [
    "uk", "united kingdom", "europe", "european", "eu version",
    "australia", "australian", "canada", "canadian",
    "germany", "german", "france", "french", "italy", "italian",
    "spain", "spanish", "netherlands", "dutch", "mexico", "mexican",
    "asia", "asian",
]

# Price floor: 75% of TCGplayer market price
MIN_PRICE_RATIO = 0.75


def _extract_quantity(title: str) -> int:
    """
    Extract multi-box quantity from listing title.
    Detects: "lot of 2", "2x", "x2", "2 boxes", "set of 2", "bundle of 2"
    Returns 1 if no multi-box pattern found. Capped at 6.
    """
    t = title.lower()

    # Pattern 1: "lot of N", "set of N", "bundle of N"
    m = re.search(r'(?:lot|set|bundle)\s+of\s+(\d+)', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 2: "Nx" multiplier (e.g., "2x booster box")
    m = re.search(r'(?:^|\s)(\d+)\s*x\s+', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 3: "xN" suffix (e.g., "booster box x2")
    m = re.search(r'\bx\s*(\d+)(?:\s|$)', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 4: "N boxes" or "N booster boxes"
    m = re.search(r'(?:^|\s)(\d+)\s+(?:booster\s+)?box(?:es)?(?:\s+lot)?', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    return 1

# Stealth browser args
STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-infobars",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-dev-shm-usage",
    "--no-sandbox",
]


# ============================================================================
# HELPERS
# ============================================================================

def _parse_price(price_str: str) -> Optional[float]:
    """Parse '$123.45' or '$123.45 to $150.00' -> float (lower bound)."""
    if not price_str:
        return None
    # Handle price ranges - take lower bound
    match = re.search(r'\$([0-9,]+\.?\d*)', price_str.replace(',', ''))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _parse_end_date(date_str: str, reference_date: datetime) -> Optional[str]:
    """
    Parse eBay date formats to ISO (YYYY-MM-DD).

    Handles:
    - "Sold Jan 15, 2026"
    - "Sold yesterday"
    - "Sold 2d ago"
    - "Jan 15, 2026"
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Remove "Sold " prefix and normalize whitespace
    date_str = re.sub(r'^Sold\s+', '', date_str, flags=re.IGNORECASE)
    date_str = re.sub(r'\s+', ' ', date_str).strip()  # Normalize multiple spaces

    # Handle relative dates
    if date_str.lower() == "yesterday":
        return (reference_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # "2d ago", "3 days ago"
    match = re.match(r'(\d+)\s*d(?:ays?)?\s*ago', date_str, re.IGNORECASE)
    if match:
        days_ago = int(match.group(1))
        return (reference_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    # Standard date formats
    for fmt in (
        "%b %d, %Y",     # Jan 15, 2026
        "%b %-d, %Y",    # Jan 3, 2026 (no leading zero) - may not work on all systems
        "%B %d, %Y",     # January 15, 2026
        "%m/%d/%Y",      # 01/15/2026
        "%Y-%m-%d",      # 2026-01-15
        "%d %b %Y",      # 15 Jan 2026
    ):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def _is_excluded_title(title: str) -> bool:
    """Check if title contains exclusion keywords."""
    title_lower = title.lower()
    return any(excl in title_lower for excl in TITLE_EXCLUSIONS)


def _is_non_us_listing(title: str) -> bool:
    """Check if title indicates non-US seller/region."""
    title_lower = title.lower()
    # Check for country exclusions
    for excl in COUNTRY_EXCLUSIONS:
        if excl in title_lower:
            # Exception: "case fresh" is fine (not "case")
            if excl == "uk" and "uk" not in title_lower.split():
                continue  # "uk" must be standalone word
            return True
    return False


def _humanize_query(query: str) -> str:
    """
    Randomly vary the query structure to avoid fingerprinting.
    - Sometimes remove some negative keywords
    - Sometimes reorder words
    - Makes query pattern less robotic
    """
    # 30% chance to simplify query (remove some negatives)
    if random.random() < 0.3:
        # Remove 1-2 negative keywords randomly
        negatives = ["-case", "-korean", "-japanese", "-display"]
        keep_negatives = random.sample(negatives, random.randint(1, 3))
        for neg in negatives:
            if neg not in keep_negatives:
                query = query.replace(f" {neg}", "")

    # 20% chance to add "sealed" (common human search term)
    if random.random() < 0.2 and "sealed" not in query.lower():
        query = query.replace("booster box", "booster box sealed")

    return query


def _build_ebay_url(query: str, min_price: Optional[float] = None, humanize: bool = True) -> str:
    """
    Build eBay sold listings URL.

    Parameters:
      - LH_Sold=1 — sold items only
      - LH_Complete=1 — completed listings
      - _sop=13 — sort by end date (newest first)
      - _udlo — minimum price filter
      - LH_PrefLoc=1 — US sellers only (cleaner data)
    """
    if humanize:
        query = _humanize_query(query)

    base = "https://www.ebay.com/sch/i.html"
    encoded_query = quote_plus(query)
    url = f"{base}?_nkw={encoded_query}&LH_Sold=1&LH_Complete=1&_sop=13&LH_PrefLoc=1"

    if min_price is not None and min_price > 0:
        url += f"&_udlo={min_price:.2f}"

    return url


# ============================================================================
# PLAYWRIGHT SCRAPER
# ============================================================================

async def _extract_sold_items(page) -> List[Dict[str, Any]]:
    """Extract sold items from eBay search results page via JS evaluation.

    Supports both old (.s-item) and new (.s-card) eBay HTML structures.
    """
    items = await page.evaluate('''() => {
        const results = [];

        // Try NEW structure first (.s-card) - eBay's 2024+ layout
        let items = document.querySelectorAll('.s-card[data-listingid]');

        if (items.length > 0) {
            // NEW STRUCTURE: .s-card elements
            for (const item of items) {
                try {
                    // Extract title
                    const titleEl = item.querySelector('.s-card__title');
                    const title = titleEl?.textContent?.trim() || '';
                    if (!title || title.toLowerCase().includes('shop on ebay')) continue;

                    // Extract item ID from data attribute or link
                    let itemId = item.getAttribute('data-listingid');
                    if (!itemId) {
                        const link = item.querySelector('a.s-card__link');
                        const url = link?.href || '';
                        const match = url.match(/itm\\/([0-9]+)/);
                        itemId = match ? match[1] : null;
                    }

                    // Extract price
                    const priceEl = item.querySelector('.s-card__price');
                    const priceText = priceEl?.textContent?.trim() || '';

                    // Extract end date (sold date) - look in caption span.positive
                    let dateText = '';
                    // Primary: .s-card__caption contains "Sold  Feb 3, 2026"
                    const captionEl = item.querySelector('.s-card__caption .positive, .s-card__caption span');
                    if (captionEl) {
                        dateText = captionEl.textContent?.trim() || '';
                    }
                    // Fallback: check subtitle
                    if (!dateText) {
                        const subtitleEl = item.querySelector('.s-card__subtitle');
                        if (subtitleEl) {
                            dateText = subtitleEl.textContent?.trim() || '';
                        }
                    }
                    // Fallback: check attribute rows
                    if (!dateText) {
                        const attrRows = item.querySelectorAll('.s-card__attribute-row');
                        for (const row of attrRows) {
                            const text = row.textContent || '';
                            if (text.toLowerCase().includes('sold')) {
                                dateText = text.trim();
                                break;
                            }
                        }
                    }

                    // Extract URL
                    const linkEl = item.querySelector('a.s-card__link');
                    const url = linkEl?.href || '';

                    if (title && itemId) {
                        results.push({
                            item_id: itemId,
                            title: title,
                            price_text: priceText,
                            date_text: dateText,
                            shipping_text: '',
                            url: url
                        });
                    }
                } catch (e) {
                    // Skip malformed items
                }
            }
        } else {
            // OLD STRUCTURE: .s-item elements (fallback)
            items = document.querySelectorAll('.s-item');

            for (const item of items) {
                try {
                    const title = item.querySelector('.s-item__title')?.textContent?.trim() || '';
                    if (title.toLowerCase().includes('shop on ebay')) continue;

                    const link = item.querySelector('a.s-item__link');
                    const url = link?.href || '';
                    const itemIdMatch = url.match(/itm\\/([0-9]+)/);
                    const itemId = itemIdMatch ? itemIdMatch[1] : null;

                    const priceEl = item.querySelector('.s-item__price');
                    const priceText = priceEl?.textContent?.trim() || '';

                    const dateEl = item.querySelector('.s-item__ended-date, .s-item__endedDate, .POSITIVE');
                    const dateText = dateEl?.textContent?.trim() || '';

                    const shippingEl = item.querySelector('.s-item__shipping, .s-item__freeXDays');
                    const shippingText = shippingEl?.textContent?.trim() || '';

                    if (title && itemId) {
                        results.push({
                            item_id: itemId,
                            title: title,
                            price_text: priceText,
                            date_text: dateText,
                            shipping_text: shippingText,
                            url: url
                        });
                    }
                } catch (e) {
                    // Skip malformed items
                }
            }
        }

        return results;
    }''')

    return items or []


async def _simulate_mouse_movement(page) -> None:
    """Simulate human-like mouse movement."""
    try:
        # Get viewport size
        viewport = page.viewport_size
        if not viewport:
            return

        # Random movements across the page
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.4))
    except Exception:
        pass  # Mouse simulation is nice-to-have, not critical


async def _click_random_item(page) -> None:
    """Click on a random search result item (then go back). Simulates real browsing."""
    try:
        # Find clickable item titles
        items = await page.query_selector_all('.s-item__title')
        if items and len(items) > 2:
            # Pick a random item (skip first which is often an ad)
            idx = random.randint(1, min(len(items) - 1, 8))
            await items[idx].click()
            await asyncio.sleep(random.uniform(2.0, 6.0))

            # Scroll on the item page
            await page.evaluate(f"window.scrollTo(0, {random.randint(300, 800)})")
            await asyncio.sleep(random.uniform(1.0, 3.0))

            # Go back
            await page.go_back(wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(1.0, 2.0))
    except Exception:
        pass  # Non-critical - just adds realism


async def _warm_session(page, profile: Dict[str, Any]) -> None:
    """
    Session warming: build a realistic browsing history before scraping.
    - Visit homepage
    - Browse 1-2 random categories
    - Maybe click on an item
    - Random scroll patterns
    """
    logger.info(f"  Session warming (profile: {profile['name']})")

    # 1. eBay homepage with realistic wait
    await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
    await _simulate_mouse_movement(page)
    await asyncio.sleep(random.uniform(2.0, 8.0))

    # 2. Scroll on homepage
    for scroll_y in _random_scroll_pattern()[:3]:
        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
        await asyncio.sleep(random.uniform(0.3, 1.2))

    # 3. Visit 1-2 random categories (not always Collectibles)
    num_categories = random.randint(1, 2)
    for cat_url in random.sample(WARMUP_CATEGORIES, num_categories):
        await asyncio.sleep(random.uniform(2.0, 5.0))
        await page.goto(cat_url, wait_until="domcontentloaded", timeout=30000)
        await _simulate_mouse_movement(page)
        await asyncio.sleep(random.uniform(3.0, 8.0))

        # Scroll randomly
        for scroll_y in _random_scroll_pattern()[:random.randint(2, 4)]:
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(random.uniform(0.4, 1.5))

    # 4. Maybe do a warmup search (50% chance)
    if random.random() < 0.5:
        warmup_query = random.choice(NOISE_QUERIES)
        warmup_url = _build_ebay_url(warmup_query)
        await page.goto(warmup_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(random.uniform(2.0, 5.0))

        # Maybe click on an item (30% chance)
        if random.random() < 0.3:
            await _click_random_item(page)

    logger.info("  Session warming complete")


async def _do_noise_search(page) -> None:
    """
    Perform a noise/decoy search with realistic engagement.
    - Navigate to search
    - Scroll through results
    - Maybe click on an item (40% chance)
    - Spend realistic time browsing
    """
    query = random.choice(NOISE_QUERIES)

    # Sometimes search for sold items, sometimes active listings (varies pattern)
    if random.random() < 0.3:
        url = _build_ebay_url(query)  # Active listings (no sold filter)
        url = url.replace("&LH_Sold=1&LH_Complete=1", "")
    else:
        url = _build_ebay_url(query)

    logger.info(f"  Noise search: {query}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await _simulate_mouse_movement(page)
    await asyncio.sleep(random.uniform(2.0, 6.0))

    # Scroll with random pattern
    for scroll_y in _random_scroll_pattern():
        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
        await asyncio.sleep(random.uniform(0.3, 1.0))

    # Click on an item 40% of the time (real users click)
    if random.random() < 0.4:
        await _click_random_item(page)

    await asyncio.sleep(random.uniform(1.0, 3.0))


async def _detect_captcha_or_block(page) -> tuple[bool, str]:
    """
    Check if we hit a CAPTCHA or block page.

    Returns:
        (is_blocked, reason) - Tuple of block status and reason string
    """
    url = page.url.lower()
    if "captcha" in url:
        return True, "URL contains captcha"
    if "blocked" in url:
        return True, "URL contains blocked"
    if "signin" in url and "ebay" in url:
        return True, "Redirected to sign-in page"

    try:
        content = await asyncio.wait_for(page.content(), timeout=10)
    except asyncio.TimeoutError:
        return True, "Timeout getting page content"

    content_lower = content.lower()

    # CAPTCHA indicators
    captcha_indicators = [
        ("verify you", "CAPTCHA - verify you"),
        ("are you a human", "CAPTCHA - are you human"),
        ("prove you're not a robot", "CAPTCHA - robot check"),
        ("unusual traffic", "CAPTCHA - unusual traffic"),
        ("automated access", "Blocked - automated access detected"),
        ("access denied", "Blocked - access denied"),
        ("please enable javascript", "JS disabled detection"),
        ("browser check", "Blocked - browser check"),
        ("security check", "Blocked - security check"),
        ("too many requests", "Rate limited - too many requests"),
        ("try again later", "Rate limited - try again later"),
    ]

    for indicator, reason in captcha_indicators:
        if indicator in content_lower:
            return True, reason

    # Check for empty/minimal page (soft block shows blank page)
    # Real eBay pages have >10KB of HTML
    if len(content) < 5000 and "ebay" in content_lower:
        return True, "Suspiciously small page (possible soft block)"

    # Check for missing search results structure (eBay always has this on real pages)
    if "srp-results" not in content_lower and "s-item" not in content_lower and "s-card" not in content_lower:
        # Could be a block page that renders nothing useful
        if "ebay" in content_lower:
            return True, "Missing search results structure"

    return False, ""


async def run_ebay_scraper(
    debug_box_id: Optional[str] = None,
    dump_html: bool = False,
    skip_startup_jitter: bool = False,
    proxy_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scrape eBay sold listings via Playwright for all 18 boxes.

    Anti-detection layers:
      1. Coherent browser profiles
      2. playwright_stealth patches
      3. Gaussian delays + distraction pauses
      4. Session warming
      5. Noise searches every 2-4 boxes
      6. Stealth browser args
      7. Session batching (restart browser every 4-7 boxes)
      8. Startup jitter (0-15 min random delay)

    Args:
        debug_box_id: If set, only scrape this box.
        dump_html: If True, save raw HTML to debug_html/.
        skip_startup_jitter: If True, skip the random startup delay (for testing).

    Returns:
        Summary dict: {results: int, errors: list, date: str}
    """
    from playwright.async_api import async_playwright

    # STARTUP JITTER: Random delay 0-15 minutes before starting
    # Combined with daily_refresh.py's 0-45 min jitter = 0-60 min total variance
    if not debug_box_id and not skip_startup_jitter:
        startup_jitter = random.uniform(0, 15 * 60)  # 0-15 minutes
        if startup_jitter > 60:
            logger.info(f"Startup jitter: waiting {startup_jitter/60:.1f} minutes before starting...")
            await asyncio.sleep(startup_jitter)
        else:
            await asyncio.sleep(startup_jitter)

    try:
        from playwright_stealth import Stealth
        stealth = Stealth()
        use_stealth = True
    except ImportError:
        logger.warning("playwright_stealth not installed, running without stealth")
        use_stealth = False

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    logger.info(f"Phase 1b (Playwright): eBay scraper starting for {today_str}")

    # Load historical entries
    try:
        with open(HISTORICAL_FILE, "r") as f:
            hist = json.load(f)
    except FileNotFoundError:
        hist = {}

    # Determine which boxes to scrape
    if debug_box_id:
        if debug_box_id not in EBAY_SEARCH_CONFIG:
            logger.error(f"Box {debug_box_id} not in EBAY_SEARCH_CONFIG")
            return {"results": 0, "errors": [f"Unknown box: {debug_box_id}"], "date": today_str}
        box_items = [(debug_box_id, EBAY_SEARCH_CONFIG[debug_box_id])]
    else:
        # Randomize box order (anti-detection)
        box_items = list(EBAY_SEARCH_CONFIG.items())
        random.shuffle(box_items)
        logger.info(f"Shuffled box order for this run ({len(box_items)} boxes)")

    results_count = 0
    errors = []
    noise_counter = 0
    noise_interval = random.randint(2, 4)  # Do noise search every 2-4 boxes

    # Track retry state for failed boxes
    retry_queue: List[tuple[str, Dict[str, Any], int]] = []  # (box_id, config, attempt_num)

    # SESSION BATCHING: Don't do all 18 boxes in one browser session
    # Split into batches of 4-7 boxes, restart browser between batches
    # This spreads the "one piece booster box" searches across multiple "sessions"
    BATCH_SIZE_MIN = 4
    BATCH_SIZE_MAX = 7
    boxes_in_current_session = 0
    max_boxes_this_session = random.randint(BATCH_SIZE_MIN, BATCH_SIZE_MAX)

    # Pick browser profile for this session
    profile = random.choice(BROWSER_PROFILES)

    # PROXY SUPPORT: Check env var or parameter
    # Format: "http://user:pass@host:port" or "http://host:port"
    import os
    proxy_url = proxy_url or os.environ.get("EBAY_PROXY_URL")
    if proxy_url:
        logger.info(f"  Using proxy: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")

    async with async_playwright() as p:
        # Browser launch options
        launch_options = {
            "headless": True,
            "args": STEALTH_ARGS,
        }
        if proxy_url:
            launch_options["proxy"] = {"server": proxy_url}

        browser = await p.chromium.launch(**launch_options)

        # Build comprehensive headers that match a real browser
        extra_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        # Add Chrome-specific headers (Chrome profiles only)
        if profile.get("sec_ch_ua"):
            extra_headers["sec-ch-ua"] = profile["sec_ch_ua"]
            extra_headers["sec-ch-ua-mobile"] = profile.get("sec_ch_ua_mobile", "?0")
            extra_headers["sec-ch-ua-platform"] = profile.get("sec_ch_ua_platform", '"Windows"')

        # Set timezone to match profile platform
        timezone_id = "America/New_York"  # Default US timezone
        if "Linux" in profile.get("name", ""):
            timezone_id = random.choice(["America/Los_Angeles", "America/Chicago", "America/New_York"])
        elif "macOS" in profile.get("name", ""):
            timezone_id = random.choice(["America/Los_Angeles", "America/New_York"])

        context = await browser.new_context(
            user_agent=profile["user_agent"],
            viewport=profile["viewport"],
            locale="en-US",
            timezone_id=timezone_id,
            extra_http_headers=extra_headers,
        )
        # Set default timeout for ALL operations (prevents infinite hangs)
        context.set_default_timeout(60000)  # 60 seconds

        page = await context.new_page()

        # Apply stealth patches
        if use_stealth:
            await stealth.apply_stealth_async(page)

        try:
            # Session warming (with timeout protection)
            try:
                await asyncio.wait_for(_warm_session(page, profile), timeout=HELPER_TIMEOUT * 2)
            except asyncio.TimeoutError:
                logger.warning(f"  Session warming timed out, continuing anyway")

            for box_idx, (box_id, config) in enumerate(box_items):
                name = config["name"]
                query = _generate_random_query(config["set_code"], config["set_name_words"], config.get("variant", ""))
                min_price_config = config["min_price"]
                max_price_config = config["max_price"]

                # Get TCGplayer market price for dynamic price floor
                tcg_market_price = None
                box_entries = hist.get(box_id, [])
                if box_entries:
                    for entry in sorted(box_entries, key=lambda e: e.get("date", ""), reverse=True):
                        if entry.get("market_price_usd"):
                            tcg_market_price = entry["market_price_usd"]
                            break
                        elif entry.get("floor_price_usd"):
                            tcg_market_price = entry["floor_price_usd"]
                            break

                # Dynamic min price: 75% of TCGplayer market price
                if tcg_market_price and tcg_market_price > 0:
                    min_price = max(tcg_market_price * MIN_PRICE_RATIO, min_price_config)
                else:
                    min_price = min_price_config

                logger.info(f"Scraping {name} (min_price=${min_price:.2f})")
                logger.debug(f"  Randomized query: {query}")

                # Check for distraction pause
                pause = _maybe_distraction_pause()
                if pause:
                    await asyncio.sleep(pause)

                # Human-like delay
                delay = _gaussian_delay()
                logger.debug(f"  Waiting {delay:.1f}s before search")
                await asyncio.sleep(delay)

                # Maybe do noise search (with timeout protection)
                noise_counter += 1
                if noise_counter >= noise_interval:
                    noise_counter = 0
                    noise_interval = random.randint(3, 4)
                    try:
                        await asyncio.wait_for(_do_noise_search(page), timeout=HELPER_TIMEOUT)
                    except asyncio.TimeoutError:
                        logger.warning(f"  Noise search timed out, continuing")
                    await asyncio.sleep(_gaussian_delay())

                # Track start time for per-box timeout
                box_start_time = asyncio.get_event_loop().time()

                def _check_box_timeout():
                    """Raise TimeoutError if per-box timeout exceeded."""
                    elapsed = asyncio.get_event_loop().time() - box_start_time
                    if elapsed > PER_BOX_TIMEOUT:
                        raise asyncio.TimeoutError(f"Box processing exceeded {PER_BOX_TIMEOUT}s")

                try:
                    # Build URL and navigate
                    url = _build_ebay_url(query, min_price)
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    _check_box_timeout()

                    # Check for CAPTCHA/block
                    is_blocked, block_reason = await _detect_captcha_or_block(page)
                    if is_blocked:
                        logger.warning(f"  CAPTCHA/block detected for {name}: {block_reason}")
                        raise Exception(f"BLOCKED: {block_reason}")

                    # Wait for actual content to load (not just DOM)
                    # eBay uses JavaScript to render results
                    try:
                        await page.wait_for_selector(
                            '.s-card[data-listingid], .s-item__title',
                            timeout=15000
                        )
                    except Exception:
                        logger.warning(f"  No results loaded for {name}, page might be blocked")
                        # Save debug HTML
                        if not dump_html:
                            DEBUG_HTML_DIR.mkdir(parents=True, exist_ok=True)
                            html = await page.content()
                            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
                            path = DEBUG_HTML_DIR / f"ebay_blocked_{safe_name}_{today_str}.html"
                            path.write_text(html)
                            logger.warning(f"    Saved debug HTML to {path}")
                        errors.append(f"{box_id}: NO_CONTENT")
                        continue

                    # Additional wait for JS to settle
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                    _check_box_timeout()

                    # Mouse movement to simulate real user
                    await _simulate_mouse_movement(page)

                    # Scroll with RANDOM pattern (not always same positions)
                    for scroll_y in _random_scroll_pattern():
                        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                        await asyncio.sleep(random.uniform(0.2, 1.2))
                    _check_box_timeout()

                    # Dump HTML if requested
                    if dump_html:
                        DEBUG_HTML_DIR.mkdir(parents=True, exist_ok=True)
                        html = await page.content()
                        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
                        path = DEBUG_HTML_DIR / f"ebay_sold_{safe_name}_{today_str}.html"
                        path.write_text(html)
                        logger.info(f"    Dumped HTML to {path}")

                    # Extract items (this is where hangs often occur)
                    raw_items = await asyncio.wait_for(
                        _extract_sold_items(page),
                        timeout=60  # 60s timeout for extraction specifically
                    )
                    logger.debug(f"    Raw items extracted: {len(raw_items)}")

                    # Filter items (before + after filtering)
                    filtered_items = []
                    excluded_counts = {"title": 0, "country": 0, "price": 0}

                    for item in raw_items:
                        title = item.get("title", "")

                        # Filter 1: Title exclusion keywords
                        if _is_excluded_title(title):
                            excluded_counts["title"] += 1
                            continue

                        # Filter 2: Non-US seller/region
                        if _is_non_us_listing(title):
                            excluded_counts["country"] += 1
                            continue

                        # Parse price
                        price = _parse_price(item.get("price_text", ""))
                        if price is None:
                            continue

                        # Handle multi-box lots (divide price by quantity)
                        quantity = _extract_quantity(title)
                        if quantity > 1:
                            price = round(price / quantity, 2)

                        # Filter 3: Price range filter (after quantity adjustment)
                        if price < min_price or price > max_price_config:
                            excluded_counts["price"] += 1
                            continue

                        # Parse date
                        sold_date = _parse_end_date(item.get("date_text", ""), today)

                        filtered_items.append({
                            "ebay_item_id": item["item_id"],
                            "title": title,
                            "sold_price_cents": int(price * 100),  # Store as cents for consistency
                            "sold_price_usd": price,
                            "sold_date": sold_date,
                            "quantity": quantity,
                            "url": item.get("url", ""),
                            "item_url": item.get("url", ""),  # Alias for DB writer
                            "sale_type": "sold",  # For DB writer
                        })

                    logger.info(f"    {len(raw_items)} raw -> {len(filtered_items)} filtered (excl: title={excluded_counts['title']}, country={excluded_counts['country']}, price={excluded_counts['price']})")

                    # Check for suspiciously empty results (possible soft block)
                    if len(filtered_items) < MIN_EXPECTED_RESULTS:
                        logger.warning(f"    {name}: Only {len(filtered_items)} results (expected >={MIN_EXPECTED_RESULTS}), queuing for retry")
                        retry_queue.append((box_id, config, 1))
                        continue

                    # Cross-day deduplication
                    prev_item_ids = set()
                    has_prev_tracking = False
                    for prev_entry in hist.get(box_id, []):
                        if prev_entry.get("date") != today_str:
                            prev_ids = prev_entry.get("_ebay_sold_item_ids", [])
                            if prev_ids:
                                has_prev_tracking = True
                                for pid in prev_ids:
                                    prev_item_ids.add(pid)

                    # Identify new sales (not seen before)
                    new_sales = [item for item in filtered_items if item["ebay_item_id"] not in prev_item_ids]
                    current_item_ids = [item["ebay_item_id"] for item in filtered_items]

                    # Expand prices by quantity (e.g., "lot of 2" at $1200 → 2× $600)
                    sold_prices = []
                    for item in filtered_items:
                        qty = item.get("quantity", 1)
                        sold_prices.extend([item["sold_price_usd"]] * qty)

                    # Total boxes sold (sum of quantities)
                    sold_box_count = sum(item.get("quantity", 1) for item in filtered_items)

                    # Today's sales (new or yesterday-dated)
                    if has_prev_tracking:
                        today_sold = new_sales
                    else:
                        yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                        today_sold = [item for item in filtered_items if item.get("sold_date") == yesterday_str]

                    today_prices = []
                    for item in today_sold:
                        qty = item.get("quantity", 1)
                        today_prices.extend([item["sold_price_usd"]] * qty)
                    today_box_count = sum(item.get("quantity", 1) for item in today_sold)

                    # Get last sold date
                    sold_dates = [item.get("sold_date") for item in filtered_items if item.get("sold_date")]
                    last_sold_date = max(sold_dates) if sold_dates else None

                    # Compute eBay fields (matching ebay_scraper.py field names exactly)
                    ebay_fields = {
                        "ebay_sold_count": sold_box_count,
                        "ebay_sold_today": today_box_count,
                        "ebay_volume_usd": round(sum(sold_prices), 2) if sold_prices else 0,
                        "ebay_daily_volume_usd": round(sum(today_prices), 2) if today_prices else 0,
                        "ebay_median_price_usd": round(statistics.median(sold_prices), 2) if sold_prices else None,
                        "ebay_avg_price_usd": round(statistics.mean(sold_prices), 2) if sold_prices else None,
                        "ebay_low_price_usd": round(min(sold_prices), 2) if sold_prices else None,
                        "ebay_high_price_usd": round(max(sold_prices), 2) if sold_prices else None,
                        "ebay_last_sold_date": last_sold_date,
                        "ebay_source": "playwright_direct",
                        "ebay_fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                        "_ebay_sold_item_ids": current_item_ids,
                        # Store today's sold items for verification (title, price, date, url)
                        "_ebay_sold_today_items": [
                            {
                                "title": item["title"],
                                "price": item["sold_price_usd"],
                                "date": item.get("sold_date"),
                                "url": item.get("url", ""),
                                "item_id": item["ebay_item_id"],
                            }
                            for item in today_sold
                        ],
                        # Store sample of all filtered items (first 10) for audit
                        "_ebay_filtered_sample": [
                            {
                                "title": item["title"],
                                "price": item["sold_price_usd"],
                                "date": item.get("sold_date"),
                                "item_id": item["ebay_item_id"],
                            }
                            for item in filtered_items[:10]
                        ],
                    }

                    # Update historical entries
                    if box_id not in hist:
                        hist[box_id] = []

                    existing_today = next(
                        (e for e in hist[box_id] if e.get("date") == today_str), None
                    )
                    if existing_today:
                        for key, val in ebay_fields.items():
                            existing_today[key] = val
                    else:
                        hist[box_id].append({"date": today_str, **ebay_fields})

                    # Write to database
                    write_ebay_to_db(box_id, today_str, ebay_fields, filtered_items)

                    results_count += 1
                    boxes_in_current_session += 1
                    logger.info(
                        f"    {name}: sold={ebay_fields['ebay_sold_count']}, "
                        f"today={ebay_fields['ebay_sold_today']}, "
                        f"median=${ebay_fields.get('ebay_median_price_usd', 'N/A')}"
                    )

                    # SESSION ROTATION: After batch size, restart browser with new profile
                    # This makes it look like different users doing searches
                    if boxes_in_current_session >= max_boxes_this_session:
                        remaining = len(box_items) - (box_idx + 1)
                        if remaining > 0:
                            logger.info(f"  Session rotation: {boxes_in_current_session} boxes done, restarting browser...")
                            await browser.close()

                            # Long pause between sessions (like different users)
                            session_break = random.uniform(30, 120)
                            logger.info(f"  Inter-session break: {session_break:.0f}s")
                            await asyncio.sleep(session_break)

                            # New profile, new browser
                            profile = random.choice(BROWSER_PROFILES)
                            launch_opts = {"headless": True, "args": STEALTH_ARGS}
                            if proxy_url:
                                launch_opts["proxy"] = {"server": proxy_url}
                            browser = await p.chromium.launch(**launch_opts)

                            # Rebuild headers for new profile
                            extra_headers = {
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.9",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Connection": "keep-alive",
                                "DNT": "1",
                                "Upgrade-Insecure-Requests": "1",
                                "Sec-Fetch-Dest": "document",
                                "Sec-Fetch-Mode": "navigate",
                                "Sec-Fetch-Site": "none",
                                "Sec-Fetch-User": "?1",
                            }
                            if profile.get("sec_ch_ua"):
                                extra_headers["sec-ch-ua"] = profile["sec_ch_ua"]
                                extra_headers["sec-ch-ua-mobile"] = profile.get("sec_ch_ua_mobile", "?0")
                                extra_headers["sec-ch-ua-platform"] = profile.get("sec_ch_ua_platform", '"Windows"')

                            timezone_id = "America/New_York"
                            if "Linux" in profile.get("name", ""):
                                timezone_id = random.choice(["America/Los_Angeles", "America/Chicago", "America/New_York"])
                            elif "macOS" in profile.get("name", ""):
                                timezone_id = random.choice(["America/Los_Angeles", "America/New_York"])

                            context = await browser.new_context(
                                user_agent=profile["user_agent"],
                                viewport=profile["viewport"],
                                locale="en-US",
                                timezone_id=timezone_id,
                                extra_http_headers=extra_headers,
                            )
                            # Set default timeout for ALL operations (prevents infinite hangs)
                            context.set_default_timeout(60000)  # 60 seconds

                            page = await context.new_page()
                            if use_stealth:
                                await stealth.apply_stealth_async(page)

                            # Warm the new session
                            await _warm_session(page, profile)

                            # Reset counters
                            boxes_in_current_session = 0
                            max_boxes_this_session = random.randint(BATCH_SIZE_MIN, BATCH_SIZE_MAX)
                            noise_counter = 0
                            noise_interval = random.randint(2, 4)

                except asyncio.TimeoutError as e:
                    error_msg = f"{name}: TIMEOUT ({e})"
                    logger.warning(f"    TIMEOUT: {name} - {e}")
                    # Queue for retry (first attempt)
                    retry_queue.append((box_id, config, 1))
                except Exception as e:
                    error_msg = f"{name}: {e}"
                    logger.warning(f"    Error: {e}")

                    # Check for rate limit
                    err_str = str(e).lower()
                    if "429" in err_str or "rate" in err_str or "blocked" in err_str:
                        logger.warning("Rate limited — backing off 5 minutes")
                        await asyncio.sleep(300)
                        # Queue for retry after backoff
                        retry_queue.append((box_id, config, 1))
                    elif "BLOCKED" in str(e):
                        # Blocked pages should be retried with different timing
                        retry_queue.append((box_id, config, 1))
                    else:
                        # Other errors - still queue for retry
                        retry_queue.append((box_id, config, 1))

            # ================================================================
            # RETRY PROCESSING: Process failed boxes with different timing
            # ================================================================
            if retry_queue and not debug_box_id:
                logger.info(f"\n  === RETRY PHASE: {len(retry_queue)} boxes to retry ===")

                # Long pause before retries (different timing pattern)
                retry_pause = random.uniform(60, 180)
                logger.info(f"  Waiting {retry_pause:.0f}s before retry phase...")
                await asyncio.sleep(retry_pause)

                # Process retry queue
                while retry_queue:
                    retry_box_id, retry_config, attempt = retry_queue.pop(0)
                    retry_name = retry_config["name"]

                    if attempt > MAX_RETRIES_PER_BOX:
                        errors.append(f"{retry_box_id}: FAILED after {MAX_RETRIES_PER_BOX} retries")
                        logger.warning(f"    {retry_name}: giving up after {MAX_RETRIES_PER_BOX} retries")
                        continue

                    logger.info(f"  RETRY {attempt}/{MAX_RETRIES_PER_BOX}: {retry_name}")

                    # Delay before retry (longer for subsequent attempts)
                    retry_delay = random.uniform(
                        RETRY_DELAY_MIN * attempt,
                        RETRY_DELAY_MAX * attempt
                    )
                    logger.info(f"    Waiting {retry_delay:.0f}s before retry...")
                    await asyncio.sleep(retry_delay)

                    try:
                        # Generate a DIFFERENT query variation for retry
                        query = _generate_random_query(
                            retry_config["set_code"],
                            retry_config["set_name_words"],
                            retry_config.get("variant", "")
                        )
                        min_price_config = retry_config["min_price"]
                        max_price_config = retry_config["max_price"]

                        # Dynamic min price
                        tcg_market_price = None
                        box_entries = hist.get(retry_box_id, [])
                        if box_entries:
                            for entry in sorted(box_entries, key=lambda e: e.get("date", ""), reverse=True):
                                if entry.get("market_price_usd"):
                                    tcg_market_price = entry["market_price_usd"]
                                    break
                        min_price = max(tcg_market_price * MIN_PRICE_RATIO, min_price_config) if tcg_market_price else min_price_config

                        url = _build_ebay_url(query, min_price)
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                        # Check for block
                        is_blocked, block_reason = await _detect_captcha_or_block(page)
                        if is_blocked:
                            raise Exception(f"BLOCKED on retry: {block_reason}")

                        # Wait for content
                        await page.wait_for_selector(
                            '.s-card[data-listingid], .s-item__title',
                            timeout=20000  # Slightly longer timeout for retries
                        )

                        await asyncio.sleep(random.uniform(2.0, 4.0))

                        # Extract items
                        raw_items = await asyncio.wait_for(
                            _extract_sold_items(page),
                            timeout=60
                        )

                        # Same filtering logic as main loop
                        filtered_items = []
                        for item in raw_items:
                            title = item.get("title", "")
                            if _is_excluded_title(title) or _is_non_us_listing(title):
                                continue
                            price = _parse_price(item.get("price_text", ""))
                            if price is None:
                                continue
                            quantity = _extract_quantity(title)
                            if quantity > 1:
                                price = round(price / quantity, 2)
                            if price < min_price or price > max_price_config:
                                continue
                            sold_date = _parse_end_date(item.get("date_text", ""), today)
                            filtered_items.append({
                                "ebay_item_id": item["item_id"],
                                "title": title,
                                "sold_price_cents": int(price * 100),
                                "sold_price_usd": price,
                                "sold_date": sold_date,
                                "quantity": quantity,
                                "url": item.get("url", ""),
                                "item_url": item.get("url", ""),
                                "sale_type": "sold",
                            })

                        # Check for suspiciously empty results
                        if len(filtered_items) < MIN_EXPECTED_RESULTS:
                            logger.warning(f"    {retry_name}: Only {len(filtered_items)} results (expected >={MIN_EXPECTED_RESULTS}), may be soft-blocked")
                            if attempt < MAX_RETRIES_PER_BOX:
                                retry_queue.append((retry_box_id, retry_config, attempt + 1))
                                continue

                        # Compute and save metrics (same as main loop)
                        sold_prices = []
                        for item in filtered_items:
                            qty = item.get("quantity", 1)
                            sold_prices.extend([item["sold_price_usd"]] * qty)
                        sold_box_count = sum(item.get("quantity", 1) for item in filtered_items)
                        current_item_ids = [item["ebay_item_id"] for item in filtered_items]

                        ebay_fields = {
                            "ebay_sold_count": sold_box_count,
                            "ebay_sold_today": 0,  # Can't determine reliably on retry
                            "ebay_volume_usd": round(sum(sold_prices), 2) if sold_prices else 0,
                            "ebay_daily_volume_usd": 0,
                            "ebay_median_price_usd": round(statistics.median(sold_prices), 2) if sold_prices else None,
                            "ebay_avg_price_usd": round(statistics.mean(sold_prices), 2) if sold_prices else None,
                            "ebay_low_price_usd": round(min(sold_prices), 2) if sold_prices else None,
                            "ebay_high_price_usd": round(max(sold_prices), 2) if sold_prices else None,
                            "ebay_source": "playwright_direct_retry",
                            "ebay_fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                            "_ebay_sold_item_ids": current_item_ids,
                        }

                        # Update historical entries
                        if retry_box_id not in hist:
                            hist[retry_box_id] = []
                        existing_today = next(
                            (e for e in hist[retry_box_id] if e.get("date") == today_str), None
                        )
                        if existing_today:
                            for key, val in ebay_fields.items():
                                existing_today[key] = val
                        else:
                            hist[retry_box_id].append({"date": today_str, **ebay_fields})

                        # Write to database
                        write_ebay_to_db(retry_box_id, today_str, ebay_fields, filtered_items)

                        results_count += 1
                        logger.info(f"    ✅ RETRY SUCCESS: {retry_name} - {len(filtered_items)} items")

                    except Exception as e:
                        logger.warning(f"    RETRY {attempt} failed for {retry_name}: {e}")
                        if attempt < MAX_RETRIES_PER_BOX:
                            retry_queue.append((retry_box_id, retry_config, attempt + 1))
                        else:
                            errors.append(f"{retry_box_id}: FAILED after {MAX_RETRIES_PER_BOX} retries ({e})")

        finally:
            await browser.close()

    # Save updated historical entries
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(hist, f, indent=2)
    logger.info(f"Saved eBay data to {HISTORICAL_FILE}")

    # Check for too many failures
    failure_rate = len(errors) / len(box_items) if box_items else 0
    if failure_rate > 0.5:
        logger.error(f"High failure rate: {failure_rate:.0%} ({len(errors)}/{len(box_items)})")

    summary = {
        "results": results_count,
        "errors": errors,
        "date": today_str,
    }
    logger.info(f"Phase 1b complete: {results_count} boxes scraped, {len(errors)} errors")
    return summary


# ============================================================================
# DATABASE WRITING
# ============================================================================

def write_ebay_to_db(
    box_id: str,
    today: str,
    ebay_fields: Dict[str, Any],
    sold_items: List[Dict[str, Any]],
) -> bool:
    """Write eBay data to ebay_box_metrics_daily and ebay_sales_raw tables."""
    try:
        from app.services.ebay_metrics_writer import upsert_ebay_daily_metrics, insert_ebay_sales_raw
    except ImportError:
        logger.warning("ebay_metrics_writer not available, skipping DB write")
        return False

    try:
        upsert_ebay_daily_metrics(
            booster_box_id=box_id,
            metric_date=today,
            ebay_sales_count=ebay_fields.get("ebay_sold_count", 0),
            ebay_volume_usd=ebay_fields.get("ebay_volume_usd", 0),
            ebay_median_sold_price_usd=ebay_fields.get("ebay_median_price_usd"),
            ebay_units_sold_count=ebay_fields.get("ebay_sold_today", 0),
            ebay_volume_7d_ema=None,  # Computed in Phase 3
            ebay_active_listings_count=None,  # Handled by 130point scraper
            ebay_active_median_price_usd=None,
            ebay_active_low_price_usd=None,
            ebay_listings_added_today=None,
            ebay_listings_removed_today=None,
        )
        logger.debug(f"  DB: upserted ebay_box_metrics_daily for {box_id}")
    except Exception as e:
        logger.warning(f"eBay daily metrics DB write failed for {box_id}: {e}")

    try:
        inserted = insert_ebay_sales_raw(booster_box_id=box_id, sold_items=sold_items)
        logger.debug(f"  DB: inserted {inserted} rows into ebay_sales_raw for {box_id}")
    except Exception as e:
        logger.warning(f"eBay raw sales DB write failed for {box_id}: {e}")

    return True


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    parser = argparse.ArgumentParser(description="Phase 1b: eBay Playwright Scraper")
    parser.add_argument("--debug", type=str, default=None, help="Only scrape this box_id")
    parser.add_argument("--dump-html", action="store_true", help="Dump raw HTML responses")
    parser.add_argument("--proxy", type=str, default=None, help="Proxy URL (http://user:pass@host:port)")
    parser.add_argument("--no-jitter", action="store_true", help="Skip startup jitter (for testing)")
    args = parser.parse_args()

    result = asyncio.run(run_ebay_scraper(
        debug_box_id=args.debug,
        dump_html=args.dump_html,
        skip_startup_jitter=args.no_jitter or args.debug is not None,
        proxy_url=args.proxy,
    ))
    print(json.dumps(result, indent=2))
