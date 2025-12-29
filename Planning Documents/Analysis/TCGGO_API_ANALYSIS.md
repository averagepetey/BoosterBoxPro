# TCGGO API Analysis

> **Note:** This analysis is for **future API integration** (Phase 2B, post-MVP). We are building with **manual data entry first**. See **[MANUAL_FIRST_APPROACH.md](../MANUAL_FIRST_APPROACH.md)** for current build strategy.

> **API Documentation:** https://www.tcggo.com/api-docs/v1/
> **Access:** Available through RapidAPI

---

## Initial Findings

Based on web search results:

**Free Plan:**
- ✅ 100 requests per day
- ✅ All data endpoints included
- ✅ Free tier available
- ⚠️ May not be sufficient for production MVP (see analysis below)

**Data Available:**
- Real-time prices
- Card data
- Market analytics
- Daily price updates
- EU and US markets

**Access Method:**
- Available through RapidAPI
- Requires API key

---

## Critical Questions to Answer

To determine if TCGGO API will work for our app, we need to verify:

### 1. Data Availability

**Required for MVP:**
- [ ] ❓ Active listings (with prices, quantities)
- [ ] ❓ Individual listing data (not just aggregated prices)
- [ ] ❓ Listing quantities/stock counts
- [ ] ❓ Historical listing data (for change detection)
- [ ] ❓ Sales history or completed listings
- [ ] ❓ Product identification (One Piece booster boxes)

**Current Status:** Unknown - Need to review actual API documentation

---

### 2. API Endpoints Needed

**For Phase 2 (TCGplayer Ingestion), we need:**

**Listing Data:**
- [ ] ❓ Get active listings for a product
- [ ] ❓ Get listing details (price, quantity, seller, listing ID)
- [ ] ❓ Search/filter listings
- [ ] ❓ Pagination support

**Product Data:**
- [ ] ❓ Search products by name (One Piece booster boxes)
- [ ] ❓ Get product details by ID
- [ ] ❓ Product categorization/filtering

**Historical Data:**
- [ ] ❓ Get historical prices (for sparklines)
- [ ] ❓ Get sales/completed listings (for volume calculation)
- [ ] ❓ Change detection (new/removed listings)

**Current Status:** Unknown - Need to review actual API documentation

---

### 3. Rate Limits

**Free Plan:**
- 100 requests per day (mentioned in search results)

**Our MVP Needs:**
- 10 boxes × 1 snapshot per day = 10 requests/day (minimum)
- Development/testing: Additional requests
- Error retries: Additional requests
- **Total estimated: 20-50 requests/day for MVP**

**Verdict:** ✅ **Free plan (100/day) should work for MVP**

**Scaling:**
- 100 boxes × 1 snapshot/day = 100 requests/day
- Would need paid plan at scale

---

### 4. Data Format

**Required:**
- [ ] ❓ JSON responses (standard API format)
- [ ] ❓ Listing ID field (for tracking changes)
- [ ] ❓ Price in USD (or convertible)
- [ ] ❓ Quantity field
- [ ] ❓ Timestamps
- [ ] ❓ Product identifiers

**Current Status:** Unknown - Need to review actual API documentation

---

## Comparison with TCGAPIs

| Feature | TCGGO (Free) | TCGAPIs (Business) |
|---------|--------------|-------------------|
| **Cost** | £0/month | £199/month |
| **Rate Limit** | 100 requests/day | 50,000 requests/month |
| **API Access** | ✅ Yes | ✅ Yes |
| **Pricing Data** | ✅ Likely (mentioned) | ✅ Yes |
| **Listings Data** | ❓ Unknown | ✅ Yes |
| **Sales History** | ❓ Unknown | ✅ Yes |
| **Booster Boxes** | ❓ Unknown | ✅ Yes (One Piece) |

---

## Assessment Criteria

### Will TCGGO Work? Checklist

**Must Have:**
- [ ] ❓ Active listings endpoint (with prices, quantities)
- [ ] ❓ Individual listing data (not just aggregated)
- [ ] ❓ Listing IDs (for tracking changes over time)
- [ ] ❓ Product search (find One Piece booster boxes)
- [ ] ❓ 100 requests/day sufficient (should be for 10 boxes)

**Nice to Have:**
- [ ] ❓ Sales history endpoint
- [ ] ❓ Historical price data
- [ ] ❓ Real-time updates (or daily snapshots sufficient)

---

## Next Steps to Verify

1. **Review Actual API Documentation**
   - Visit https://www.tcggo.com/api-docs/v1/
   - Check available endpoints
   - Verify data structure
   - Confirm listing/product endpoints exist

2. **Key Endpoints to Look For:**
   - `/products` or `/search` - Find products
   - `/listings` or `/market` - Get listings for product
   - `/prices` - Get price data
   - `/sales` or `/completed` - Sales history (if available)

3. **Test with Free Plan:**
   - Sign up via RapidAPI
   - Get API key
   - Test endpoint with One Piece product
   - Verify data format matches our needs

4. **Verify Data Completeness:**
   - Does it include individual listings? (not just prices)
   - Does it include quantities?
   - Does it include listing IDs?
   - Can we track changes day-over-day?

---

## Preliminary Verdict

**Potential:** ⚠️ **PROMISING BUT NEEDS VERIFICATION**

**Pros:**
- ✅ Free tier (100 requests/day)
- ✅ Real-time prices mentioned
- ✅ Market analytics mentioned
- ✅ Rate limit sufficient for MVP (10 boxes)

**Concerns:**
- ⚠️ Unclear if individual listings are available (vs. aggregated prices)
- ⚠️ Unclear if quantities are included
- ⚠️ Unclear if sales history is available
- ⚠️ Need to verify One Piece booster box data exists

**Critical Question:** 
Does TCGGO provide **individual listing data** (price, quantity, listing ID) or just **aggregated prices**? We need individual listings to:
- Calculate floor price (min of all listings)
- Track quantity changes (detect sales)
- Build listing snapshots

---

## Recommendation

**Next Action:**
1. Review the actual API documentation at https://www.tcggo.com/api-docs/v1/
2. Look specifically for:
   - Listing endpoints (not just price endpoints)
   - Whether data includes individual listings or aggregated
   - Product search capabilities
   - Data structure/format
3. If endpoints look good, sign up for free plan and test
4. Compare results with TCGAPIs Business plan requirements

**If TCGGO has listing endpoints:**
- ✅ Free plan could work for MVP
- ✅ Significantly cheaper than TCGAPIs (£0 vs £199/month)
- ⚠️ May need paid plan at scale (100+ boxes)

**If TCGGO only has aggregated prices:**
- ❌ Won't work for our architecture (we need individual listings)
- ❌ Need TCGAPIs Business plan or alternative

---

## Questions to Answer from Documentation

When reviewing https://www.tcggo.com/api-docs/v1/, specifically check:

1. **Listings Endpoint:**
   - Is there a `/listings` or `/market/listings` endpoint?
   - Does it return individual listings (not aggregated)?
   - Does each listing have: ID, price, quantity, seller?

2. **Products:**
   - Can we search for "One Piece booster box"?
   - Are booster boxes categorized separately?
   - How do we identify the 10 specific boxes we need?

3. **Data Structure:**
   - Are listing IDs unique and persistent?
   - Can we track same listing over time?
   - Are timestamps included?

4. **Sales History:**
   - Is there a `/sales` or `/completed` endpoint?
   - Or do we need to infer from listing changes?

5. **Rate Limits:**
   - 100 requests/day confirmed?
   - What happens when limit exceeded?
   - Paid plan pricing/limits?

---

## Update This Document

Once you review the actual API documentation, update this file with:
- ✅/❌ for each required feature
- Specific endpoint names
- Data structure examples
- Final verdict: Will it work for MVP?

