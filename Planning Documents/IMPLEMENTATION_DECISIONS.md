# Implementation Decisions & Engineering Plan

> **This document contains authoritative implementation decisions and constraints. These are locked-in requirements, not exploratory notes.**

---

## 1️⃣ Data Collection Strategy: Manual-First Approach

### Decision: ✅ RESOLVED

We are building with **manual data entry first**, then adding marketplace API integration later.

### Primary Approach: Manual Entry (MVP)

**Implementation:**
- Manual data entry via admin panel or API endpoint
- Data stored directly in `box_metrics_unified` table
- Same database schema as future API integration
- No raw data tables needed for manual mode
- See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for complete details

**Benefits:**
- Build and validate app immediately without API access
- No API costs during development
- Instant iteration and testing
- Same database structure - seamless transition later

### Future: Marketplace API Integration (Post-MVP)

**When Ready:**
- After MVP is complete and validated with manual data
- When API access is obtained (TCGGO, TCGAPIs, or eBay Developer Account)

**Implementation Rules (Future Phase):**

- **Adapter Layer:**
  - Create `TCGPlayerAdapter`
  - Create `EbayAdapter`
  - Each adapter handles: Auth, Pagination, Rate limiting, Normalization

- **Raw Data Storage:**
  - `tcg_listings_raw` - Store raw TCGplayer responses
  - `ebay_sales_raw` - Store raw eBay responses
  - No cross-market deduplication at listing level

- **API Failure Handling:**
  - Retries with exponential backoff
  - Skip + log on failure (never block pipeline)
  - Add versioning to adapters to handle API changes safely
  - Manual entry remains as backup/fallback option

**Result:** App is fully functional with manual data, API integration enhances automation without requiring frontend changes.

---

## 2️⃣ Volume Calculation Accuracy & Edge Cases

### Decision: ✅ RESOLVED

**Manual Mode:** Volume comes directly from manual entry (`boxes_sold_today` field). No inference needed.

**Future API Mode:** We do NOT attempt to perfectly infer sales. We use conservative heuristics and accept undercounting.

### Manual Mode Logic

#### Manual Entry
- **Track:**
  - Floor price (directly entered)
  - Active listings count (directly entered)
  - Boxes sold today (directly entered)
  - Daily volume USD (calculated: `boxes_sold × floor_price` or directly entered)

- **No inference needed:**
  - Sales data comes directly from manual entry
  - Volume is calculated from entered sales data
  - All metrics use entered values directly

### Future API Mode Logic

#### TCGplayer (Future)
- **Track:**
  - Total quantity on market (snapshot)
  - Floor price

- **Sales inference:**
  - Net quantity decrease between snapshots
  - Ignore price-only changes
  - Ignore same-seller relists within 24h

#### eBay (Future)
- Use ONLY completed/sold listings
- Ignore active listings entirely
- Count each completed sale as 1 unit

### Safeguards (Future API Mode)
- Log every inferred sale with reason
- Flag abnormal volume spikes
- No ML initially — deterministic logic only

**Result:** Manual mode uses entered data directly (most accurate). Future API mode will use conservative inference for volume rankings.

---

## 3️⃣ Database Performance & Scale

### Decision: ✅ CONTROLLED

All expensive calculations are precomputed.

### Implementation Strategy

- **Daily metric aggregation jobs**
- **Materialized tables:**
  - `tcg_box_metrics_daily`
  - `ebay_box_metrics_daily`
  - `box_metrics_unified`

- **Leaderboards read ONLY from unified metrics**

- **Redis cache for:**
  - Top 10 / Top 50
  - Box detail views

### Schema Strategy
- Time-partition raw snapshot tables by day
- Archive raw data after N days
- Index on: `box_id`, `date`, `volume_score`

**Result:** Rankings stay <200ms even at scale.

---

## 4️⃣ Sparkline Data Collection

### Decision: ✅ SIMPLIFIED

Daily snapshots only for MVP.

### Rationale
- Daily is sufficient for trend direction
- Frontend interpolates visually
- Hourly snapshots deferred

### Later Upgrade Path
- Add `price_snapshots_hourly` table if needed
- No schema rework required

**Result:** Fast MVP, no over-engineering.

---

## 5️⃣ Image / Asset Data

### Decision: ✅ DEFERRED SAFELY

Images are non-blocking.

### Approach
- Default placeholder image for all boxes
- Manual mapping for initial 10 boxes
- Future automation via:
  - TCGplayer metadata
  - External dataset if available

**Result:** UI is shippable without image risk.

---

## 6️⃣ Liquidity Measurement

### Decision: ✅ DEFINED

Liquidity = Absorption Speed × Depth × Consistency

### Initial Formula (Tunable)

```
Liquidity Score =
  (Boxes Sold / Boxes Listed) × 0.5
+ (7d Sales Velocity EMA) × 0.3
+ (eBay Sales Frequency) × 0.2
```

### Notes
- Liquidity is relative, not absolute
- Used for ranking & signals, not pricing
- Always smoothed (EMA)

---

## 7️⃣ Days to +20% Price Model

### Decision: ✅ BOUNDED

This is a projection, not a promise.

### Calculation (Deterministic)

```
Days to +20% =
  Remaining Boxes to Price Tier
  ÷ Average Daily Buy Rate (30d)
```

### Safeguards
- Clamp output (e.g., max 180 days)
- Hide if buy rate too low
- Label as "Projected"

**Result:** Useful signal without legal or credibility risk.

---

## 8️⃣ Reprint Risk Indicator

### Decision: ✅ HEURISTIC

Reprint risk is sentiment-based, not factual.

### Inputs
- Community votes (future)
- Known historical reprint cadence
- Manual analyst flags

### Output
- `LOW`
- `UNCONFIRMED`
- `ELEVATED`

Never numeric, never predictive.

---

## 9️⃣ Scope Control

### Decision: ✅ ENFORCED

**Explicitly Out of Scope for MVP:**
- ❌ Portfolio tracking
- ❌ Perfect sales accuracy
- ❌ Supply estimates
- ❌ ML prediction models
- ❌ Multi-language support

---

## 🔁 Implementation Phases (Locked)

> **See [BUILD_PHASES.md](./BUILD_PHASES.md) for complete, granular build phase breakdown (Phases 0-8).**

### High-Level Phases

**Phase 1 (MVP):**
- Track 10 One Piece booster boxes
- TCGplayer ingestion
- Daily metrics
- Top-10 leaderboard
- Paywalled (7-day trial)

**Phase 2:**
- Add eBay sold listings
- Momentum + demand signals
- Liquidity refinement

**Phase 3:**
- Analyst rankings
- Community sentiment
- Reprint expectations

### Detailed Build Order (BUILD_PHASES.md)

The detailed breakdown (Phases 0-8) provides:
- **Phase 0:** UX + API Planning (mock data only)
- **Phase 1:** Core Data Foundation (box registry)
- **Phase 2:** TCGplayer Ingestion (raw data)
- **Phase 3:** TCGplayer Metrics (aggregated)
- **Phase 4:** eBay Demand Signal (sold listings)
- **Phase 5:** Unified Metrics Layer (combined)
- **Phase 6:** Rankings & Caching (performance)
- **Phase 7:** API Layer (endpoints)
- **Phase 8:** Monetization (auth + payments)

**These phases must be completed sequentially.**

---

## 🧭 Guiding Rules for Implementation

1. **Conservative bias always** - Better to undercount than overcount
2. **Metrics > raw data** - Pre-compute everything possible
3. **Isolation > cleverness** - Keep marketplaces separate, don't over-engineer
4. **Ship MVP fast, validate, then iterate** - Get to working product quickly

---

## 📋 Decisions Still Needed

Based on the engineering plan, here are clarifications/decisions that may still be needed:

1. **Initial Box Set:**
   - ✅ Decided: 10 One Piece booster boxes for MVP
   - ❓ Which specific 10 boxes? (need list for Phase 1)
   - ❓ How to match TCGplayer product IDs to boxes?

2. **Archive Strategy:**
   - ❓ Archive raw data after how many days? (N = ?)
   - ❓ Move to cold storage or delete?

3. **Paywall/Authentication:**
   - ✅ Decided: 7-day trial
   - ❓ Full authentication system in Phase 1 or Phase 2?
   - ❓ Payment processing provider? (Stripe, etc.)

4. **Redis Caching:**
   - ❓ Cache TTL for leaderboards? (5 min, 1 hour?)
   - ❓ Cache invalidation strategy?

5. **Liquidity Score Tuning:**
   - ✅ Initial formula provided (50/30/20 split)
   - ❓ How to tune based on observed data? (A/B testing? Manual?)

6. **One Piece Specific:**
   - ✅ Decided: One Piece booster boxes for MVP
   - ❓ Future: Add other TCGs in Phase 2/3? (MTG, Pokemon, etc.)

7. **TCGplayer API Details:**
   - ❓ Product matching strategy? (search by name? external IDs?)
   - ❓ How to identify booster boxes vs. other products?

8. **Tech Stack Hosting:** (See TECH_STACK.md for recommendations)
   - ❓ Database hosting? (Supabase, Neon, Railway's Postgres?)
   - ❓ Redis hosting? (Redis Cloud, Upstash, Railway's Redis?)
   - ❓ Backend hosting? (Railway, Render, AWS?)
   - ❓ Mobile framework? (React Native recommended, or Flutter?)

---

## ✅ Architecture Alignment

All decisions align with the existing architecture:

- ✅ Separate marketplace adapters → Matches MARKETPLACE_STRATEGY.md
- ✅ Conservative volume calculation → Matches edge case handling
- ✅ Pre-computed metrics → Matches calculation pipeline design
- ✅ Daily snapshots only → Matches sparkline simplification
- ✅ Unified metrics table → Matches schema design
- ✅ Liquidity score formula → Can be added to unified metrics
- ✅ Phase 1: TCGplayer only → Matches implementation phases

---

## 📝 Next Steps

1. ✅ Architecture decisions locked in
2. ⚠️ **CRITICAL:** Resolve unknowns in [REMAINING_UNKNOWNS.md](./REMAINING_UNKNOWNS.md)
   - Get TCGplayer API credentials
   - Identify 10 One Piece booster boxes
   - Test product matching strategy
3. ⏳ Set up development environment
4. ⏳ Begin Phase 1 implementation (box registry)

**See [REMAINING_UNKNOWNS.md](./REMAINING_UNKNOWNS.md) for complete list of decisions needed.**

