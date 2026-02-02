#!/usr/bin/env python3
"""
Phase 1b: eBay Sales & Listings Scraper via 130point.com
---------------------------------------------------------
Scrapes 130point.com — a third-party aggregator that surfaces real eBay sold
prices (including Best Offer accepted prices) and active for-sale listings.

Anti-detection measures:
  1. Session warming — load main page first, carry cookies through all requests
  2. Coherent browser profiles — UA + sec-ch-ua + platform all match per-session
  3. Human-like timing — gaussian jitter + occasional distraction pauses
  4. Randomized box order — shuffled each run
  5. Daily time jitter — handled upstream in daily_refresh.py (0-30 min delay)

Run standalone:  python scripts/ebay_scraper.py [--debug <box_id>] [--dump-html]
Called by daily_refresh.py as Phase 1b (after Apify, before listings scraper).

Rate limit: 10 searches/min on 130point (1-hour block on violation).
We pace at ~1 request per gaussian(8s, 2.5s) with distraction pauses mixed in.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

HISTORICAL_FILE = project_root / "data" / "historical_entries.json"
DEBUG_HTML_DIR = project_root / "data" / "debug_html"

# ============================================================================
# LISTING QUALITY CHECKS — mirrors TCGplayer listings_scraper.py filters
# ============================================================================

# Title keywords that indicate non-booster-box items (used for sold listings)
TITLE_EXCLUSIONS = [
    "japanese", "jp", "single", "card lot", "pack", "bundle",
    "damaged", "opened", "resealed", "display",
    "playmat", "sleeve", "deck box", "promo", "lot of",
    "empty", "no cards", "custom", "repack", "break",
]

# Japanese/Asian listing keywords (from TCGplayer scraper)
JAPANESE_EXCLUSIONS = [
    "japanese", "japan", "jp version", "jp ver", "\u65e5\u672c", "\u65e5\u672c\u8a9e",
    "japanese language", "asian english", "asian",
]

# Suspicious condition keywords (from TCGplayer scraper)
SUSPICIOUS_KEYWORDS = [
    "damaged", "opened", "no shrink wrap", "heavy play", "poor condition",
    "missing", "incomplete", "resealed", "no seal", "unsealed",
    "loose packs", "loose pack", "unsealed box", "no box", "packs only",
    "pack only", "empty box", "for display", "display only",
]

# Positive indicators that confirm a legitimate sealed box
POSITIVE_INDICATORS = [
    "booster box", "premium booster", "extra booster", "premium box",
    "factory sealed", "sealed",
]

# Price floor as fraction of TCG market price (81% = reject below 19% discount)
ACTIVE_MIN_PRICE_RATIO = 0.81


# ============================================================================
# COHERENT BROWSER PROFILES
# ============================================================================
# Each profile is a complete, internally-consistent browser identity.
# UA string, sec-ch-ua headers, Accept-Language, platform all match.
# One profile is chosen per session and used for ALL requests.

BROWSER_PROFILES = [
    {
        "name": "Chrome 131 macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"',
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1920",
        "viewport_height": "1080",
    },
    {
        "name": "Chrome 130 macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"',
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1440",
        "viewport_height": "900",
    },
    {
        "name": "Chrome 131 Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1920",
        "viewport_height": "1080",
    },
    {
        "name": "Chrome 130 Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1366",
        "viewport_height": "768",
    },
    {
        "name": "Firefox 134 Windows",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "sec_ch_ua": None,  # Firefox doesn't send sec-ch-ua
        "sec_ch_ua_mobile": None,
        "sec_ch_ua_platform": None,
        "accept_language": "en-US,en;q=0.5",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1920",
        "viewport_height": "1080",
    },
    {
        "name": "Safari 18 macOS",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
        "sec_ch_ua": None,  # Safari doesn't send sec-ch-ua
        "sec_ch_ua_mobile": None,
        "sec_ch_ua_platform": None,
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br",  # Safari doesn't support zstd
        "viewport_width": "1536",
        "viewport_height": "864",
    },
    {
        "name": "Chrome 131 Linux",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Linux"',
        "accept_language": "en-US,en;q=0.9",
        "accept_encoding": "gzip, deflate, br, zstd",
        "viewport_width": "1920",
        "viewport_height": "1080",
    },
]


# ============================================================================
# HUMAN-LIKE TIMING
# ============================================================================
# Gaussian delay with occasional longer "distraction pauses" that simulate
# someone switching to another browser tab and coming back.

DELAY_MEAN = 8.0
DELAY_SIGMA = 2.5
DELAY_MIN = 4.0
DELAY_MAX = 15.0
DISTRACTION_PAUSE_EVERY = (8, 12)  # pause every N requests (random range)
DISTRACTION_PAUSE_RANGE = (20, 40)  # seconds for the long pause

_request_counter = 0
_next_distraction_at = random.randint(*DISTRACTION_PAUSE_EVERY)


def _human_delay() -> float:
    """Return a human-like delay in seconds, with occasional long pauses."""
    global _request_counter, _next_distraction_at
    _request_counter += 1

    if _request_counter >= _next_distraction_at:
        _request_counter = 0
        _next_distraction_at = random.randint(*DISTRACTION_PAUSE_EVERY)
        delay = random.uniform(*DISTRACTION_PAUSE_RANGE)
        logger.debug(f"Distraction pause: {delay:.1f}s (next in ~{_next_distraction_at} requests)")
        return delay

    delay = random.gauss(DELAY_MEAN, DELAY_SIGMA)
    delay = max(DELAY_MIN, min(DELAY_MAX, delay))
    return delay


# ============================================================================
# EBAY SEARCH CONFIG — 18 boxes mapped to 130point search queries
# ============================================================================
# Price ranges are in USD DOLLARS (not cents). Used to filter out obviously
# wrong results (singles, packs, cases, bulk lots). Intentionally generous.
EBAY_SEARCH_CONFIG: Dict[str, Dict[str, Any]] = {
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {
        "name": "OP-01 Romance Dawn (Blue)",
        "query": "One Piece OP-01 Romance Dawn booster box sealed blue",
        "active_query": "romance dawn op01 booster box sealed blue",
        "min_price": 20,
        "max_price": 200,
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {
        "name": "OP-01 Romance Dawn (White)",
        "query": "One Piece OP-01 Romance Dawn booster box sealed white",
        "active_query": "romance dawn op01 booster box sealed white",
        "min_price": 15,
        "max_price": 150,
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {
        "name": "OP-02 Paramount War",
        "query": "One Piece OP-02 Paramount War booster box sealed",
        "active_query": "paramount war op02 booster box sealed",
        "min_price": 15,
        "max_price": 150,
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {
        "name": "OP-03 Pillars of Strength",
        "query": "One Piece OP-03 Pillars of Strength booster box sealed",
        "active_query": "pillars of strength op03 booster box sealed",
        "min_price": 15,
        "max_price": 150,
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {
        "name": "OP-04 Kingdoms of Intrigue",
        "query": "One Piece OP-04 Kingdoms Intrigue booster box sealed",
        "active_query": "kingdoms of intrigue op04 booster box sealed",
        "min_price": 15,
        "max_price": 120,
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {
        "name": "OP-05 Awakening of the New Era",
        "query": "One Piece OP-05 Awakening New Era booster box sealed",
        "active_query": "awakening of the new era op05 booster box sealed",
        "min_price": 20,
        "max_price": 200,
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {
        "name": "OP-06 Wings of the Captain",
        "query": "One Piece OP-06 Wings Captain booster box sealed",
        "active_query": "wings of the captain op06 booster box sealed",
        "min_price": 15,
        "max_price": 120,
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {
        "name": "OP-07 500 Years in the Future",
        "query": "One Piece OP-07 500 Years Future booster box sealed",
        "active_query": "500 years in the future op07 booster box sealed",
        "min_price": 15,
        "max_price": 120,
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {
        "name": "OP-08 Two Legends",
        "query": "One Piece OP-08 Two Legends booster box sealed",
        "active_query": "two legends op08 booster box sealed",
        "min_price": 30,
        "max_price": 250,
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {
        "name": "OP-09 Emperors in the New World",
        "query": "One Piece OP-09 Emperors New World booster box sealed",
        "active_query": "emperors in the new world op09 booster box sealed",
        "min_price": 30,
        "max_price": 250,
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {
        "name": "OP-10 Royal Blood",
        "query": "One Piece OP-10 Royal Blood booster box sealed",
        "active_query": "royal blood op10 booster box sealed",
        "min_price": 30,
        "max_price": 250,
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {
        "name": "OP-11 A Fist of Divine Speed",
        "query": "One Piece OP-11 Fist Divine Speed booster box sealed",
        "active_query": "fist of divine speed op11 booster box sealed",
        "min_price": 40,
        "max_price": 300,
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {
        "name": "OP-12 Legacy of the Master",
        "query": "One Piece OP-12 Legacy Master booster box sealed",
        "active_query": "legacy of the master op12 booster box sealed",
        "min_price": 30,
        "max_price": 250,
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {
        "name": "OP-13 Carrying on His Will",
        "query": "One Piece OP-13 Carrying His Will booster box sealed",
        "active_query": "carrying on his will op13 booster box sealed",
        "min_price": 200,
        "max_price": 900,
    },
    "3b17b708-b35b-4008-971e-240ade7afc9c": {
        "name": "EB-01 Memorial Collection",
        "query": "One Piece EB-01 Memorial Collection booster box sealed",
        "active_query": "memorial collection eb01 booster box sealed",
        "min_price": 40,
        "max_price": 350,
    },
    "7509a855-f6da-445e-b445-130824d81d04": {
        "name": "EB-02 Anime 25th Collection",
        "query": "One Piece EB-02 Anime 25th booster box sealed",
        "active_query": "anime 25th collection eb02 booster box sealed",
        "min_price": 30,
        "max_price": 250,
    },
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {
        "name": "PRB-01 Premium Booster",
        "query": "One Piece PRB-01 Premium Booster box sealed",
        "active_query": "premium booster prb01 booster box sealed",
        "min_price": 40,
        "max_price": 350,
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {
        "name": "PRB-02 Premium Booster Vol. 2",
        "query": "One Piece PRB-02 Premium Booster Vol 2 box sealed",
        "active_query": "premium booster vol 2 prb02 booster box sealed",
        "min_price": 40,
        "max_price": 250,
    },
}


# ============================================================================
# HELPERS
# ============================================================================

def _is_excluded_title(title: str) -> bool:
    """Check if a listing title indicates a non-booster-box item."""
    title_lower = title.lower()
    return any(excl in title_lower for excl in TITLE_EXCLUSIONS)


def _is_case_listing(title: str) -> bool:
    """Check if listing is for a case (wholesale multi-box unit), not a single box.

    Cases contain 12+ booster boxes and are priced far above single-box range.
    "Case fresh" is a condition descriptor for single boxes (pulled straight
    from a sealed case) and should NOT be excluded.
    """
    t = title.lower()
    # "case fresh" describes a single box's condition — allow it
    if "case fresh" in t:
        return False
    # Match "case" as a whole word (avoids "showcase", "suitcase", etc.)
    return bool(re.search(r'\bcase\b', t))


def _parse_price(price_str: str) -> Optional[int]:
    """Parse a price string like '$89.99' or 'US $89.99' to cents (int)."""
    if not price_str:
        return None
    cleaned = re.sub(r'[^\d.]', '', price_str.strip())
    try:
        dollars = float(cleaned)
        return int(round(dollars * 100))
    except (ValueError, TypeError):
        return None


def _parse_date(date_str: str) -> Optional[str]:
    """
    Parse a date string from 130point to ISO format (YYYY-MM-DD).

    130point format: "Sun 01 Feb 2026 12:07:57 EST"
    Also handles: "Feb 01, 2026", "01/02/2026", "2026-01-01"
    """
    if not date_str:
        return None
    date_str = date_str.strip()

    # Strip trailing timezone abbreviation (EST, PST, etc.) — strptime can't parse them
    date_str = re.sub(r'\s+[A-Z]{2,5}$', '', date_str)

    for fmt in (
        "%a %d %b %Y %H:%M:%S",  # Sun 01 Feb 2026 12:07:57  (130point primary)
        "%a %d %b %Y",            # Sun 01 Feb 2026
        "%d %b %Y %H:%M:%S",     # 01 Feb 2026 12:07:57
        "%d %b %Y",              # 01 Feb 2026
        "%b %d, %Y",             # Feb 01, 2026
        "%m/%d/%Y",              # 01/02/2026
        "%Y-%m-%d",              # 2026-01-01
        "%B %d, %Y",             # February 01, 2026
        "%b %d %Y",              # Feb 01 2026
    ):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    logger.debug(f"Could not parse date: {date_str!r}")
    return None


def _extract_ebay_item_id(url: str) -> Optional[str]:
    """Extract eBay item ID from a URL like 'https://www.ebay.com/itm/123456789'."""
    if not url:
        return None
    m = re.search(r'/itm/(\d+)', url)
    return m.group(1) if m else None


# ============================================================================
# SESSION MANAGER — persistent httpx client with warming + cookies
# ============================================================================

class BrowserSession:
    """
    Manages a persistent httpx session that mimics a real browser.

    On init:
      1. Picks a random browser profile (locked for the entire session)
      2. Builds internally-consistent headers from that profile
      3. Warms up by loading the 130point main page (gets cookies, looks natural)

    All subsequent requests reuse the same client (cookies carry forward).
    """

    def __init__(self, profile: Optional[Dict[str, Any]] = None):
        self.profile = profile or random.choice(BROWSER_PROFILES)
        self.client: Optional[Any] = None
        self._warmed = False

    def _build_headers(self, is_ajax: bool = False) -> Dict[str, str]:
        """Build a complete, consistent header set from the chosen profile.

        Note: We intentionally do NOT set Accept-Encoding. httpx handles
        transparent decompression automatically. Explicitly setting it causes
        the server to send compressed data that httpx doesn't auto-decode
        when reading .text, resulting in garbled binary output.
        """
        p = self.profile
        headers: Dict[str, str] = {
            "User-Agent": p["user_agent"],
            "Accept-Language": p["accept_language"],
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        if is_ajax:
            headers["Accept"] = "text/html, */*; q=0.01"
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers.pop("Upgrade-Insecure-Requests", None)
        else:
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"

        # sec-ch-ua family (Chrome only — None for Firefox/Safari)
        if p.get("sec_ch_ua"):
            headers["sec-ch-ua"] = p["sec_ch_ua"]
        if p.get("sec_ch_ua_mobile"):
            headers["sec-ch-ua-mobile"] = p["sec_ch_ua_mobile"]
        if p.get("sec_ch_ua_platform"):
            headers["sec-ch-ua-platform"] = p["sec_ch_ua_platform"]

        return headers

    async def start(self):
        """Create the httpx client."""
        import httpx
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            # httpx stores cookies automatically across requests on the same client
        )

    async def warm_up(self):
        """
        Load the 130point main sales page like a real user landing on the site.
        This sets cookies and makes subsequent API calls look natural
        (they come from a session that already visited the page).
        """
        if self._warmed:
            return
        if not self.client:
            await self.start()

        logger.info(f"Session warming: loading 130point.com (profile: {self.profile['name']})")
        try:
            headers = self._build_headers(is_ajax=False)
            resp = await self.client.get(
                "https://130point.com/sales/",
                headers=headers,
            )
            resp.raise_for_status()
            logger.info(f"  Warm-up complete: status={resp.status_code}, cookies={len(self.client.cookies)}")
            self._warmed = True
        except Exception as e:
            logger.warning(f"  Warm-up failed (non-fatal, continuing): {e}")
            self._warmed = True  # Don't retry, just proceed

    async def post(self, url: str, data: Dict[str, str], referer: str) -> str:
        """Make a POST request with full browser headers and session cookies."""
        if not self.client:
            await self.start()
        if not self._warmed:
            await self.warm_up()

        headers = self._build_headers(is_ajax=True)
        headers["Referer"] = referer
        headers["Origin"] = "https://130point.com"

        resp = await self.client.post(url, data=data, headers=headers)
        resp.raise_for_status()
        return resp.text

    async def close(self):
        """Close the httpx client."""
        if self.client:
            await self.client.aclose()
            self.client = None


# ============================================================================
# HTML PARSING
# ============================================================================

def parse_sold_listings_html(html: str) -> List[Dict[str, Any]]:
    """
    Parse sold listings HTML from 130point.com backend.

    130point returns an HTML fragment with a DataTable:
      <table id="salesDataTable-1">
        <tr data-currency="USD" data-price="300" data-rowid="1-2" id="dRow">
          <td id="imgCol">...</td>
          <td id="dCol">
            <span id="titleText"><a href="https://www.ebay.com/itm/123">Title</a></span>
            <span id="auctionLabel">Best Offer Accepted</span>
            <span id="priceSpanOuter"><b>Sale Price:</b>
              <span class="priceSpan" id="1-2-priceFull">300.00 USD</span>
            </span>
            <span id="dateText"><b>Date:</b>Sun 01 Feb 2026 12:07:57 EST</span>
          </td>
        </tr>

    Returns list of dicts with: title, sold_price_cents, sold_date, item_url,
    ebay_item_id, sale_type
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("BeautifulSoup not installed. Run: pip install beautifulsoup4")
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Find rows with data-price attribute (the real sold listing rows)
    rows = soup.find_all("tr", attrs={"data-price": True})
    if not rows:
        # Fallback: try the table directly
        table = soup.find("table", id=re.compile(r"salesDataTable"))
        if table:
            rows = table.find_all("tr", attrs={"data-price": True})

    logger.debug(f"Found {len(rows)} sold listing rows with data-price attr")

    for row in rows:
        try:
            # ── Price from data-price attribute (most reliable) ──
            data_price = row.get("data-price")
            data_currency = row.get("data-currency", "USD")
            if not data_price:
                continue

            try:
                price_dollars = float(data_price)
                price_cents = int(round(price_dollars * 100))
            except (ValueError, TypeError):
                continue

            # Skip non-USD for now
            if data_currency and data_currency.upper() != "USD":
                continue

            # ── Title + eBay URL from #titleText a ──
            title_span = row.find("span", id="titleText")
            if not title_span:
                continue
            title_link = title_span.find("a")
            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            if not title:
                continue
            item_url = title_link.get("href", "")

            # ── Sale type from #auctionLabel ──
            sale_type_el = row.find("span", id="auctionLabel")
            sale_type = sale_type_el.get_text(strip=True) if sale_type_el else None

            # ── Date from #dateText ──
            date_el = row.find("span", id="dateText")
            sold_date = None
            if date_el:
                date_text = date_el.get_text(strip=True)
                # Strip the "Date:" label prefix
                date_text = re.sub(r'^Date:\s*', '', date_text)
                sold_date = _parse_date(date_text)

            ebay_item_id = _extract_ebay_item_id(item_url)

            results.append({
                "title": title,
                "sold_price_cents": price_cents,
                "sold_date": sold_date,
                "item_url": item_url,
                "ebay_item_id": ebay_item_id,
                "sale_type": sale_type,
            })
        except Exception as e:
            logger.debug(f"Error parsing sold listing row: {e}")
            continue

    return results


# ============================================================================
# ACTIVE LISTINGS QUALITY CHECKS (mirrors TCGplayer scraper filters)
# ============================================================================

def _is_japanese(title: str) -> bool:
    """Check if listing is Japanese/Asian product."""
    t = title.lower()
    return any(excl in t for excl in JAPANESE_EXCLUSIONS)


def _is_suspicious(title: str) -> bool:
    """Check for damaged/opened/resealed indicators."""
    t = title.lower()
    # Check strict exclusion keywords
    if any(kw in t for kw in SUSPICIOUS_KEYWORDS):
        # Exception: "booster box" + "sealed" overrides ambiguous keywords
        has_positive = any(pos in t for pos in POSITIVE_INDICATORS)
        if has_positive and "sealed" in t:
            return False
        return True
    return False


def _is_valid_sealed_box(title: str) -> bool:
    """Title must contain 'sealed' AND 'box' (in any variation).

    This is the core inclusion filter per user spec — only count listings
    that explicitly mention both 'sealed' and 'box'/'booster box'.
    """
    t = title.lower()
    return "sealed" in t and "box" in t


def _normalize_title(title: str) -> str:
    """Normalize eBay listing title to a grouping key.
    Same normalized title + same price = likely same seller.
    """
    t = title.lower().strip()
    # Remove common noise prefixes
    for prefix in ("new ", "brand new ", "sealed ", "factory sealed ",
                   "free shipping ", "fast shipping ", "ships free "):
        if t.startswith(prefix):
            t = t[len(prefix):]
    # Remove punctuation except hyphens (OP-01, etc.)
    t = re.sub(r'[^\w\s-]', '', t)
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _extract_quantity(title: str) -> int:
    """Extract multi-box quantity from listing title.

    Detects patterns like "lot of 2", "2x", "x2", "2 boxes", "set of 2",
    "bundle of 2", "2 box lot". Returns 1 if no multi-box pattern found.
    Capped at 6 to avoid false positives from product codes (OP-01, EB-02).
    """
    t = title.lower()

    # Pattern 1: "lot of N", "set of N", "bundle of N"
    m = re.search(r'(?:lot|set|bundle)\s+of\s+(\d+)', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 2: "Nx" multiplier (e.g., "2x booster box sealed")
    # (?:^|\s) ensures not part of product code like OP-02
    m = re.search(r'(?:^|\s)(\d+)\s*x\s+', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 3: "xN" suffix (e.g., "booster box x2")
    # \b ensures word boundary before x (won't match inside "10x15")
    m = re.search(r'\bx\s*(\d+)(?:\s|$)', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    # Pattern 4: "N boxes" or "N booster boxes" or "N box lot"
    # (?:^|\s) before digit avoids product codes (OP-02 has "-" before "02")
    m = re.search(r'(?:^|\s)(\d+)\s+(?:booster\s+)?box(?:es)?(?:\s+lot)?', t)
    if m:
        qty = int(m.group(1))
        if 2 <= qty <= 6:
            return qty

    return 1


def filter_active_listings(
    raw: List[Dict[str, Any]],
    min_price_usd: float,
    max_price_usd: float,
    tcg_floor_price: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Filter active listings with TCGplayer-equivalent quality checks.

    Filters applied (in order):
    1. Title must contain 'sealed' AND 'box' (inclusion filter)
    2. Japanese/Asian exclusion
    3. Suspicious keywords (damaged, opened, resealed, etc.)
    4. Price range (config min/max)
    5. Price floor (81% of TCG market price if available)
    6. Dedup by eBay item ID
    """
    seen_ids: set = set()
    seen_title_price: set = set()
    filtered = []
    multi_box_count = 0
    excluded = {"no_sealed_box": 0, "case": 0, "japanese": 0, "suspicious": 0,
                "price_range": 0, "price_floor": 0, "dedup": 0,
                "title_price_dedup": 0}

    for item in raw:
        title = item.get("title", "")
        price_usd = item.get("price_usd")
        ebay_id = item.get("ebay_item_id")

        # 1. Must contain "sealed" AND "box"
        if not _is_valid_sealed_box(title):
            excluded["no_sealed_box"] += 1
            continue

        # 2. Case exclusion (allows "case fresh" single-box listings)
        if _is_case_listing(title):
            excluded["case"] += 1
            continue

        # 3. Japanese exclusion
        if _is_japanese(title):
            excluded["japanese"] += 1
            continue

        # 4. Suspicious keywords
        if _is_suspicious(title):
            excluded["suspicious"] += 1
            continue

        # 3b. Detect multi-box quantity and compute per-box price
        qty = _extract_quantity(title)
        if qty > 1:
            item = item.copy()
            shipping_usd = item.get("shipping_usd") or 0
            total_usd = (price_usd or 0) + shipping_usd
            price_usd = round(total_usd / qty, 2)
            item["price_usd"] = price_usd
            item["quantity"] = qty
            multi_box_count += 1

        # 4. Price range (uses per-box price after qty adjustment)
        if price_usd is not None:
            if price_usd < min_price_usd or price_usd > max_price_usd:
                excluded["price_range"] += 1
                continue

        # 5. Price floor (81% of TCG market price)
        if price_usd is not None and tcg_floor_price and tcg_floor_price > 0:
            if price_usd < tcg_floor_price * ACTIVE_MIN_PRICE_RATIO:
                excluded["price_floor"] += 1
                continue

        # 6. Dedup by eBay item ID
        if ebay_id:
            if ebay_id in seen_ids:
                excluded["dedup"] += 1
                continue
            seen_ids.add(ebay_id)

        # 7. Secondary dedup by price + normalized title (seller proxy)
        norm_title = _normalize_title(title)
        tp_key = f"{price_usd:.2f}|{norm_title}" if price_usd else None
        if tp_key:
            if tp_key in seen_title_price:
                excluded["title_price_dedup"] += 1
                continue
            seen_title_price.add(tp_key)

        filtered.append(item)

    logger.debug(f"Active filter stats: {excluded}, multi_box_adjusted={multi_box_count}")
    return filtered


# ============================================================================
# PLAYWRIGHT ACTIVE LISTINGS SCRAPER
# ============================================================================

async def scrape_active_listings_browser(
    box_items: List[tuple],
    dump_html: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape active eBay listings via Playwright on 130point.com.

    The active listings endpoint (getSalesFull.php) requires browser context
    (Cloudflare JS cookies), so we use Playwright to:
    1. Navigate to 130point.com/sales/
    2. Select 'Items For Sale' + 'eBay' marketplace
    3. For each box: type query, submit, wait, extract items

    Args:
        box_items: List of (box_id, config) tuples to scrape.
        dump_html: Save raw results HTML.

    Returns:
        Dict mapping box_id -> list of parsed active listing dicts.
    """
    from playwright.async_api import async_playwright

    results: Dict[str, List[Dict[str, Any]]] = {}
    profile = random.choice(BROWSER_PROFILES)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=profile["user_agent"],
            viewport={
                "width": int(profile["viewport_width"]),
                "height": int(profile["viewport_height"]),
            },
            locale="en-US",
        )
        page = await context.new_page()

        try:
            logger.info(f"Active listings: launching browser (profile: {profile['name']})")
            await page.goto(
                "https://130point.com/sales/",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_selector("#searchBar", timeout=15000)
            logger.info("  130point page loaded, search bar ready")

            # Select "Items For Sale" and "eBay" marketplace (once, persists)
            await page.select_option("#searchType", "for_sale2")
            await page.select_option("#marketplaceFS", "ebay")
            await asyncio.sleep(random.uniform(1.0, 2.0))

            for box_id, config in box_items:
                name = config["name"]
                active_query = config.get("active_query", config["query"])

                logger.info(f"  Active search: {name} -> {active_query!r}")

                try:
                    # Human-like delay between searches
                    await asyncio.sleep(_human_delay())

                    # Clear and type query
                    await page.fill("#searchBar", "")
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    await page.fill("#searchBar", active_query)
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                    # Submit search
                    await page.click("#submit_ebay")

                    # Wait for results to load (AJAX call)
                    await asyncio.sleep(random.uniform(8.0, 12.0))

                    # Dump HTML if requested
                    if dump_html:
                        results_html = await page.evaluate(
                            "() => document.querySelector('#results1')?.innerHTML || ''"
                        )
                        if results_html:
                            DEBUG_HTML_DIR.mkdir(parents=True, exist_ok=True)
                            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
                            path = DEBUG_HTML_DIR / f"active_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                            path.write_text(results_html)
                            logger.info(f"    Dumped active HTML to {path}")

                    # Extract items from the page
                    items = await page.evaluate("""() => {
                        const items = document.querySelectorAll('#itemsFS_item');
                        return Array.from(items).map(item => {
                            // Title from the ebayFS link
                            const titleLink = item.querySelector('a.ebayFS, a#itemsFS-break-line');
                            const title = titleLink ? titleLink.textContent.trim() : '';
                            const url = titleLink ? titleLink.href : '';

                            // Price from "Current Price: XX USD" text
                            const textContent = item.querySelector('.itemsFS_text')?.textContent || '';
                            const priceMatch = textContent.match(/Current Price:\\s*([\\d,.]+)\\s*USD/i);
                            const price = priceMatch ? parseFloat(priceMatch[1].replace(',', '')) : null;

                            // Listing type
                            const typeMatch = textContent.match(/(Buy It Now|Auction|Best Offer)[^\\n]*/i);
                            const listingType = typeMatch ? typeMatch[0].trim() : null;

                            return { title, url, price, listingType };
                        });
                    }""")

                    # Parse into our standard format
                    parsed = []
                    for item in items:
                        if not item.get("title"):
                            continue
                        ebay_item_id = _extract_ebay_item_id(item.get("url", ""))
                        parsed.append({
                            "title": item["title"],
                            "price_usd": item.get("price"),
                            "item_url": item.get("url", ""),
                            "ebay_item_id": ebay_item_id,
                            "listing_type": item.get("listingType"),
                        })

                    results[box_id] = parsed
                    logger.info(f"    Found {len(parsed)} raw active listings")

                except Exception as e:
                    logger.warning(f"    Error scraping active for {name}: {e}")
                    results[box_id] = []

        finally:
            await browser.close()

    return results


# ============================================================================
# 130POINT API INTERACTION (uses BrowserSession)
# ============================================================================

async def fetch_sold_listings(
    session: BrowserSession,
    query: str,
    dump_html: bool = False,
    box_name: str = "",
) -> str:
    """Fetch sold listings HTML from 130point backend via the shared session."""
    html = await session.post(
        "https://back.130point.com/sales/",
        data={
            "query": query,
            "type": "1",
            "subcat": "",
            "tab_id": "1",
            "tz": "America/New_York",
            "sort": "EndTimeSoonest",
        },
        referer="https://130point.com/sales/",
    )

    if dump_html:
        DEBUG_HTML_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', box_name)
        path = DEBUG_HTML_DIR / f"sold_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path.write_text(html)
        logger.info(f"  Dumped sold HTML to {path}")

    return html




# ============================================================================
# FILTERING & TRANSFORMATION
# ============================================================================

def filter_sold_listings(
    raw: List[Dict[str, Any]],
    min_price_usd: float,
    max_price_usd: float,
) -> List[Dict[str, Any]]:
    """Filter sold listings with TCGplayer-equivalent quality checks.

    Filters applied (in order):
    1. Title keyword exclusion
    2. Japanese/Asian exclusion
    3. Suspicious keyword exclusion
    4. Price range (config min/max)
    5. Dedup by eBay item ID
    6. Secondary dedup by price + normalized title (seller proxy)

    Args:
        raw: Parsed listing dicts with sold_price_cents.
        min_price_usd: Minimum price in USD dollars (e.g. 30 = $30).
        max_price_usd: Maximum price in USD dollars (e.g. 250 = $250).
    """
    seen_ids: set = set()
    seen_title_price: set = set()
    filtered = []
    multi_box_count = 0
    excluded = {"title_exclusion": 0, "case": 0, "japanese": 0, "suspicious": 0,
                "price_range": 0, "dedup": 0, "title_price_dedup": 0}

    for item in raw:
        title = item.get("title", "")
        price_cents = item.get("sold_price_cents")
        ebay_id = item.get("ebay_item_id")

        if _is_excluded_title(title):
            excluded["title_exclusion"] += 1
            continue
        if _is_case_listing(title):
            excluded["case"] += 1
            continue
        if _is_japanese(title):
            excluded["japanese"] += 1
            continue
        if _is_suspicious(title):
            excluded["suspicious"] += 1
            continue

        # 3b. Detect multi-box quantity and compute per-box price
        qty = _extract_quantity(title)
        if qty > 1:
            item = item.copy()
            shipping_cents = item.get("shipping_cents") or 0
            total_cents = (price_cents or 0) + shipping_cents
            price_cents = int(round(total_cents / qty))
            item["sold_price_cents"] = price_cents
            item["quantity"] = qty
            multi_box_count += 1

        # 4. Price range (uses per-box price after qty adjustment)
        if price_cents is not None:
            price_usd = price_cents / 100.0
            if price_usd < min_price_usd or price_usd > max_price_usd:
                excluded["price_range"] += 1
                continue
        if ebay_id:
            if ebay_id in seen_ids:
                excluded["dedup"] += 1
                continue
            seen_ids.add(ebay_id)
        # Secondary dedup: price + normalized title (seller proxy)
        price_usd = (price_cents / 100.0) if price_cents else 0
        norm_title = _normalize_title(title)
        tp_key = f"{price_usd:.2f}|{norm_title}"
        if tp_key in seen_title_price:
            excluded["title_price_dedup"] += 1
            continue
        seen_title_price.add(tp_key)

        filtered.append(item)

    logger.debug(f"Sold filter stats: {excluded}, multi_box_adjusted={multi_box_count}")
    return filtered


def compute_ebay_fields(
    sold: List[Dict[str, Any]],
    today: str,
    active: Optional[List[Dict[str, Any]]] = None,
    new_sales_only: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Transform filtered sold + active listings into ebay_* fields for the JSON entry.
    All prices in the output are in USD (float), not cents.

    Args:
        sold: All filtered sold listings (for aggregate stats like median).
        today: ISO date string (YYYY-MM-DD).
        active: Filtered active listings.
        new_sales_only: If provided, use these (cross-day deduped) for today's count
                        instead of date-filtering from sold.
    """
    # Expand prices by quantity so median/mean/volume reflect per-box prices
    # weighted by actual box count (e.g., "lot of 2" at $1185 → 2× $592.50)
    sold_prices = []
    for item in sold:
        if item.get("sold_price_cents") is not None:
            per_box = item["sold_price_cents"] / 100.0
            qty = item.get("quantity", 1)
            sold_prices.extend([per_box] * qty)

    # Total boxes sold (sum of quantities)
    sold_box_count = sum(item.get("quantity", 1) for item in sold)

    # Daily count uses yesterday (eBay data lags — today's sales aren't complete)
    yesterday = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    if new_sales_only is not None:
        today_sold = [item for item in new_sales_only if item.get("sold_date") == yesterday]
    else:
        today_sold = [item for item in sold if item.get("sold_date") == yesterday]
    today_prices = []
    for item in today_sold:
        if item.get("sold_price_cents") is not None:
            per_box = item["sold_price_cents"] / 100.0
            qty = item.get("quantity", 1)
            today_prices.extend([per_box] * qty)
    today_box_count = sum(item.get("quantity", 1) for item in today_sold)

    sold_dates = [item.get("sold_date") for item in sold if item.get("sold_date")]
    last_sold_date = max(sold_dates) if sold_dates else None

    # Active listings metrics (expand by quantity for multi-box lots)
    active = active or []
    active_prices = []
    for item in active:
        if item.get("price_usd") is not None:
            per_box = item["price_usd"]
            qty = item.get("quantity", 1)
            active_prices.extend([per_box] * qty)
    active_box_count = sum(item.get("quantity", 1) for item in active) if active else None

    return {
        "ebay_sold_count": sold_box_count,
        "ebay_sold_today": today_box_count,
        "ebay_volume_usd": round(sum(sold_prices), 2) if sold_prices else 0,
        "ebay_daily_volume_usd": round(sum(today_prices), 2) if today_prices else 0,
        "ebay_median_price_usd": round(statistics.median(sold_prices), 2) if sold_prices else None,
        "ebay_avg_price_usd": round(statistics.mean(sold_prices), 2) if sold_prices else None,
        "ebay_low_price_usd": round(min(sold_prices), 2) if sold_prices else None,
        "ebay_high_price_usd": round(max(sold_prices), 2) if sold_prices else None,
        "ebay_active_listings": active_box_count,
        "ebay_active_median_price": round(statistics.median(active_prices), 2) if active_prices else None,
        "ebay_active_low_price": round(min(active_prices), 2) if active_prices else None,
        "ebay_source": "130point",
        "ebay_fetch_timestamp": datetime.now(timezone.utc).isoformat(),
        "ebay_last_sold_date": last_sold_date,
    }


# ============================================================================
# DB WRITING
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
            ebay_active_listings_count=ebay_fields.get("ebay_active_listings"),
            ebay_active_median_price_usd=ebay_fields.get("ebay_active_median_price"),
            ebay_active_low_price_usd=ebay_fields.get("ebay_active_low_price"),
            ebay_listings_added_today=ebay_fields.get("ebay_boxes_added_today"),
            ebay_listings_removed_today=ebay_fields.get("ebay_boxes_removed_today"),
        )
    except Exception as e:
        logger.warning(f"eBay daily metrics DB write failed for {box_id}: {e}")

    try:
        insert_ebay_sales_raw(booster_box_id=box_id, sold_items=sold_items)
    except Exception as e:
        logger.warning(f"eBay raw sales DB write failed for {box_id}: {e}")

    return True


# ============================================================================
# MAIN SCRAPER
# ============================================================================

async def run_ebay_scraper(
    debug_box_id: Optional[str] = None,
    dump_html: bool = False,
    skip_active: bool = False,
) -> Dict[str, Any]:
    """
    Scrape 130point for eBay sold + active listings for all 18 boxes.

    Phase 1b-A: Sold listings via httpx (fast, no browser needed)
    Phase 1b-B: Active listings via Playwright (needs browser for Cloudflare)

    Args:
        debug_box_id: If set, only scrape this box.
        dump_html: If True, save raw HTML responses to data/debug_html/.
        skip_active: If True, skip the active listings phase (sold only).

    Returns:
        Summary dict: {results: int, errors: list, date: str}
    """
    import os
    skip_active = skip_active or os.environ.get("SKIP_EBAY_ACTIVE", "").lower() in ("1", "true", "yes")

    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Phase 1b: eBay scraper starting for {today}")

    # Load historical entries
    with open(HISTORICAL_FILE, "r") as f:
        hist = json.load(f)

    # Determine which boxes to scrape
    if debug_box_id:
        if debug_box_id not in EBAY_SEARCH_CONFIG:
            logger.error(f"Box {debug_box_id} not in EBAY_SEARCH_CONFIG")
            return {"results": 0, "errors": [f"Unknown box: {debug_box_id}"], "date": today}
        box_items = [(debug_box_id, EBAY_SEARCH_CONFIG[debug_box_id])]
    else:
        # Randomize box order each run (anti-detection measure #4)
        box_items = list(EBAY_SEARCH_CONFIG.items())
        random.shuffle(box_items)
        logger.info(f"Shuffled box order for this run ({len(box_items)} boxes)")

    results_count = 0
    errors = []
    consecutive_errors = 0

    # ── Phase 1b-A: Sold listings (httpx) ──────────────────────────
    logger.info(f"Phase 1b-A: Scraping sold listings ({len(box_items)} boxes)")
    sold_data: Dict[str, List[Dict[str, Any]]] = {}

    session = BrowserSession()
    try:
        await session.start()
        await session.warm_up()
        await asyncio.sleep(random.uniform(2.0, 5.0))

        for box_id, config in box_items:
            name = config["name"]
            query = config["query"]
            min_price = config["min_price"]
            max_price = config["max_price"]

            logger.info(f"Scraping sold data for {name}")

            try:
                await asyncio.sleep(_human_delay())

                sold_html = await fetch_sold_listings(
                    session, query, dump_html=dump_html, box_name=name,
                )
                raw_sold = parse_sold_listings_html(sold_html)
                filtered_sold = filter_sold_listings(raw_sold, min_price, max_price)
                logger.info(f"  Sold: {len(raw_sold)} raw -> {len(filtered_sold)} filtered")

                sold_data[box_id] = filtered_sold
                results_count += 1
                consecutive_errors = 0

            except Exception as e:
                error_msg = f"Sold {name}: {e}"
                errors.append(error_msg)
                consecutive_errors += 1
                logger.warning(f"  Error: {e}")
                sold_data[box_id] = []

                err_str = str(e).lower()
                if "429" in err_str or "rate" in err_str or "blocked" in err_str:
                    logger.warning("Rate limited — waiting 60s then retrying")
                    await asyncio.sleep(60)
                    try:
                        await fetch_sold_listings(session, query)
                        consecutive_errors = 0
                    except Exception:
                        break

                if consecutive_errors >= 3:
                    logger.warning("3 consecutive errors — aborting sold phase")
                    break
    finally:
        await session.close()

    # ── Phase 1b-B: Active listings (Playwright) ───────────────────
    active_data: Dict[str, List[Dict[str, Any]]] = {}

    if skip_active:
        logger.info("Phase 1b-B: Active listings SKIPPED (skip_active=True)")
    else:
        logger.info(f"Phase 1b-B: Scraping active listings ({len(box_items)} boxes)")
        try:
            raw_active = await scrape_active_listings_browser(
                box_items, dump_html=dump_html,
            )

            # Apply quality filters to each box's active listings
            for box_id, config in box_items:
                raw = raw_active.get(box_id, [])
                if not raw:
                    active_data[box_id] = []
                    continue

                # Get TCG floor price from existing JSON for price floor check
                tcg_floor = None
                existing_today = next(
                    (e for e in hist.get(box_id, []) if e.get("date") == today), None
                )
                if existing_today:
                    tcg_floor = existing_today.get("floor_price_usd")

                filtered = filter_active_listings(
                    raw,
                    min_price_usd=config["min_price"],
                    max_price_usd=config["max_price"],
                    tcg_floor_price=tcg_floor,
                )
                active_data[box_id] = filtered
                logger.info(
                    f"  Active {config['name']}: {len(raw)} raw -> {len(filtered)} filtered"
                )

        except Exception as e:
            logger.warning(f"Phase 1b-B (active listings) failed (non-fatal): {e}")
            errors.append(f"Active listings: {e}")

    # ── Merge sold + active into JSON and DB ───────────────────────
    for box_id, config in box_items:
        filtered_sold = sold_data.get(box_id, [])
        filtered_active = active_data.get(box_id, [])

        # Cross-day dedup: identify items already seen in previous entries
        prev_item_ids = set()
        for prev_entry in hist.get(box_id, []):
            if prev_entry.get("date") != today:
                for pid in prev_entry.get("_ebay_sold_item_ids", []):
                    prev_item_ids.add(pid)

        # Track this run's item IDs for future cross-day dedup
        current_item_ids = [item["ebay_item_id"] for item in filtered_sold if item.get("ebay_item_id")]

        # Truly new sales = not seen in any previous day
        new_sales = [item for item in filtered_sold if item.get("ebay_item_id") not in prev_item_ids]

        ebay_fields = compute_ebay_fields(filtered_sold, today, filtered_active, new_sales_only=new_sales)
        ebay_fields["_ebay_sold_item_ids"] = current_item_ids

        # Compute eBay active listing delta (mirrors TCGplayer boxes_added_today)
        ebay_active_count = ebay_fields.get("ebay_active_listings")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_entry = next(
            (e for e in hist.get(box_id, []) if e.get("date") == yesterday_str), None
        )
        yesterday_ebay_active = (
            yesterday_entry.get("ebay_active_listings")
            if yesterday_entry else None
        )

        if ebay_active_count is not None and yesterday_ebay_active is not None:
            delta = ebay_active_count - yesterday_ebay_active
            ebay_fields["ebay_boxes_added_today"] = delta
            ebay_fields["ebay_boxes_removed_today"] = max(0, -delta)
        else:
            ebay_fields["ebay_boxes_added_today"] = None
            ebay_fields["ebay_boxes_removed_today"] = None

        if box_id not in hist:
            hist[box_id] = []

        existing_today = next(
            (e for e in hist[box_id] if e.get("date") == today), None
        )
        if existing_today:
            for key, val in ebay_fields.items():
                existing_today[key] = val
        else:
            hist[box_id].append({"date": today, **ebay_fields})

        write_ebay_to_db(box_id, today, ebay_fields, filtered_sold)

        logger.info(
            f"  {config['name']}: sold={ebay_fields['ebay_sold_count']}, "
            f"active={ebay_fields.get('ebay_active_listings', 'N/A')}, "
            f"median=${ebay_fields.get('ebay_median_price_usd', 'N/A')}"
        )

    # Save updated historical entries
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(hist, f, indent=2)
    logger.info(f"Saved eBay data to {HISTORICAL_FILE}")

    summary = {
        "results": results_count,
        "errors": errors,
        "date": today,
    }
    logger.info(f"Phase 1b complete: {results_count} boxes scraped, {len(errors)} errors")
    return summary


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

    parser = argparse.ArgumentParser(description="Phase 1b: eBay Scraper via 130point.com")
    parser.add_argument("--debug", type=str, default=None, help="Only scrape this box_id")
    parser.add_argument("--dump-html", action="store_true", help="Dump raw HTML responses for inspection")
    parser.add_argument("--skip-active", action="store_true", help="Skip active listings (sold only)")
    args = parser.parse_args()

    result = asyncio.run(run_ebay_scraper(
        debug_box_id=args.debug,
        dump_html=args.dump_html,
        skip_active=args.skip_active,
    ))
    print(json.dumps(result, indent=2))
