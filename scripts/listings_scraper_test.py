#!/usr/bin/env python3
"""
Test scraper on a single box to verify everything works.
"""

import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test with OP-13 (correct URL from tcgplayer_apify.py)
TEST_URL = "https://www.tcgplayer.com/product/628352/one-piece-card-game-carrying-on-his-will-carrying-on-his-will-booster-box?Language=English"


async def test_single_box():
    """Test scraping a single box"""
    logger.info("=" * 60)
    logger.info("Testing TCGplayer Scraper on OP-13")
    logger.info("=" * 60)
    
    async with async_playwright() as p:
        logger.info("Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        # Navigate
        logger.info(f"Navigating to: {TEST_URL}")
        await page.goto(TEST_URL, wait_until='domcontentloaded', timeout=60000)
        
        # Wait for initial load
        logger.info("Waiting for initial render...")
        await asyncio.sleep(3)
        
        # Scroll down in steps to trigger lazy loading
        logger.info("Scrolling down to load listings...")
        for i in range(10):
            await page.evaluate(f'window.scrollTo(0, {(i+1) * 500})')
            await asyncio.sleep(0.5)
        
        # Scroll all the way down
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(3)
        
        # Scroll back up a bit (sometimes triggers more loading)
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
        await asyncio.sleep(2)
        
        # Take screenshot
        await page.screenshot(path='logs/test_screenshot.png', full_page=True)
        logger.info("Screenshot saved")
        
        # Get the full HTML
        html = await page.content()
        with open('logs/test_page.html', 'w') as f:
            f.write(html)
        logger.info(f"HTML saved ({len(html)} bytes)")
        
        # Look for common TCGplayer listing patterns
        logger.info("\n--- Checking for listing indicators ---")
        
        indicators = {
            '$5': 'Dollar prices',
            'Add to Cart': 'Add to Cart buttons',
            'add-to-cart': 'Add to cart class',
            'Seller': 'Seller info',
            'seller': 'Seller class',
            'Condition': 'Condition filter',
            'Sealed': 'Sealed listings',
            'Near Mint': 'Near Mint listings',
            'listing': 'Listing class',
            'Listing': 'Listing text',
        }
        
        for key, desc in indicators.items():
            count = html.count(key)
            if count > 0:
                logger.info(f"  ✓ {desc}: {count} occurrences")
            else:
                logger.info(f"  ✗ {desc}: not found")
        
        # Try clicking on "Listings" tab if it exists
        logger.info("\n--- Looking for listings tab ---")
        try:
            listings_tab = await page.query_selector('text=Listings')
            if listings_tab:
                logger.info("Found 'Listings' tab, clicking...")
                await listings_tab.click()
                await asyncio.sleep(3)
                
                # Re-capture HTML after click
                html = await page.content()
                await page.screenshot(path='logs/test_screenshot_after_click.png', full_page=True)
                logger.info("Screenshot after click saved")
        except Exception as e:
            logger.info(f"No listings tab found: {e}")
        
        # Look for actual prices
        logger.info("\n--- Looking for specific price elements ---")
        price_texts = await page.evaluate('''
            () => {
                const prices = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.innerText || '';
                    if (/^\$\d{2,3}\.\d{2}$/.test(text.trim())) {
                        prices.push(text.trim());
                    }
                });
                return [...new Set(prices)].slice(0, 20);
            }
        ''')
        if price_texts:
            logger.info(f"Found prices: {price_texts}")
        else:
            logger.info("No matching price formats found")
        
        # Check for listing rows
        logger.info("\n--- Looking for listing rows ---")
        row_selectors = [
            '.listing-item',
            '.product-listing',
            '[class*="listing-row"]',
            '[class*="ListingRow"]',
            'tr[class*="listing"]',
            '[class*="add-to-cart"]',
            'button[class*="cart"]',
        ]
        
        for sel in row_selectors:
            try:
                rows = await page.query_selector_all(sel)
                if rows:
                    logger.info(f"  ✓ {sel}: {len(rows)} elements")
            except:
                pass
        
        # Keep browser open
        logger.info("\n" + "=" * 60)
        logger.info("Browser open for 45 seconds - check the page!")
        logger.info("Look for: The listings section, seller prices, etc.")
        logger.info("=" * 60)
        
        await asyncio.sleep(45)
        await browser.close()
    
    logger.info("Test complete!")


if __name__ == '__main__':
    Path('logs').mkdir(exist_ok=True)
    asyncio.run(test_single_box())
