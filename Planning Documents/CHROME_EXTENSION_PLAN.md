# Chrome Extension Plan - BoosterBoxPro Market Intelligence

## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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


## Overview

A Chrome extension that **automatically detects** which booster box you're viewing on TCGplayer or eBay and displays the **full box detail page stats** in a sidebar panel. Users get complete market intelligence without leaving the marketplace - like having the BoosterBoxPro dashboard right next to their shopping.

---

## Core Value Proposition

**"Your full dashboard, right where you shop."**

When browsing ANY booster box URL on TCGplayer or eBay:
1. **Auto-Detection**: Extension automatically identifies the box (e.g., OP-13, OP-01)
2. **Full Stats Panel**: Shows ALL box detail metrics (not just a summary)
3. **Compare Tab**: Compare current box to any other box side-by-side
4. **No Manual Lookup**: Just browse normally, data appears automatically

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

### 1. Auto-Detection (Core Feature)

**How it works:**
- Extension monitors the current URL
- Detects TCGplayer product pages: `tcgplayer.com/product/...`
- Detects eBay searches/listings: `ebay.com/sch/...` or `ebay.com/itm/...`
- Extracts product identifier (OP-13, OP-01, etc.) from URL or page title
- Automatically fetches and displays data - **NO manual lookup needed**

**Detection Methods:**
```
TCGplayer URL: /product/514680/one-piece-card-game-op13-booster-box
              → Extract "OP-13" from product name
              
eBay Search:   /sch/i.html?_nkw=op13+booster+box
              → Extract "OP-13" from search query
              
eBay Listing:  /itm/One-Piece-OP-13-Booster-Box/...
              → Extract "OP-13" from title
```

---

### 2. Full Stats Panel (Sidebar)

**Trigger:** Automatically appears when box is detected on page

**Layout:** Collapsible sidebar panel (right side of screen)

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│                                         │
│ [Box Image]                             │
│ OP-13: Carrying On His Will Booster Box          │
│                                         │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]                │
│ ───────────────────────────────────────-│
│                                         │
│ 💰 PRICING                              │
│ ┌─────────────────────────────────────┐ │
│ │ Floor Price      $124.99            │ │
│ │ 24h Change       +2.3% ▲            │ │
│ │ 30d Change       +15.7% ▲           │ │
│ │ Listing Price    $129.99 (+4.0%)    │ │
│ │ Verdict          🟡 FAIR            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📈 VOLUME & SALES                       │
│ ┌─────────────────────────────────────┐ │
│ │ Daily Volume     $2,450             │ │
│ │ 30d Volume       $73,500            │ │
│ │ 7d EMA           $2,180             │ │
│ │ Sales/Day        2.8                │ │
│ │ 30d Avg Sales    2.4                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📦 SUPPLY                               │
│ ┌─────────────────────────────────────┐ │
│ │ Active Listings  847                │ │
│ │ Added Today      +23                │ │
│ │ Liquidity Score  8.4/10             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⏱️ INVESTMENT METRICS                   │
│ ┌─────────────────────────────────────┐ │
│ │ Days to +20%     45 days            │ │
│ │ Reprint Risk     🟡 MEDIUM          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📉 PRICE HISTORY (30d)                  │
│ ┌─────────────────────────────────────┐ │
│ │ [Mini Chart Here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [View Full Dashboard →]                 │
│                                         │
└─────────────────────────────────────────┘
```

**All Stats Shown (matches Box Detail page):**
- Floor Price (current)
- 24h Price Change %
- 30d Price Change %
- Listing Price Comparison (if on a listing)
- Daily Volume USD
- 30-Day Volume USD
- 7-Day EMA Volume
- Sales Per Day
- 30-Day Average Sales
- Active Listings Count
- Boxes Added Today
- Liquidity Score
- Days to +20% Increase
- Reprint Risk Level
- Mini Price Chart (30d)

---

### 3. Compare Tab (Side-by-Side)

**Trigger:** User clicks "Compare" tab in the sidebar

**Display:** Two-column comparison view

```
┌─────────────────────────────────────────┐
│ 🎯 BoosterBoxPro          [─] [×]       │
│ ═══════════════════════════════════════ │
│ [📊 Stats]  [⚖️ Compare]  ← ACTIVE      │
│ ───────────────────────────────────────-│
│                                         │
│ 🔍 Compare to: [Search box... ▼]        │
│    Recent: OP-01, OP-03, OP-05          │
│                                         │
│ ═══════════════════════════════════════ │
│                                         │
│   CURRENT         vs      COMPARE       │
│   OP-13                   OP-01         │
│ ┌────────────────┬────────────────────┐ │
│ │ [OP-13 Image]  │  [OP-01 Image]     │ │
│ │ Carrying On... │  Romance Dawn      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💰 FLOOR PRICE                          │
│ ┌────────────────┬────────────────────┐ │
│ │ $124.99        │  $89.99            │ │
│ │                │  -28% cheaper      │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📈 30D CHANGE                           │
│ ┌────────────────┬────────────────────┐ │
│ │ +15.7% ▲       │  +8.2% ▲           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📊 DAILY VOLUME                         │
│ ┌────────────────┬────────────────────┐ │
│ │ $2,450         │  $4,200            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🏃 SALES/DAY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 2.8            │  4.1               │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 📦 ACTIVE LISTINGS                      │
│ ┌────────────────┬────────────────────┐ │
│ │ 847            │  1,203             │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 💧 LIQUIDITY                            │
│ ┌────────────────┬────────────────────┐ │
│ │ 8.4/10         │  9.1/10            │ │
│ │                │  WINNER ✓          │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ ⏱️ DAYS TO +20%                         │
│ ┌────────────────┬────────────────────┐ │
│ │ 45 days        │  62 days           │ │
│ │ WINNER ✓       │                    │ │
│ └────────────────┴────────────────────┘ │
│                                         │
│ 🎯 VERDICT                              │
│ ┌─────────────────────────────────────┐ │
│ │ OP-13 wins on: Growth Potential     │ │
│ │ OP-01 wins on: Volume, Liquidity    │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Compare Features:**
- Dropdown/search to select comparison box
- Shows recent comparisons for quick access
- Side-by-side stat comparison
- Highlights "winner" for each metric
- Summary verdict at bottom
- Quick-swap button to flip boxes

---

### 4. Extension Popup (Quick Access)

**Trigger:** Click extension icon in toolbar

**Display:** Mini dashboard for when not on a marketplace page

```
┌─────────────────────────────────┐
│ 🎯 BoosterBoxPro                │
├─────────────────────────────────┤
│ 🔍 Search boxes...              │
├─────────────────────────────────┤
│ QUICK COMPARE                   │
│ ────────────────────────────    │
│ [Box 1 ▼] vs [Box 2 ▼]         │
│ [Compare →]                     │
├─────────────────────────────────┤
│ TOP MOVERS TODAY                │
│ ────────────────────────────    │
│ 🔥 OP-13  $124.99  +5.2%       │
│ 📈 OP-05  $92.00   +3.1%       │
│ 📉 OP-02  $71.50   -2.0%       │
├─────────────────────────────────┤
│ [Open Full Dashboard]           │
│ [Settings]                      │
└─────────────────────────────────┘
```

---

### 5. Notification Badge

**When detected:** Extension icon shows badge indicating data is available

```
  ┌─────┐
  │ 🎯  │  ← Normal (no box detected)
  └─────┘
  
  ┌─────┐
  │ 🎯  │  ← Green dot = box detected, panel ready
  │  🟢 │
  └─────┘
```

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

### API Endpoints (Backend)

**1. Full Box Lookup (for Stats Panel)**

```python
@app.get("/extension/box/{set_code}")
async def extension_box_lookup(
    set_code: str,  # e.g., "OP-13", "OP-01", "EB-01"
    listing_price: float = Query(None, description="Current marketplace listing price")
):
    """
    Full box data for Chrome extension sidebar.
    Returns ALL metrics shown in box detail page.
    """
    return {
        "matched": True,
        "box": {
            "id": "uuid",
            "product_name": "OP-13: Carrying On His Will Booster Box",
            "set_code": "OP-13",
            "set_name": "Carrying On His Will",
            "game_type": "One Piece",
            "image_url": "/images/boxes/op-13.png",
            "reprint_risk": "MEDIUM",
            "dashboard_url": "https://boosterboxpro.com/box/uuid"
        },
        "metrics": {
            "floor_price_usd": 124.99,
            "floor_price_1d_change_pct": 2.3,
            "floor_price_30d_change_pct": 15.7,
            "daily_volume_usd": 2450.00,
            "unified_volume_usd": 73500.00,  # 30-day
            "unified_volume_7d_ema": 2180.00,
            "sales_per_day": 2.8,
            "boxes_sold_30d_avg": 2.4,
            "active_listings_count": 847,
            "boxes_added_today": 23,
            "liquidity_score": 8.4,
            "days_to_20pct_increase": 45
        },
        "price_history": [
            # Last 30 days for mini chart
            {"date": "2026-01-21", "floor_price_usd": 124.99},
            {"date": "2026-01-20", "floor_price_usd": 122.50},
            # ... more days
        ],
        "listing_comparison": {
            "listing_price": 129.99,
            "difference_usd": 5.00,
            "difference_pct": 4.0,
            "verdict": "fair"  # "good", "fair", "overpriced"
        }
    }
```

**2. Compare Boxes Endpoint**

```python
@app.get("/extension/compare")
async def extension_compare(
    box1: str = Query(..., description="First box set code (e.g., OP-13)"),
    box2: str = Query(..., description="Second box set code (e.g., OP-01)")
):
    """
    Compare two boxes side-by-side.
    Returns both boxes' full metrics for comparison view.
    """
    return {
        "box1": { ... },  # Same structure as /extension/box response
        "box2": { ... },
        "comparison": {
            "floor_price_winner": "box2",  # or "box1" or "tie"
            "growth_winner": "box1",
            "volume_winner": "box2",
            "liquidity_winner": "box2",
            "sales_winner": "box2",
            "investment_winner": "box1",  # days to +20%
            "summary": "OP-01 is more liquid and sells faster. OP-13 has better growth potential."
        }
    }
```

**3. Search Boxes (for Compare dropdown)**

```python
@app.get("/extension/search")
async def extension_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Max results")
):
    """
    Quick search for Compare feature dropdown.
    """
    return {
        "results": [
            {"set_code": "OP-01", "name": "Romance Dawn", "floor_price": 89.99},
            {"set_code": "OP-02", "name": "Paramount War", "floor_price": 71.50},
            # ...
        ]
    }
```

**4. Top Movers (for Popup)**

```python
@app.get("/extension/top-movers")
async def extension_top_movers():
    """
    Top movers for extension popup quick view.
    """
    return {
        "gainers": [
            {"set_code": "OP-13", "name": "Carrying On His Will", "price": 124.99, "change_pct": 5.2},
            # ...
        ],
        "losers": [
            {"set_code": "OP-02", "name": "Paramount War", "price": 71.50, "change_pct": -2.0},
            # ...
        ]
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

### Phase 1: Core Detection + Stats Panel (Week 1)
- [ ] Project structure (Manifest V3)
- [ ] URL detection for TCGplayer product pages
- [ ] Set code extraction from URL/page
- [ ] `/extension/box/{set_code}` API endpoint
- [ ] Full stats sidebar panel UI
- [ ] Auto-open when box detected
- [ ] Collapse/expand functionality
- [ ] Mini price chart (30d)

### Phase 2: Compare Feature (Week 2)
- [ ] Compare tab UI
- [ ] `/extension/compare` API endpoint
- [ ] `/extension/search` API endpoint
- [ ] Box search dropdown
- [ ] Side-by-side comparison view
- [ ] "Winner" highlighting
- [ ] Recent comparisons memory

### Phase 3: eBay + Popup (Week 3)
- [ ] eBay URL detection (search + listings)
- [ ] eBay content script
- [ ] Extension popup UI
- [ ] `/extension/top-movers` endpoint
- [ ] Quick compare from popup
- [ ] Badge indicator when box detected

### Phase 4: Polish + Launch (Week 4)
- [ ] Caching layer (reduce API calls)
- [ ] Error handling & offline states
- [ ] Settings page (position, auto-open)
- [ ] Performance optimization
- [ ] Chrome Web Store assets
- [ ] Privacy policy
- [ ] Submit to Chrome Web Store

### Future Enhancements
- [ ] Firefox support
- [ ] Price alerts
- [ ] Auth integration (for premium features)
- [ ] Watchlist sync
- [ ] Dark/light theme toggle

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

