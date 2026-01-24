#!/usr/bin/env python3
"""Quick test: scrape one box and show results"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Box configurations for testing
TEST_BOXES = {
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {  # OP-13
        "url": "https://www.tcgplayer.com/product/628352/one-piece-card-game-carrying-on-his-will-carrying-on-his-will-booster-box?Language=English",
        "name": "OP-13: Carrying On His Will"
    },
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {  # OP-01
        "url": "https://www.tcgplayer.com/product/450086/one-piece-card-game-romance-dawn-romance-dawn-booster-box-wave-1-blue?Language=English",
        "name": "OP-01: Romance Dawn"
    },
}

# Default to OP-13, but allow override via command line
DEFAULT_BOX_ID = "2d7d2b54-596d-4c80-a02f-e2eeefb45a34"  # OP-13
TEST_BOX_ID = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BOX_ID

if TEST_BOX_ID not in TEST_BOXES:
    logger.error(f"Unknown box ID: {TEST_BOX_ID}")
    logger.info(f"Available boxes: {list(TEST_BOXES.keys())}")
    sys.exit(1)

TEST_URL = TEST_BOXES[TEST_BOX_ID]["url"]
BOX_NAME = TEST_BOXES[TEST_BOX_ID]["name"]


async def scrape_listings_page(page, min_price, max_price):
    """Extract listings using JavaScript, filter by price range and exclude packs/Japanese/suspicious listings"""
    try:
        # Wait for listings to appear (with longer timeout)
        try:
            await page.wait_for_selector('.listing-item', timeout=15000)
        except:
            # If no listings found, try scrolling
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            try:
                await page.wait_for_selector('.listing-item', timeout=5000)
            except:
                logger.warning("  No .listing-item elements found on this page")
                return {
                    'filtered_listings': [],
                    'total_count': 0,
                    'filtered_count': 0,
                    'should_stop': False
                }
        
        # Check how many listing elements we found - try multiple selectors
        listing_count = await page.evaluate('document.querySelectorAll(".listing-item").length')
        listing_count_alt = await page.evaluate('document.querySelectorAll("[class*=\'listing\']").length')
        logger.info(f"  DEBUG: Found {listing_count} .listing-item elements, {listing_count_alt} total elements with 'listing' in class")
        
        # Also check for other possible listing containers
        all_listing_selectors = await page.evaluate('''
            () => {
                const selectors = [
                    '.listing-item',
                    '[class*="listing"]',
                    '[class*="Listing"]',
                    '[data-listing]',
                    'article',
                    '[role="listitem"]'
                ];
                const counts = {};
                selectors.forEach(sel => {
                    try {
                        counts[sel] = document.querySelectorAll(sel).length;
                    } catch(e) {}
                });
                return counts;
            }
        ''')
        logger.info(f"  DEBUG: Listing element counts by selector: {all_listing_selectors}")
        
        result = await page.evaluate('''
            () => {
                const listings = [];
                const debugInfo = [];
                const listingElements = document.querySelectorAll('.listing-item');
                
                let processedCount = 0;
                const filterCounts = {
                    pack: 0,
                    japanese: 0,
                    suspicious: 0,
                    passed: 0
                };
                
                listingElements.forEach((el, index) => {
                    try {
                        processedCount++;
                        // Get full text first to check if it's a box
                        const fullText = (el.innerText || '').toLowerCase();
                        const fullTextOriginal = el.innerText || '';
                        
                        // Debug: log first few listings BEFORE filtering
                        if (index < 5) {
                            let filterReason = '';
                            
                            // Check each filter
                            if (fullText.includes('single pack') || 
                                fullText.includes('1 pack') ||
                                (fullText.includes(' pack') && !fullText.includes('box') && !fullText.includes('booster'))) {
                                filterReason = 'pack';
                            } else if (fullText.includes('japanese') || 
                                fullText.includes('jpn') ||
                                fullText.includes('jp ') ||
                                fullText.includes('(jp)')) {
                                filterReason = 'japanese';
                            } else {
                                // Check suspicious keywords
                                if (fullText.includes('damaged')) {
                                    filterReason = 'suspicious: damaged';
                                } else if (fullText.includes('resealed')) {
                                    filterReason = 'suspicious: resealed';
                                } else if (fullText.includes('repack')) {
                                    filterReason = 'suspicious: repack';
                                } else if (fullText.includes('not sealed')) {
                                    filterReason = 'suspicious: not sealed';
                                } else if (fullText.includes('used')) {
                                    filterReason = 'suspicious: used';
                                } else if (fullText.includes('played')) {
                                    filterReason = 'suspicious: played';
                                } else if (fullText.includes('poor condition')) {
                                    filterReason = 'suspicious: poor condition';
                                } else if (fullText.includes('opened') && !fullText.includes('unopened')) {
                                    filterReason = 'suspicious: opened';
                                }
                            }
                            
                            debugInfo.push({
                                index: index,
                                textPreview: fullTextOriginal.substring(0, 200),
                                filterReason: filterReason || 'passed',
                                hasPack: fullText.includes('pack'),
                                hasBox: fullText.includes('box'),
                                hasBooster: fullText.includes('booster')
                            });
                        }
                        
                        // Skip if it's clearly a single pack (but allow "booster box")
                        if (fullText.includes('single pack') || 
                            fullText.includes('1 pack') ||
                            (fullText.includes(' pack') && !fullText.includes('box') && !fullText.includes('booster'))) {
                            filterCounts.pack++;
                            return; // Skip this listing
                        }
                        
                        // Skip Japanese listings - be more specific to avoid false positives
                        // Check for "japanese" as a word (not part of another word) or explicit JP markers
                        if (fullText.includes(' japanese ') || 
                            fullText.includes('japanese version') ||
                            fullText.includes('japanese language') ||
                            fullText.includes('(jpn)') ||
                            fullText.includes('(jp)') ||
                            fullText.startsWith('japanese') ||
                            (fullText.includes('jpn') && (fullText.includes('version') || fullText.includes('language')))) {
                            filterCounts.japanese++;
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
                            filterCounts.suspicious++;
                            return; // Skip suspicious listings
                        }
                        
                        filterCounts.passed++;
                        
                        let price = 0;
                        // Try to find price in common TCGplayer price locations
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
                                // Try multiple price patterns
                                let match = text.match(/\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/);
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
                        
                        const conditionEl = el.querySelector('[class*="condition"]');
                        const condition = conditionEl ? conditionEl.innerText.trim() : '';
                        
                        const sellerEl = el.querySelector('[class*="seller"]');
                        const seller = sellerEl ? sellerEl.innerText.trim() : '';
                        
                        // Always include for debugging, even if price is 0
                        listings.push({
                            price: price,
                            quantity: quantity,
                            condition: condition,
                            seller: seller.substring(0, 50),
                            title: fullText.substring(0, 100).replace(/\\n/g, ' ')
                        });
                    } catch (e) {}
                });
                
                return { 
                    listings: listings, 
                    debugInfo: debugInfo,
                    processedCount: processedCount,
                    filterCounts: filterCounts,
                    totalFound: listingElements.length
                };
            }
        ''')
        
        # Extract listings and debug info
        listings_data = result.get('listings', []) if result else []
        debug_info = result.get('debugInfo', []) if result else []
        processed_count = result.get('processedCount', 0) if result else 0
        filter_counts = result.get('filterCounts', {}) if result else {}
        total_found = result.get('totalFound', 0) if result else 0
        
        # Log processing summary
        logger.info(f"  DEBUG: Processing summary - Found {total_found} listing elements, processed {processed_count}")
        if filter_counts:
            logger.info(f"  DEBUG: Filter breakdown - Passed: {filter_counts.get('passed', 0)}, Pack: {filter_counts.get('pack', 0)}, Japanese: {filter_counts.get('japanese', 0)}, Suspicious: {filter_counts.get('suspicious', 0)}")
        
        # Log debug info for first few listings
        if debug_info:
            logger.info(f"  DEBUG: Sample listing analysis (first {len(debug_info)}):")
            for dbg in debug_info:
                logger.info(f"    [{dbg['index']}] Filter: {dbg.get('filterReason', 'unknown')} | Text: '{dbg.get('textPreview', '')[:120]}...'")
                logger.info(f"         hasPack: {dbg.get('hasPack', False)}, hasBox: {dbg.get('hasBox', False)}, hasBooster: {dbg.get('hasBooster', False)}")
        
        # Debug: show all prices found (including 0s to see if extraction is working)
        all_prices_raw = [l['price'] for l in listings_data] if listings_data else []
        prices_with_zeros = [p for p in all_prices_raw]
        logger.info(f"  DEBUG: Raw prices extracted (including 0s): {prices_with_zeros[:10] if prices_with_zeros else 'none'}...")
        
        # Filter out listings with price = 0 (extraction failed)
        listings_with_prices = [l for l in listings_data if l['price'] > 0] if listings_data else []
        zero_price_count = len(listings_data) - len(listings_with_prices) if listings_data else 0
        if zero_price_count > 0:
            logger.info(f"  DEBUG: {zero_price_count} listings had price = 0 (extraction failed)")
        
        listings_data = listings_with_prices
        
        # Debug: show all prices found after filtering
        total_listings_count = len(listings_data) if listings_data else 0
        if listings_data:
            all_prices = sorted([l['price'] for l in listings_data])
            in_range_prices = [p for p in all_prices if min_price <= p <= max_price]
            logger.info(f"  DEBUG: Found {total_listings_count} listings with valid prices: {all_prices[:10] if all_prices else 'none'}...")
            logger.info(f"  DEBUG: Prices in range (${min_price:.2f} - ${max_price:.2f}): {in_range_prices[:10] if in_range_prices else 'none'}")
        else:
            logger.info(f"  DEBUG: No listings with valid prices found (all filtered out or price extraction failed)")
        
        # Filter by price range: min_price (floor) to max_price (20% above market)
        # Only count listings within 20% of market price
        filtered_listings = []
        should_stop = False  # Flag to stop pagination if all listings exceed max_price
        
        if listings_data:
            # Filter to only include listings within our price range
            filtered_listings = [
                l for l in listings_data 
                if min_price <= l['price'] <= max_price
            ]
            
            # Expand listings by quantity - each unit counts as a separate listing
            expanded_listings = []
            for listing in filtered_listings:
                quantity = listing.get('quantity', 1)
                # Create one listing entry for each unit
                for i in range(quantity):
                    # Create a copy of the listing for each unit
                    expanded_listing = listing.copy()
                    expanded_listing['quantity'] = 1  # Each expanded listing represents 1 unit
                    expanded_listing['unit_number'] = i + 1  # Track which unit this is (1, 2, 3, etc.)
                    expanded_listings.append(expanded_listing)
            
            filtered_listings = expanded_listings
            
            # Check if we should stop pagination
            # Stop if all listings on this page exceed max_price (we've gone past the 20% threshold)
            if listings_data:
                min_listing_price = min([l['price'] for l in listings_data])
                if min_listing_price > max_price:
                    # All listings exceed 20% threshold - stop pagination
                    should_stop = True
                    logger.info(f"  All listings exceed 20% threshold (${max_price:.2f}), stopping pagination")
                elif filtered_listings:
                    # Check if the highest filtered listing is close to max (within 1%)
                    max_filtered_price = max([l['price'] for l in filtered_listings])
                    if max_filtered_price >= max_price * 0.99:
                        # We're at the top of our range, but continue to see if there are more
                        pass
        
        # Return filtered listings and stop flag
        return {
            'filtered_listings': filtered_listings,
            'total_count': total_listings_count,
            'filtered_count': len(filtered_listings),
            'should_stop': should_stop
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'filtered_listings': [],
            'total_count': 0,
            'filtered_count': 0,
            'should_stop': False
        }


async def main():
    logger.info("=" * 60)
    logger.info(f"Testing Single Box Scrape: {BOX_NAME}")
    logger.info("=" * 60)
    
    # Load market price from historical data
    market_price = 0
    box_id = TEST_BOX_ID
    
    try:
        with open('data/historical_entries.json', 'r') as f:
            hist = json.load(f)
        if box_id in hist and hist[box_id]:
            # Find the most recent entry that has a market price (not just the latest entry)
            sorted_entries = sorted(hist[box_id], key=lambda x: x.get('date', ''), reverse=True)
            market_price = 0
            for entry in sorted_entries:
                market_price = entry.get('market_price_usd') or entry.get('floor_price_usd', 0)
                if market_price and market_price > 0:
                    logger.info(f"Loaded market price: ${market_price:.2f} from {entry.get('date')}")
                    break
            if not market_price or market_price <= 0:
                logger.error(f"⚠️  NO MARKET PRICE FOUND in historical data for {box_id}")
    except Exception as e:
        logger.warning(f"Could not load market price: {e}")
        market_price = 0
    
    # Price range: 15% below market price to 20% above market price
    if market_price and market_price > 0:
        min_box_price = market_price * 0.85  # 15% below market price
        max_box_price = market_price * 1.20  # 20% above market price
        logger.info(f"Price range: ${min_box_price:.2f} - ${max_box_price:.2f} (market: ${market_price:.2f}, -15% to +20%)")
    else:
        min_box_price = 100  # Fallback
        max_box_price = 1200  # Fallback
        logger.warning(f"No market price available, using fallback: ${min_box_price:.2f} - ${max_box_price:.2f}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        logger.info(f"Navigating to: {TEST_URL}")
        await page.goto(TEST_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        
        # Scroll
        for i in range(5):
            await page.evaluate(f'window.scrollTo(0, {(i+1) * 400})')
            await asyncio.sleep(0.3)
        
        # Click Listings tab - try multiple selectors
        logger.info("Looking for Listings tab...")
        clicked = False
        
        # Wait a bit for tabs to render
        await asyncio.sleep(2)
        
        # Try different selectors
        selectors = [
            'text=Listings',
            'button:has-text("Listings")',
            '[role="tab"]:has-text("Listings")',
            '.tab-item:has-text("Listings")',
            'a:has-text("Listings")',
            '[class*="tab"]:has-text("Listings")',
        ]
        
        for sel in selectors:
            try:
                tab = await page.query_selector(sel)
                if tab:
                    # Scroll tab into view
                    await tab.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await tab.click()
                    logger.info(f"✓ Clicked Listings tab using: {sel}")
                    clicked = True
                    await asyncio.sleep(4)  # Wait for listings to load
                    break
            except Exception as e:
                logger.debug(f"Selector {sel} failed: {e}")
        
        if not clicked:
            logger.warning("⚠ No Listings tab found - trying to find listings anyway...")
            await page.evaluate('window.scrollTo(0, 2000)')
            await asyncio.sleep(2)
        
        # Scrape - paginate until we exceed 20% threshold
        all_listings = []
        current_page = 1
        max_pages = 20  # Increased limit, but we'll stop early if we exceed threshold
        
        # Get first page's first listing price to verify pagination
        prev_first_price = None
        
        while current_page <= max_pages:
            logger.info(f"\n--- Scraping page {current_page} ---")
            
            # Scroll down to listings section (page resets to top after pagination click)
            logger.info("  Scrolling down to listings...")
            await page.evaluate('window.scrollTo(0, 2000)')
            await asyncio.sleep(2)
            
            # Additional scrolls to ensure listings are loaded
            for i in range(3):
                await page.evaluate(f'window.scrollTo(0, {(i+1) * 600})')
                await asyncio.sleep(0.5)
            
            page_data = await scrape_listings_page(page, min_price=min_box_price, max_price=max_box_price)
            
            # Extract data from return format
            page_filtered_listings = page_data.get('filtered_listings', [])
            should_stop = page_data.get('should_stop', False)
            
            # Check if we're on a new page (compare first listing)
            if page_filtered_listings:
                first_price = page_filtered_listings[0]['price']
                if prev_first_price == first_price and current_page > 1:
                    logger.warning(f"  ⚠ Same listings as previous page (first price: ${first_price}) - pagination may not be working")
                prev_first_price = first_price
            
            if not page_filtered_listings:
                logger.info(f"  Page {current_page}: 0 listings in range (${min_box_price:.2f} - ${max_box_price:.2f})")
            else:
                # page_filtered_listings is already expanded (each unit = 1 listing)
                logger.info(f"  Page {current_page}: Found {len(page_filtered_listings)} unit listings in range! (first: ${page_filtered_listings[0]['price']:.2f})")
                all_listings.extend(page_filtered_listings)
            
            # Stop if all listings exceed 20% threshold
            if should_stop:
                logger.info(f"  Stopping pagination - all listings exceed 20% threshold (${max_box_price:.2f})")
                break
            
            # Try next page - click numbered pagination buttons (1, 2, 3, etc.)
            next_page_num = current_page + 1
            
            # First, find all pagination buttons to see what's available
            logger.info(f"  Looking for page {next_page_num} button...")
            all_pagination_buttons = await page.query_selector_all('[class*="pagination"] button, [class*="pagination"] a, button[aria-label*="page" i], a[aria-label*="page" i]')
            
            if all_pagination_buttons:
                logger.info(f"  Found {len(all_pagination_buttons)} pagination elements")
                # Show what we found
                for i, btn in enumerate(all_pagination_buttons[:10]):
                    try:
                        text = await btn.inner_text()
                        logger.info(f"    [{i}] '{text.strip()}'")
                    except:
                        pass
            
            # Look for the numbered button for the next page
            page_button = None
            is_arrow_button = False
            
            try:
                logger.info(f"  Looking for page {next_page_num} button...")
                
                # First, try to find the numbered button directly
                all_buttons = await page.query_selector_all('[class*="pagination"] button, [class*="pagination"] a')
                
                for btn in all_buttons:
                    try:
                        text = (await btn.inner_text()).strip()
                        classes = (await btn.get_attribute('class') or '').lower()
                        
                        # Check if this is the numbered button we want
                        if text == str(next_page_num):
                            # Check if it's the current page - primary check is if text matches current_page
                            is_current_page = (text == str(current_page))
                            
                            if is_current_page:
                                logger.info(f"  Page {next_page_num} button matches current page ({current_page}), skipping")
                                continue
                            
                            # Check if it's disabled
                            is_disabled = await btn.get_attribute('disabled')
                            aria_disabled = await btn.get_attribute('aria-disabled')
                            
                            # Check if actually disabled (disabled="true" or aria-disabled="true")
                            # Note: get_attribute returns the string value or None
                            actually_disabled = (
                                (is_disabled and is_disabled.lower() in ['true', 'disabled']) or
                                (aria_disabled and aria_disabled.lower() == 'true')
                            )
                            
                            if actually_disabled:
                                logger.info(f"  Page {next_page_num} button is disabled, skipping")
                                continue
                            
                            # Found a valid button to click
                            page_button = btn
                            logger.info(f"  ✓ Found page {next_page_num} button (text: '{text}')")
                            break
                    except:
                        continue
                
                # If no numbered button found, try the right arrow button
                if not page_button:
                    logger.info(f"  Page {next_page_num} button not found, trying right arrow...")
                    for btn in all_buttons:
                        try:
                            text = (await btn.inner_text()).strip()
                            aria_label = (await btn.get_attribute('aria-label') or '').lower()
                            
                            # Check if this is a right arrow button
                            if text in ['>', '»'] or 'next' in aria_label:
                                # Make sure it's not disabled
                                is_disabled = await btn.get_attribute('disabled')
                                aria_disabled = await btn.get_attribute('aria-disabled')
                                classes = (await btn.get_attribute('class') or '').lower()
                                
                                if not is_disabled and aria_disabled != 'true' and 'disabled' not in classes:
                                    page_button = btn
                                    is_arrow_button = True
                                    logger.info(f"  ✓ Found right arrow button (text: '{text}', aria-label: '{aria_label}')")
                                    break
                        except:
                            continue
                                
            except Exception as e:
                logger.warning(f"  Error finding pagination button: {e}")
                import traceback
                logger.warning(traceback.format_exc())
                
            if page_button:
                button_text = (await page_button.inner_text()).strip()
                is_disabled = await page_button.get_attribute('disabled')
                aria_disabled = await page_button.get_attribute('aria-disabled')
                classes = (await page_button.get_attribute('class') or '').lower()
                
                logger.info(f"  Button status - text: '{button_text}', is_arrow: {is_arrow_button}, disabled: {is_disabled}, aria-disabled: {aria_disabled}")
                
                # Check if actually disabled (disabled="true" or aria-disabled="true")
                actually_disabled = (
                    (is_disabled and is_disabled.lower() in ['true', 'disabled']) or
                    (aria_disabled and aria_disabled.lower() == 'true') or
                    'disabled' in classes
                )
                
                if actually_disabled:
                    logger.info(f"  No more pages (button disabled)")
                    break
                
                # Click the button
                button_desc = f"page {next_page_num}" if not is_arrow_button else "right arrow"
                logger.info(f"  ✓ Clicking {button_desc} button...")
                try:
                    # Scroll button into view before clicking
                    await page_button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await page_button.click()
                    logger.info(f"  ✓ Clicked {button_desc} button")
                    
                    # Wait for page to load and navigate (page will reset to top)
                    await asyncio.sleep(3)
                    
                    # Wait for listings to load
                    try:
                        await page.wait_for_selector('.listing-item', timeout=10000)
                    except:
                        logger.warning("  Listings selector not found immediately, continuing...")
                    
                    # Page resets to top after click, so we'll scroll down in the next iteration
                    # Update page number
                    if is_arrow_button:
                        current_page += 1
                    else:
                        current_page = next_page_num
                    logger.info(f"  ✓ Now on page {current_page}, will scroll to listings in next iteration")
                except Exception as e:
                    logger.error(f"  ✗ Error clicking {button_desc}: {e}")
                    break
            else:
                logger.info(f"  ✗ No page {next_page_num} button found (reached end)")
                break
        
        # all_listings only contains listings within the price range (-15% to +20%)
        listings = all_listings
        today_listings_count = len(listings)  # Count of listings within price range only
        
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
                        listings_change = today_listings_count - yesterday_count
        except Exception as e:
            logger.warning(f"Could not load historical data for comparison: {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Price range: ${min_box_price:.2f} - ${max_box_price:.2f} (market -15% to +20%)")
        logger.info(f"Total listings within range (each unit counted separately): {today_listings_count}")
        
        # Display day-over-day change (only for listings within price range)
        if yesterday_count is not None:
            change_sign = "+" if listings_change >= 0 else ""
            logger.info(f"Day-over-day change (within range): {change_sign}{listings_change} listings ({yesterday_count} yesterday → {today_listings_count} today)")
        else:
            logger.info(f"Day-over-day change: No previous data available (first run or no data for {yesterday})")
        
        if listings:
            # Each listing now represents 1 unit (expanded by quantity)
            # Group by price to show unique seller listings
            from collections import defaultdict
            price_groups = defaultdict(list)
            for l in listings:
                price_groups[(l['price'], l['seller'])].append(l)
            
            unique_seller_listings = len(price_groups)
            logger.info(f"Unique seller listings: {unique_seller_listings}")
            
            # Sort by price
            listings.sort(key=lambda x: x['price'])
            
            # Show floor price (lowest in our range)
            floor = listings[0]['price']
            highest = listings[-1]['price']
            
            logger.info(f"\nFloor Price (in range): ${floor:.2f}")
            logger.info(f"Highest Price (in range): ${highest:.2f}")
            logger.info(f"All {len(listings)} unit listings are within -15% to +20% of market price")
            
            logger.info(f"\nFirst 15 listings (sorted by price, each unit shown separately):")
            for i, l in enumerate(listings[:15]):
                unit_num = l.get('unit_number', 1)
                logger.info(f"  {i+1}. ${l['price']:.2f} - {l['seller'][:30]} (unit {unit_num})")
        else:
            logger.info("No listings found in the specified price range.")
        
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
            # Save as listings_count_in_range to make it clear this is only listings within -15% to +20% range
            if today_entry:
                today_entry['listings_count_in_range'] = today_listings_count
                today_entry['listings_count'] = today_listings_count  # Keep for backward compatibility
                today_entry['timestamp'] = datetime.now().isoformat()
                logger.info(f"Updated today's listings count (within range) in historical data: {today_listings_count}")
            else:
                # Create new entry for today
                new_entry = {
                    'date': today_str,
                    'source': 'listings_scraper',
                    'data_type': 'listings',
                    'listings_count_in_range': today_listings_count,  # Count within -15% to +20% price range
                    'listings_count': today_listings_count,  # Keep for backward compatibility
                    'price_range_min': min_box_price,
                    'price_range_max': max_box_price,
                    'timestamp': datetime.now().isoformat()
                }
                hist[box_id].append(new_entry)
                # Sort by date
                hist[box_id].sort(key=lambda x: x.get('date', ''))
                logger.info(f"Saved today's listings count (within range) to historical data: {today_listings_count}")
            
            # Save back to file
            with open(hist_file, 'w') as f:
                json.dump(hist, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save listings count to historical data: {e}")
        
        logger.info(f"\nBrowser open for 20 seconds...")
        await asyncio.sleep(20)
        await browser.close()
    
    logger.info("Done!")


if __name__ == '__main__':
    Path('logs').mkdir(exist_ok=True)
    asyncio.run(main())

