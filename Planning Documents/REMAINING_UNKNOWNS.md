# Remaining Unknowns & Decisions Needed

> **This document lists all decisions and information still needed before starting implementation. Items are prioritized by criticality for Phase 1.**

---

## 🔴 CRITICAL (Block Phase 1 Start)

### 1. TCGplayer Data Collection Method

**Status:** ⚠️ NEEDS DECISION - Multiple Options Available

**Options Under Consideration:**

1. **API Services** (Recommended for MVP)
   - **TCGAPIs** (tcgapis.com) - £199/month Business plan (see API_SERVICE_ANALYSIS.md)
   - **TCGGO** (tcggo.com) - Free tier available (100 requests/day) - **NEEDS VERIFICATION** (see TCGGO_API_ANALYSIS.md)
   - **Pros:** Reliable, legal, faster development
   - **Cons:** Cost (TCGAPIs) or feature limitations (TCGGO)

2. **Scraping Agent** (Alternative/Backup)
   - Browser automation with human behavior simulation
   - See SCRAPING_AGENT_DESIGN.md for architecture
   - **Pros:** Free, full control
   - **Cons:** Complex, maintenance burden, legal/ethical risks, detection risk

**Decision Needed:**
- [ ] Choose primary method (API vs. scraping)
- [ ] If API: Which service? (TCGGO free vs. TCGAPIs Business)
- [ ] If scraping: Accept 60-80% detection risk within 2-3 months?
- [ ] Consider hybrid approach (API primary, scraping backup)

**Detection Risk Assessment:**
- See [TCGPLAYER_DETECTION_ASSESSMENT.md](./TCGPLAYER_DETECTION_ASSESSMENT.md)
- **Scraping Detection Likelihood:** 60-80% within 2-3 months (even with good evasion)
- **API Detection Likelihood:** 0% (legal, authorized access)

**Recommendation:** Start with API service (TCGGO if verified, else TCGAPIs), develop scraping agent as backup/alternative. Scraping has high detection risk even with excellent evasion.

**What We Need:**
- [ ] **Plan Selection** - Which TCGAPIs plan? (See analysis below)
- [ ] TCGAPIs API credentials (API keys)
- [ ] API documentation (endpoints, request/response formats)
- [ ] Rate limits (requests per minute/hour/day)
- [ ] Authentication method

**Why Critical:**
- Phase 2 (TCGplayer Ingestion) cannot start without this
- Need to understand data format before building adapter
- Rate limits determine polling strategy
- Plan selection affects MVP feasibility

**Plan Analysis:**

**Free Plan (£0/month):**
- ✅ Free
- ❌ No API calls - CSV downloads only
- ❌ No pricing information access
- ❌ No sales history access
- ❌ Cannot do daily snapshots programmatically
- **Verdict:** ❌ Not suitable for MVP (we need API calls, not CSV downloads)

**Hobby Plan (£49/month):**
- ✅ 10,000 API calls/month
- ✅ API access (not just CSV)
- ❌ **No pricing information access**
- ❌ **No sales history access**
- **Verdict:** ❌ Missing critical features (pricing + sales data)

**Business Plan (£199/month):**
- ✅ 50,000 API calls/month
- ✅ **Pricing information access** (needed for floor price)
- ✅ **Sales history data access** (needed for volume calculation)
- ✅ All features from Hobby plan
- **Verdict:** ✅ **MINIMUM VIABLE PLAN** for MVP

**Unlimited Plan (£499/month):**
- ✅ Unlimited API calls
- ✅ Live TCGPlayer listings access (better than Business?)
- ✅ All Business features
- **Verdict:** ⚠️ Overkill for MVP, but might be better if "live listings" is needed

**Recommendation:**
- **MVP:** Business Plan (£199/month) - Has pricing + sales history
- **Alternative:** Test if Hobby Plan can work (if pricing/sales not needed, but unlikely)
- **Budget Constraint:** If £199/month is too expensive, consider:
  - CSV downloads (Free plan) + manual processing (not scalable)
  - Alternative data sources
  - Start with smaller scope (fewer boxes, less frequent updates)

**Action:** 
1. Decide on TCGAPIs plan (Business recommended for MVP)
2. Sign up for chosen plan
3. Get API credentials and review documentation

---

### 2. Specific 10 One Piece Booster Boxes

**Status:** ❓ Unknown

**What We Need:**
- [ ] List of 10 specific One Piece booster boxes for MVP
- [ ] Product names (exact as they appear on TCGplayer)
- [ ] TCGplayer product IDs (if known)
- [ ] How to identify/match boxes to TCGplayer products

**Why Critical:**
- Phase 1 (Box Registry) requires this list
- Need to manually register these 10 boxes
- Need mapping strategy (name matching? external IDs?)

**Action:** Create list of 10 One Piece boxes, identify TCGplayer product IDs

**Example Format Needed:**
```
1. One Piece Booster Box - Romance Dawn
   - TCGplayer Product ID: 12345
   - Release Date: 2023-01-01
   
2. One Piece Booster Box - Paramount War
   - TCGplayer Product ID: 12346
   - Release Date: 2023-06-01
   
... (8 more)
```

---

### 3. Product Matching Strategy

**Status:** ❓ Unknown

**What We Need:**
- [ ] How to match box names to TCGplayer product IDs?
   - Manual mapping? (recommended for 10 boxes)
   - Search API? (if TCGplayer has search endpoint)
   - External dataset? (if available)
- [ ] How to identify "booster boxes" vs. other products?
   - Category filters?
   - Product type field?
   - Manual verification?

**Why Critical:**
- Need to link our box registry to TCGplayer products
- Prevents ingesting wrong products

**Action:** Decide on matching strategy, test with sample boxes

---

## 🟡 IMPORTANT (Before Phase 2-3)

### 4. eBay API Access & Documentation

**Status:** ❓ Unknown (Phase 4 dependency)

**What We Need:**
- [ ] eBay API credentials (App ID, OAuth, etc.)
- [ ] API documentation (sold listings endpoint)
- [ ] Rate limits
- [ ] How to filter for "completed/sold" listings only
- [ ] How to search by product name (One Piece booster boxes)
- [ ] Pricing/cost structure

**Why Important:**
- Phase 4 (eBay Demand Signal) needs this
- Can defer until after Phase 3, but good to know early

**Action:** Get eBay API access, understand sold listings API

---

### 5. Archive Strategy

**Status:** ❓ Unknown

**What We Need:**
- [ ] Archive raw data after how many days? (30? 90? 365?)
- [ ] Move to cold storage or delete?
- [ ] Which tables to archive? (listing_snapshots, sales_raw, etc.)
- [ ] Archive format? (S3? Database backup? CSV export?)

**Why Important:**
- Affects database schema (partitioning strategy)
- Storage costs
- Can be decided during Phase 2, but good to plan early

**Action:** Decide retention policy, plan archive strategy

---

### 6. Redis Caching Strategy

**Status:** ❓ Partially Known

**What We Need:**
- [ ] Cache TTL for leaderboards? (5 min? 15 min? 1 hour?)
- [ ] Cache invalidation strategy?
   - Time-based only? (TTL)
   - Event-based? (invalidate on new metrics)
- [ ] What to cache?
   - Top 10 leaderboard
   - Top 50 leaderboard
   - Individual box details
   - Time-series data?

**Why Important:**
- Phase 6 (Rankings & Caching) needs this
- Affects performance requirements

**Action:** Define caching strategy, test TTL values

---

### 7. Authentication Details

**Status:** ❓ Partially Known

**What We Need:**
- [ ] JWT token expiration? (1 hour? 24 hours?)
- [ ] Refresh tokens? (yes/no)
- [ ] Token storage strategy?
   - Mobile: Keychain/Keystore (decided)
   - Web: httpOnly cookie vs. localStorage?
- [ ] 7-day trial implementation:
   - Trial starts on registration?
   - Trial starts on first API call?
   - How to track trial expiration?

**Why Important:**
- Phase 8 (Monetization) needs this
- Can be refined during implementation

**Action:** Define auth flow, token strategy

---

### 8. Payment Processing

**Status:** ❓ Unknown

**What We Need:**
- [ ] Payment provider? (Stripe recommended)
- [ ] Stripe account setup?
- [ ] Pricing model?
   - Monthly subscription?
   - One-time payment?
   - Tiered pricing?
- [ ] Subscription management?
   - Cancel anytime?
   - Refund policy?

**Why Important:**
- Phase 8 (Monetization) needs this
- Can be decided later, but good to plan

**Action:** Set up Stripe account, define pricing

---

## 🟢 NICE-TO-HAVE (Can Decide Later)

### 9. Hosting Platform Decisions

**Status:** ❓ Recommendations Provided

**What We Need:**
- [ ] Backend hosting: Railway, Render, or other?
- [ ] Database hosting: Supabase, Neon, or Railway's Postgres?
- [ ] Redis hosting: Redis Cloud, Upstash, or Railway's Redis?
- [ ] Domain name?
- [ ] SSL certificate strategy? (usually auto-provided)

**Why Nice-to-Have:**
- Can use free tiers initially
- Can migrate later if needed
- Recommendations provided in TECH_STACK.md

**Action:** Choose hosting providers (can start with free tiers)

---

### 10. Mobile Framework Choice

**Status:** ❓ Recommendation Provided

**What We Need:**
- [ ] React Native (recommended) or Flutter?
- [ ] iOS development account? (for App Store)
- [ ] Android developer account? (for Play Store)

**Why Nice-to-Have:**
- Frontend comes after backend (Phase 7+)
- Can decide during Phase 0 or Phase 7
- React Native recommended for faster development

**Action:** Choose mobile framework (can defer)

---

### 11. Monitoring & Logging

**Status:** ❓ Optional for MVP

**What We Need:**
- [ ] Error tracking: Sentry or other?
- [ ] Log aggregation: Cloud provider logs or dedicated service?
- [ ] Metrics: Prometheus/Grafana or managed service?
- [ ] Uptime monitoring?

**Why Nice-to-Have:**
- Can add after MVP launch
- Basic logging sufficient for Phase 1-7

**Action:** Can defer until after MVP

---

### 12. Liquidity Score Tuning Strategy

**Status:** ❓ Formula Defined, Tuning Unknown

**What We Need:**
- [ ] How to tune 50/30/20 split based on observed data?
   - Manual adjustment?
   - A/B testing?
   - Data analysis?
- [ ] When to tune? (after 30 days? 90 days?)

**Why Nice-to-Have:**
- Formula is defined (can use initial values)
- Tuning can happen after real data collection

**Action:** Can defer until Phase 5+ when we have real data

---

### 13. Image Source Strategy

**Status:** ❓ Deferred (Placeholders for MVP)

**What We Need:**
- [ ] Where do box images come from?
   - TCGplayer API? (if available)
   - Scraping? (legal/technical considerations)
   - Manual upload? (for 10 boxes, manageable)
   - External dataset?
- [ ] Image storage: CDN? S3? Database?

**Why Nice-to-Have:**
- Placeholders work for MVP
- Can add real images incrementally

**Action:** Can defer, use placeholders initially

---

### 14. Future TCG Expansion

**Status:** ❓ Future Consideration

**What We Need:**
- [ ] When to add other TCGs? (MTG, Pokemon, etc.)
- [ ] Same architecture for all TCGs?
- [ ] Separate leaderboards per TCG?

**Why Nice-to-Have:**
- Out of scope for MVP (One Piece only)
- Can plan after MVP launch

**Action:** Can defer until after MVP

---

## 📋 Pre-Phase 1 Checklist

**Must Have Before Starting Phase 1:**

- [ ] TCGplayer API credentials obtained
- [ ] TCGplayer API documentation reviewed
- [ ] List of 10 One Piece booster boxes created
- [ ] Product matching strategy decided (manual mapping for 10 boxes)
- [ ] TCGplayer product IDs identified for all 10 boxes

**Can Defer (But Good to Know):**

- [ ] eBay API access (needed for Phase 4)
- [ ] Hosting platform chosen (can use free tiers)
- [ ] Archive strategy (can decide during Phase 2)
- [ ] Caching strategy (can refine during Phase 6)
- [ ] Auth details (can refine during Phase 8)

---

## 🎯 Immediate Next Steps

### Before Phase 1 (Box Registry):

1. **Get TCGplayer API Access**
   - Sign up for TCGplayer API (if available)
   - Review API documentation
   - Understand rate limits and authentication

2. **Identify 10 One Piece Boxes**
   - Research popular One Piece booster boxes
   - Create list with exact names
   - Find TCGplayer product IDs (manual search or API)

3. **Test Product Matching**
   - Try to find TCGplayer product IDs for sample boxes
   - Verify matching strategy works
   - Document any challenges

### During Phase 0 (If Doing UX Planning):

4. **Finalize UI Mockups**
   - Leaderboard design
   - Box detail screen
   - Navigation structure

5. **Lock API Response Shapes**
   - Define exact JSON structures
   - Create mock data files
   - Frontend can start with mocks

---

## ❓ Questions to Answer

### TCGplayer-Specific:

1. Does TCGplayer have a public API? (or is it partner-only?)
2. What authentication method does TCGplayer API use?
3. How do we search for products by name?
4. How do we get listings for a specific product?
5. What fields are available in listing data? (price, quantity, seller, etc.)
6. How do we identify "booster boxes" vs. other product types?
7. Are product images available via API?

### eBay-Specific (For Phase 4):

1. Which eBay API? (REST? GraphQL? Finding API?)
2. How to filter for "completed/sold" listings only?
3. How to search by product name (One Piece booster boxes)?
4. What data is available in sold listings? (price, date, quantity?)
5. Rate limits for sold listings API?

### General:

1. Do we have budget for API costs? (if any)
2. Preferred hosting region? (US? EU?)
3. Team size? (solo? small team?)
4. Timeline expectations? (MVP in X weeks/months?)

---

## ✅ What We Already Know

**Decided:**
- ✅ Tech stack (Python, FastAPI, PostgreSQL, Redis, Celery)
- ✅ Marketplace strategy (TCGplayer primary, eBay secondary)
- ✅ Volume calculation approach (conservative heuristics)
- ✅ Database schema (per-marketplace + unified)
- ✅ Build phases (0-8, sequential)
- ✅ MVP scope (10 One Piece boxes, TCGplayer only initially)
- ✅ Engineering principles (conservative, precompute, isolation)

**These are locked and ready to implement once unknowns are resolved.**

---

## 🚀 Recommendation

**Start with these 3 critical items:**

1. **Get TCGplayer API access** - This is the blocker
2. **Create list of 10 One Piece boxes** - Needed for Phase 1
3. **Test product matching** - Verify we can link boxes to TCGplayer

Once these are done, Phase 1 (Box Registry) can begin immediately.

Everything else can be decided/refined during implementation or can use recommended defaults from TECH_STACK.md.

