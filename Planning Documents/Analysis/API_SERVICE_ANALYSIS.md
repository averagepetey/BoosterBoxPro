# API Service Analysis

> **Note:** This analysis is for **future API integration** (Phase 2B, post-MVP). We are building with **manual data entry first**. See **[MANUAL_FIRST_APPROACH.md](../MANUAL_FIRST_APPROACH.md)** for current build strategy. & Comparison

## Services Under Consideration

1. **TCGAPIs** (tcgapis.com) - Provides TCGplayer data access
2. **TCGGO** (tcggo.com) - Alternative API service (see TCGGO_API_ANALYSIS.md)

---

## TCGAPIs Service Analysis

**TCGAPIs** (tcgapis.com) provides API access to TCGplayer data without requiring TCGplayer API keys directly.

---

## Plan Comparison for MVP Requirements

### Our MVP Data Needs

For Phase 2 (TCGplayer Ingestion), we need:
1. ✅ **Active listings** (prices, quantities) - for floor price, market cap
2. ✅ **Pricing information** - for floor price calculation
3. ✅ **Sales history** - for volume calculation (inferred from listing changes)
4. ✅ **API access** - for automated daily snapshots (not CSV downloads)

---

## Plan Analysis

### Free Plan (£0/month)

**Features:**
- Unlimited CSV downloads
- Complete game datasets
- Access to all 40+ trading card games
- Professional CSV format
- Community support

**Limitations:**
- ❌ **No API calls** - CSV downloads only
- ❌ **No pricing information access** (not mentioned)
- ❌ **No sales history access** (not mentioned)

**Verdict:** ❌ **NOT SUITABLE FOR MVP**

**Why:**
- We need programmatic API access for daily snapshots
- CSV downloads require manual processing (not scalable)
- Pricing and sales data are critical features not available

**Could work if:**
- We manually download CSVs daily (not feasible)
- We only need catalog data (we need listings/pricing)

---

### Hobby Plan (£49/month)

**Features:**
- 10,000 API calls per month
- 1,000 card recognition calls
- Basic card catalog data
- CSV downloads included
- Email support
- No API keys required for any platform

**Limitations:**
- ❌ **Explicitly states: "No pricing information access"**
- ❌ **Explicitly states: "No sales history access"**

**Verdict:** ❌ **NOT SUITABLE FOR MVP**

**Why:**
- Missing two critical features:
  - Pricing information (needed for floor price)
  - Sales history (needed for volume calculation)
- We cannot calculate key metrics without these

**Could work if:**
- We only needed catalog data (we don't)
- Pricing/sales aren't critical (they are)

---

### Business Plan (£199/month)

**Features:**
- 50,000 API calls per month
- 5,000 card recognition calls
- Unlimited PSA Checker API calls
- Everything in Hobby plan
- ✅ **Pricing information access**
- ✅ **Sales history data access**
- Priority support
- Custom data exports

**Verdict:** ✅ **MINIMUM VIABLE PLAN FOR MVP**

**Why:**
- Has all critical features:
  - API access (50k calls/month is plenty)
  - Pricing information (floor price calculation)
  - Sales history (volume calculation)
- Includes all Hobby features plus what we need

**Cost Analysis:**
- 50,000 calls/month = ~1,667 calls/day
- For 10 boxes, daily snapshots: ~10 calls/day
- Plenty of headroom for development, testing, errors

---

### Unlimited Plan (£499/month)

**Features:**
- Unlimited API calls
- 50,000 card recognition calls
- Unlimited PSA Checker API calls
- Everything in Business plan
- ✅ **Live TCGPlayer listings access** (enhanced)
- SKU ID pricing access
- Dedicated account manager
- Custom integrations
- SLA guarantees

**Verdict:** ⚠️ **OVERSIZED FOR MVP, BUT POTENTIALLY BETTER**

**Questions:**
- What's the difference between Business "pricing information" and Unlimited "live listings"?
- Is "live listings" just more real-time, or better data?
- Could Business plan work initially, upgrade later?

**Recommendation:** Start with Business, upgrade if needed

---

## MVP Cost Analysis

### Using Business Plan

**Monthly Cost:** £199/month (~$250 USD/month)

**API Usage Estimate (MVP - 10 boxes):**
- Daily snapshot: ~10 API calls (10 boxes × 1 call each)
- Monthly: ~300 calls (30 days × 10 calls)
- **Usage: <1% of 50,000 limit** - Plenty of headroom

**Scaling (Future - 100 boxes):**
- Daily snapshot: ~100 API calls
- Monthly: ~3,000 calls
- **Still only 6% of limit** - Can scale significantly

**Cost per Box (MVP):**
- £199 / 10 boxes = £19.90/month per box
- At scale (100 boxes): £199 / 100 = £1.99/month per box

---

## Free Plan Alternatives (If Budget Constrained)

### Option 1: Manual CSV Processing (Not Recommended)

**Approach:**
- Use Free plan CSV downloads
- Manually download daily
- Parse CSV files in code
- Store data

**Pros:**
- £0/month cost

**Cons:**
- ❌ Not automated (manual daily work)
- ❌ Not scalable
- ❌ No pricing/sales data in CSV (likely)
- ❌ Time-consuming
- ❌ Not suitable for production

**Verdict:** Only viable for very early testing/proof-of-concept

---

### Option 2: Alternative Data Sources

**Options:**
- Direct TCGplayer scraping (legal/ethical concerns)
- Other TCG data APIs (if they exist)
- Manual data entry (not feasible)

**Verdict:** Not viable alternatives

---

### Option 3: Reduced Scope MVP

**Approach:**
- Start with fewer boxes (5 instead of 10)
- Less frequent updates (every 2-3 days instead of daily)
- Still need Business plan for pricing/sales data

**Verdict:** Still requires Business plan minimum

---

## Recommendation

### For MVP Development

**Plan:** **Business Plan (£199/month)**

**Rationale:**
1. ✅ Has all required features (pricing + sales history)
2. ✅ 50k API calls/month is more than enough (we'll use <1%)
3. ✅ Can scale to 100+ boxes without upgrading
4. ✅ Includes priority support (helpful during development)
5. ⚠️ Not free, but necessary for core functionality

**Budget Consideration:**
- £199/month = ~$250 USD/month
- This is the cost of doing business for this type of application
- Can be considered part of infrastructure costs
- Will be offset by subscription revenue (Phase 8)

### Free Plan Assessment

**Verdict:** ❌ **Free plan cannot work for MVP**

**Why:**
- No API access (only CSV downloads)
- No pricing information
- No sales history
- Would require complete architectural change (manual CSV processing)

**Conclusion:** Free plan is not a viable option for automated market intelligence application.

---

## Decision Needed

**Question:** Is £199/month acceptable for MVP development?

**If Yes:**
- Sign up for Business plan
- Get API credentials
- Review API documentation
- Proceed with Phase 2 development

**If No (Budget Constrained):**
- Consider alternative approaches:
  1. Find alternative/free data sources (unlikely)
  2. Reduce scope significantly (fewer features)
  3. Manual data collection (not scalable)
  4. Defer MVP until budget available

---

## TCGGO Alternative

**Status:** ⚠️ Under Review (see TCGGO_API_ANALYSIS.md)

**TCGGO API** (tcggo.com) offers:
- Free tier: 100 requests/day
- Real-time prices
- Market analytics
- Available via RapidAPI

**Key Question:** Does TCGGO provide individual listing data (prices, quantities, listing IDs) or just aggregated prices?

**Action:** Review TCGGO API documentation at https://www.tcggo.com/api-docs/v1/ to verify endpoints match our requirements.

**If TCGGO has listing endpoints:**
- ✅ Free tier could work for MVP (10 boxes = 10 requests/day)
- ✅ Much cheaper than TCGAPIs (£0 vs £199/month)
- ⚠️ May need paid plan at scale

**If TCGGO only has aggregated prices:**
- ❌ Won't work (we need individual listings for change detection)
- ❌ Need TCGAPIs Business plan or alternative

---

## Next Steps

1. **Review TCGGO API Documentation**
   - Check https://www.tcggo.com/api-docs/v1/
   - Verify listing endpoints exist
   - Confirm data structure matches needs

2. **Compare Services:**
   - TCGGO (free, needs verification)
   - TCGAPIs Business (£199/month, confirmed features)

3. **Decision:** Choose based on:
   - Feature availability (individual listings required)
   - Cost constraints
   - Rate limits (100/day sufficient for MVP?)

4. **Update REMAINING_UNKNOWNS.md** once decision is made

