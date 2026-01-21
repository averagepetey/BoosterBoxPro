# Chrome Extension Plan - BoosterBoxPro Market Intelligence

## Overview

A Chrome extension that overlays BoosterBoxPro market data directly on TCGplayer and eBay product pages, so users can see real-time floor prices, sales velocity, and trends without leaving the marketplace.

---

## Core Value Proposition

**"See market intelligence while you shop."**

When browsing a booster box listing on TCGplayer or eBay, users instantly see:
- Our tracked floor price vs. the listing price
- Is this a good deal? (price comparison indicator)
- Sales velocity (how fast is this box selling?)
- Price trend (up/down over 30 days)
- Quick link to full BoosterBoxPro dashboard

---

## Target Marketplaces

### Phase 1 (MVP)
1. **TCGplayer** - Primary marketplace for TCG boxes
   - Product pages: `tcgplayer.com/product/*`
   - Search results: `tcgplayer.com/search/*`

### Phase 2
2. **eBay** - Secondary marketplace
   - Listings: `ebay.com/itm/*`
   - Search results: `ebay.com/sch/*`

---

## User Stories

1. **As a collector**, I want to see the market floor price when viewing a TCGplayer listing, so I know if I'm getting a good deal.

2. **As an investor**, I want to see sales velocity on eBay listings, so I know if a box is liquid/easy to resell.

3. **As a user**, I want a quick link to the full BoosterBoxPro dashboard from any listing, so I can dive deeper into the data.

4. **As a user**, I want the extension to be non-intrusive, so it doesn't slow down my browsing.

---

## Feature Specification

### 1. Product Page Overlay

**Trigger:** When user views a booster box product page on TCGplayer/eBay

**Display:** Small floating card/badge near the price showing:

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ Floor Price: $89.99             │
│ This listing: $94.99 (+5.5%)    │
│ ────────────────────────────    │
│ Sales/day: 2.3 📈               │
│ 30d trend: +12.4% ▲             │
│ ────────────────────────────    │
│ [View Full Data →]              │
└─────────────────────────────────┘
```

**Color Coding:**
- 🟢 Green: Listing price ≤ floor price (good deal)
- 🟡 Yellow: Listing price 1-10% above floor (fair)
- 🔴 Red: Listing price >10% above floor (overpriced)

### 2. Search Results Enhancement

**Trigger:** When user views search results with multiple listings

**Display:** Small badge on each recognized booster box:

```
┌──────────────────────────────────────┐
│ [Box Image] OP-01 Romance Dawn       │
│ $94.99                               │
│ 🎯 Floor: $89.99 | 2.3/day          │
└──────────────────────────────────────┘
```

### 3. Extension Popup

**Trigger:** Click extension icon in toolbar

**Display:** Quick dashboard showing:
- User's tracked/favorite boxes
- Recent price alerts
- Quick search for any box
- Link to full dashboard

```
┌─────────────────────────────────┐
│ BoosterBoxPro                   │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ YOUR WATCHLIST                  │
│ ────────────────────────────    │
│ OP-01 Romance Dawn  $89.99 ▲2%  │
│ OP-03 Pillars       $78.50 ▼1%  │
│ OP-05 Awakening     $92.00 ─    │
├─────────────────────────────────┤
│ [Open Dashboard]                │
│ [Settings]                      │
└─────────────────────────────────┘
```

### 4. Price Alerts (Future)

- Set alerts for specific boxes
- Get notified when a listing is below your target price
- Browser notification when alert triggers

---

## Technical Architecture

### Extension Structure

```
chrome-extension/
├── manifest.json          # Extension manifest (V3)
├── background.js          # Service worker for API calls
├── content/
│   ├── tcgplayer.js      # Content script for TCGplayer
│   ├── tcgplayer.css     # Styles for TCGplayer overlay
│   ├── ebay.js           # Content script for eBay
│   └── ebay.css          # Styles for eBay overlay
├── popup/
│   ├── popup.html        # Extension popup UI
│   ├── popup.js          # Popup logic
│   └── popup.css         # Popup styles
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── utils/
    ├── api.js            # API client for BoosterBoxPro
    └── storage.js        # Chrome storage helpers
```

### Manifest V3 (Required for Chrome Web Store)

```json
{
  "manifest_version": 3,
  "name": "BoosterBoxPro - Market Intelligence",
  "version": "1.0.0",
  "description": "See real-time market data on TCGplayer and eBay",
  
  "permissions": [
    "storage",
    "activeTab"
  ],
  
  "host_permissions": [
    "https://www.tcgplayer.com/*",
    "https://tcgplayer.com/*",
    "https://www.ebay.com/*",
    "https://ebay.com/*",
    "https://api.boosterboxpro.com/*"
  ],
  
  "background": {
    "service_worker": "background.js"
  },
  
  "content_scripts": [
    {
      "matches": ["https://*.tcgplayer.com/*"],
      "js": ["content/tcgplayer.js"],
      "css": ["content/tcgplayer.css"]
    },
    {
      "matches": ["https://*.ebay.com/*"],
      "js": ["content/ebay.js"],
      "css": ["content/ebay.css"]
    }
  ],
  
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

### Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Content Script │───▶│ Background      │───▶│ BoosterBoxPro   │
│  (TCGplayer/    │    │ Service Worker  │    │ API             │
│   eBay page)    │◀───│                 │◀───│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                                              │
        │                                              │
        ▼                                              ▼
┌─────────────────┐                         ┌─────────────────┐
│  Overlay UI     │                         │  /extension/    │
│  (injected)     │                         │  lookup?name=   │
└─────────────────┘                         └─────────────────┘
```

### API Endpoint (Backend)

Need to add a new endpoint to FastAPI:

```python
@app.get("/extension/lookup")
async def extension_lookup(
    product_name: str = Query(..., description="Product name from marketplace"),
    marketplace: str = Query("tcgplayer", description="tcgplayer or ebay"),
    listing_price: float = Query(None, description="Current listing price")
):
    """
    Quick lookup for Chrome extension.
    Returns minimal data for fast overlay rendering.
    """
    return {
        "matched": True,
        "box_id": "uuid",
        "product_name": "OP-01 Romance Dawn Booster Box",
        "floor_price_usd": 89.99,
        "sales_per_day": 2.3,
        "trend_30d_pct": 12.4,
        "trend_direction": "up",  # up, down, flat
        "listing_comparison": {
            "difference_pct": 5.5,
            "verdict": "fair"  # good, fair, overpriced
        },
        "dashboard_url": "https://boosterboxpro.com/box/uuid"
    }
```

---

## Product Name Matching

### Challenge
TCGplayer and eBay have different naming conventions than our database.

**Examples:**
- TCGplayer: "One Piece Card Game Romance Dawn [OP-01] Booster Box"
- eBay: "One Piece OP-01 Romance Dawn Booster Box SEALED"
- Our DB: "One Piece TCG: Romance Dawn (OP-01) Booster Box"

### Solution: Fuzzy Matching

1. **Extract key identifiers:**
   - Set code: `OP-01`, `OP-02`, etc.
   - Set name: "Romance Dawn", "Paramount War"
   - Product type: "Booster Box"

2. **Matching logic:**
   ```python
   def match_product(marketplace_name: str) -> Optional[BoosterBox]:
       # 1. Extract set code (OP-XX, EB-XX, PRB-XX)
       set_code = extract_set_code(marketplace_name)  # "OP-01"
       
       # 2. If set code found, match by set code
       if set_code:
           return db.query(BoosterBox).filter(
               BoosterBox.product_name.ilike(f"%{set_code}%")
           ).first()
       
       # 3. Fuzzy match on product name
       return fuzzy_search(marketplace_name, all_boxes)
   ```

3. **Caching:**
   - Cache matched products in extension storage
   - TTL: 24 hours
   - Reduces API calls on repeated visits

---

## UI/UX Design

### Overlay Styling

```css
/* Dark theme matching BoosterBoxPro */
.bbp-overlay {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 280px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 999999;
}

.bbp-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
}

.bbp-price-good { color: #22c55e; }
.bbp-price-fair { color: #eab308; }
.bbp-price-high { color: #ef4444; }

.bbp-trend-up { color: #22c55e; }
.bbp-trend-down { color: #ef4444; }
.bbp-trend-flat { color: #6b7280; }
```

### Minimized State

User can minimize the overlay to just a small icon:

```
┌─────┐
│ 🎯  │  ← Click to expand
└─────┘
```

### Settings

- Toggle overlay on/off per site
- Choose overlay position (bottom-right, bottom-left, etc.)
- Enable/disable search results enhancement
- Sign in to sync watchlist

---

## Authentication (Optional)

### Free Tier (No Login)
- Basic price data
- Floor price comparison
- Sales velocity

### Premium Tier (Logged In)
- Personal watchlist sync
- Price alerts
- Historical data in popup
- Priority API access

### Auth Flow
1. User clicks "Sign In" in popup
2. Opens BoosterBoxPro login page in new tab
3. After login, redirects back with auth token
4. Extension stores token in chrome.storage.sync
5. All API calls include Bearer token

---

## Development Phases

### Phase 1: MVP (Week 1)
- [ ] Basic manifest and structure
- [ ] TCGplayer content script (product pages only)
- [ ] Simple overlay with floor price
- [ ] API endpoint for lookups
- [ ] Basic popup with search

### Phase 2: Enhanced (Week 2)
- [ ] Full overlay with all metrics
- [ ] Search results enhancement
- [ ] eBay support
- [ ] Caching layer
- [ ] Settings page

### Phase 3: Premium (Week 3)
- [ ] Authentication integration
- [ ] Watchlist sync
- [ ] Price alerts
- [ ] Badge notifications

### Phase 4: Polish (Week 4)
- [ ] Performance optimization
- [ ] Error handling
- [ ] Analytics
- [ ] Chrome Web Store submission

---

## Chrome Web Store Requirements

### Required Assets
- 128x128 icon
- 440x280 screenshot (at least 1)
- 1280x800 screenshot (promotional, optional)
- Detailed description (up to 132 characters summary)
- Privacy policy URL

### Review Checklist
- [ ] No remote code execution
- [ ] Clear permission justifications
- [ ] Privacy policy in place
- [ ] No data collection without consent
- [ ] Proper error handling
- [ ] Works offline gracefully

### Estimated Review Time
- First submission: 1-3 business days
- Updates: Usually same day

---

## Privacy Considerations

### Data Collected
- URLs visited (only on tcgplayer.com and ebay.com)
- Product names viewed (for matching)
- Optional: User ID if logged in

### Data NOT Collected
- Browsing history outside target sites
- Personal information
- Payment information

### Privacy Policy Required
- Must explain what data is collected
- Must explain how data is used
- Must provide opt-out options

---

## Performance Targets

- Overlay render time: < 500ms
- API lookup time: < 200ms
- Memory usage: < 50MB
- No impact on page load time

---

## Success Metrics

1. **Installs:** Target 1,000 in first month
2. **Daily Active Users:** 30% of installs
3. **Clicks to Dashboard:** Track conversion from extension
4. **User Ratings:** Target 4.5+ stars

---

## Next Steps

1. **Set up extension project structure**
2. **Create API endpoint for lookups**
3. **Build TCGplayer content script**
4. **Design and build overlay UI**
5. **Test on real TCGplayer pages**
6. **Submit to Chrome Web Store**

---

## Questions to Answer

1. Should the extension be free or part of premium?
2. What's the API rate limit for extension users?
3. Do we need eBay support at launch?
4. Should we support Firefox as well?

