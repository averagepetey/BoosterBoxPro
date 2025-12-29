# BoosterBoxPro - Planning Summary

## ✅ Planning Status: COMPLETE

All architecture planning documents have been created and updated based on your UI mockup and requirements.

## 🎯 Build Strategy: Manual-First Approach

**Primary Approach:** We're building with **manual data entry first**, then adding marketplace API integration later.

This allows us to:
- ✅ Build and validate the entire app immediately without waiting for API access
- ✅ Test all functionality before investing in API costs
- ✅ Iterate quickly with instant data changes
- ✅ Use the same database schema - seamless transition to APIs later
- ✅ Frontend code requires no changes when APIs are added

See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for complete details on manual entry workflow.

---

## 📚 Planning Documents Created

1. **ARCHITECTURE_PLAN.md** - Complete system architecture
2. **UI_REQUIREMENTS.md** - UI specifications based on your mockup
3. **QUICK_REFERENCE.md** - Formulas and logic quick lookup
4. **DATA_FLOW.md** - Visual flow diagrams
5. **[README.md](../README.md)** - Project overview and navigation
6. **PLANNING_SUMMARY.md** - This file

---

## 🎨 UI Design Alignment

Your UI mockup shows a **dark-themed leaderboard table** similar to NFT marketplaces (Magic Eden/OpenSea style). The architecture has been updated to fully support this design:

### UI Columns → Data Mappings

| UI Column | Data Field | Status |
|-----------|-----------|--------|
| Rank (#) | `rank` | ✅ Added |
| Collection (name + avatar) | `product_name` + `image_url` | ✅ Added `image_url` |
| Rank change indicator | `rank_change_direction` | ✅ Added |
| Floor | `metrics.floor_price_usd` | ✅ Already had |
| Floor 1d % | `metrics.floor_price_1d_change_pct` | ✅ Added calculation |
| Volume | `metrics.daily_volume_usd` | ✅ Already had (PRIMARY) |
| Sales | `metrics.units_sold_count` | ✅ Already had |
| Listed | `metrics.listed_percentage` + counts | ✅ Added |
| Last 1d (sparkline) | `metrics.price_sparkline_1d` | ✅ Added structure |

### UI Features Supported

- ✅ Sortable columns (all major metrics)
- ✅ Color-coded changes (green ▲ for up, red ▼ for down)
- ✅ Rank change indicators (↑↓ arrows on avatars)
- ✅ Sparkline charts (price trend over 24h)
- ✅ Dark theme ready (API provides all data, styling is frontend)

---

## 🗄️ Database Schema Updates

### Added Fields

**booster_boxes table:**
- `image_url VARCHAR(500)` - Avatar/logo URL for UI display
- `estimated_total_supply INT` - Optional, for listed percentage calculation

**daily_derived_metrics table:**
- `floor_price_1d_change_pct DECIMAL(6, 2)` - 1-day floor price % change
- `listed_percentage DECIMAL(5, 2)` - Percentage of supply listed (if total_supply available)

---

## 📊 Calculation Pipeline Updates

### New Calculations Added

1. **Floor Price 1-Day Change %**
   - Compares today's floor_price to yesterday's
   - Formula: `((today_floor - yesterday_floor) / yesterday_floor) * 100`
   - Returns NULL if no previous day data

2. **Listed Percentage**
   - Formula: `(active_listings_count / estimated_total_supply) * 100`
   - Returns NULL if no total_supply estimate available
   - Falls back to absolute count display

3. **Rank Change Direction**
   - Compares current rank to previous rank
   - Returns: `"up"`, `"down"`, or `"same"`
   - Used for UI arrow indicators

4. **Sparkline Data**
   - Initial: Use daily floor_price for last 7 days
   - Future: Store hourly snapshots for smoother 24h charts

---

## 🔌 API Response Updates

### Leaderboard Endpoint (`GET /api/v1/booster-boxes`)

**Updated response shape** includes:
- `rank` - Current rank number
- `rank_change_direction` - "up"/"down"/"same" for UI arrows
- `image_url` - Collection avatar/logo
- `metrics.floor_price_1d_change_pct` - For "▼1.3%" display
- `metrics.units_sold_count` - Sales count
- `metrics.listed_percentage` - For "3,044 / 36.6K (8.3%)" display
- `metrics.price_sparkline_1d` - Array of price points for mini chart

### Sorting Support

All columns are sortable:
- `sort=volume` (default)
- `sort=market_cap`
- `sort=floor_price`
- `sort=floor_change_1d`
- `sort=sales`
- `sort=listed`

---

## 🎯 Key Decisions Made

1. ✅ **Mobile-First with Web Support** - Both platforms use same API
2. ✅ **UI-Driven Architecture** - API response shapes match table structure
3. ✅ **Volume as Primary Metric** - Most prominent in UI
4. ✅ **Sparklines** - Initial: daily data, future: hourly snapshots
5. ✅ **Rank Change Indicators** - Visual arrows for up/down movement
6. ✅ **User Favorites Feature** - Authentication required, "My List" for tracking boxes

---

## ❓ Remaining Decisions Needed

Before coding, please confirm:

1. **Marketplace APIs**
   - Which marketplace(s) first? (TCGplayer, eBay, etc.)
   - Do you have API credentials/rate limits?

2. **Images/Avatars**
   - Where will booster box images come from?
   - Marketplace API? External CDN? Manual upload?

3. **Total Supply Estimates**
   - Do marketplace APIs provide total supply data?
   - Or should we estimate from historical listings?
   - Or skip listed percentage initially?

4. **Sparkline Implementation**
   - Start with daily data (7-day sparkline)?
   - Or build hourly snapshot system from the start?

5. **Authentication Method**
   - Email/password only? ✅ (decided)
   - Social auth (Google/Apple)? (optional, future)
   - Token storage: httpOnly cookies vs localStorage? (decision needed)

6. **Mobile Framework**
   - React Native? Flutter? Native iOS/Android?
   - (Decision needed for Phase 2)

7. **Website Framework**
   - Next.js? React? Vue?
   - (Decision needed for Phase 3)

---

## 🚀 Next Steps

### Build Phases (See BUILD_PHASES.md for complete breakdown)

**Phase 0:** UX + API Planning (mock data)
**Phase 1:** Core Data Foundation (box registry)
**Phase 2:** TCGplayer Ingestion (raw data)
**Phase 3:** TCGplayer Metrics (aggregated)
**Phase 4:** eBay Demand Signal (sold listings)
**Phase 5:** Unified Metrics Layer (combined)
**Phase 6:** Rankings & Caching (performance)
**Phase 7:** API Layer (endpoints)
**Phase 8:** Monetization (auth + payments)

**MVP = Phases 1-7, Launch = Phases 1-8**

### Phase 2: Mobile App
1. ⏳ Choose mobile framework
2. ⏳ Build mobile app UI (leaderboard table)
3. ⏳ Integrate with API
4. ⏳ Test and refine

### Phase 3: Website
1. ⏳ Build responsive website
2. ⏳ Reuse mobile API
3. ⏳ Add web-specific features if needed

---

## 📝 Notes

- **UI Mockup Reviewed** ✅ - Architecture aligned with leaderboard design
- **Mobile-First Confirmed** ✅ - API optimized for mobile, web uses same endpoints
- **Favorites Feature Designed** ✅ - User auth, favorites table, My List endpoints
- **All Core Metrics Defined** ✅ - Volume, market cap, demand velocity, supply inflow, etc.
- **Edge Cases Documented** ✅ - Relists, low liquidity, missing data, etc.

---

**Ready to start coding once you confirm the remaining decisions!** 🎉


