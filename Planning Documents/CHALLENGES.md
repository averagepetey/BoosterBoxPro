# Biggest Challenges Before Implementation

## 🚨 Critical Challenges (Must Resolve)

### 1. Marketplace API Integration & Data Reliability
**Risk Level: HIGH** ⚠️

**Why it's critical:**
- The entire product depends on reliable, accurate marketplace data
- Without good data, all calculations are meaningless
- This is the foundation - everything else builds on this

**✅ DECIDED:** TCGplayer (primary) + eBay (secondary)
- See [MARKETPLACE_STRATEGY.md](./MARKETPLACE_STRATEGY.md) for architecture
- Strict separation: Each marketplace has own raw tables
- Unified metrics calculated at aggregate level only

**Remaining Unknowns/Challenges:**
- ❓ **API access & credentials** - Do you have API keys for both? Rate limits?
- ❓ **Data format** - What do TCGplayer/eBay API responses look like?
- ❓ **Data quality** - How clean/reliable is their data?
- ❓ **Rate limits** - Can we fetch all boxes within limits for both APIs?
- ❓ **eBay API specifics** - How to fetch only completed sales? Filtering strategy?
- ❓ **TCGplayer API specifics** - How to get listing snapshots? Change detection?
- ❓ **API stability** - Do they change endpoints/data structure frequently?
- ❓ **Weight tuning** - 70/30 split (TCG/eBay) may need adjustment based on real data

**What we need:**
- [ ] Get API credentials for TCGplayer and eBay
- [ ] Get API documentation for both marketplaces
- [ ] Understand rate limits and pricing for both APIs
- [ ] Test TCGplayer API responses (listings, changes)
- [ ] Test eBay API responses (completed sales filtering)
- [ ] Design error handling for API failures (both)
- [ ] Plan for API changes/versioning
- [ ] Validate 70/30 weight split with real data

**Mitigation:**
- ✅ Start with TCGplayer only (Phase 1)
- ✅ Build marketplace adapter layer (abstract interface)
- ✅ Add eBay in Phase 2 (sold listings only)
- ✅ Implement robust retry logic and error handling per adapter
- ✅ Separate raw data tables (no mixing)
- ✅ Unified metrics calculated explicitly (testable)

---

### 2. Volume Calculation Accuracy & Edge Cases
**Risk Level: HIGH** ⚠️

**Why it's critical:**
- Volume is the PRIMARY ranking signal - must be accurate
- Incorrect volume = incorrect rankings = product is unreliable
- Many edge cases can corrupt volume calculations

**Known Edge Cases:**
- 🔴 **Relists** - Seller delists and relists same item (not a real sale)
- 🔴 **Partial sales** - Quantity decreases (real sale) vs. seller adjusting quantity (not a sale)
- 🔴 **Multiple snapshots** - What if we miss a day? Gap detection
- 🔴 **Price changes** - Listing price changes don't count as sales
- 🔴 **Data gaps** - API failures, missing snapshots
- 🔴 **Seller behavior** - Sellers removing/re-adding listings for various reasons

**Specific Challenges:**
- **Relist detection logic** - Complex heuristics needed
  - Same seller_id + same listing_id + <24h gap = likely relist (don't count)
  - Different seller_id = likely real sale (count it)
  - >24h gap = treat as new listing
- **Partial quantity changes** - Hard to distinguish real sales from seller edits
- **Multiple marketplaces** - Same item listed on multiple sites = potential duplicates

**What we need:**
- [ ] Detailed test cases for all edge cases
- [ ] Validation logic for sales detection
- [ ] Manual review process for first few weeks of data
- [ ] Comparison with actual marketplace sales data (if available)
- [ ] Monitoring/alerting for anomalies in volume calculations

**Mitigation:**
- Start conservative (better to under-count than over-count sales)
- Log all changes for audit trail
- Build validation queries to spot anomalies
- Manual review period before going live
- Consider machine learning later to improve detection accuracy

---

### 3. Database Performance & Scale
**Risk Level: MEDIUM-HIGH** ⚠️

**Why it's critical:**
- Leaderboard queries need to be fast (users expect <500ms)
- Ranking queries with window functions can be slow at scale
- Listing snapshots grow quickly (daily snapshots for all boxes)

**Challenges:**
- 📊 **Ranking queries** - Window functions on large datasets
  - `ROW_NUMBER() OVER (ORDER BY volume_7d_ema DESC)` on 1000+ boxes
  - Need to be fast for mobile app
- 📊 **Snapshot storage** - Daily snapshots for 1000 boxes × 365 days = 365K rows/year
  - Plus individual listing records (could be millions)
  - Storage costs and query performance
- 📊 **Metrics calculation** - EMAs require historical data lookups
  - 30-day SMAs need to fetch 30 rows per box
  - Could be slow with thousands of boxes
- 📊 **Favorites queries** - Need to check favorite status efficiently
  - Batch checking favorite status for leaderboard (100+ boxes)

**What we need:**
- [ ] Database indexing strategy (already planned, but need to validate)
- [ ] Query performance testing at scale
- [ ] Partitioning strategy for listing_snapshots (by date)
- [ ] Caching strategy for rankings (Redis?)
- [ ] Connection pooling configuration
- [ ] Query optimization for window functions

**Mitigation:**
- Pre-calculate rankings (materialized view or cache)
- Index strategically (already planned in schema)
- Partition listing_snapshots by date (archive old data)
- Use Redis for frequently-accessed rankings
- Optimize queries with EXPLAIN ANALYZE
- Consider read replicas for scaling

---

### 4. Sparkline Data Collection
**Risk Level: MEDIUM** ⚠️

**Why it matters:**
- UI requires sparklines (mini charts) for price trends
- Need frequent enough data points for smooth charts
- Storage and calculation overhead

**Challenges:**
- 📈 **Data frequency** - Daily snapshots = jagged sparklines
  - Need hourly or 4-hour snapshots for smooth 24h charts
  - More storage, more API calls, more complexity
- 📈 **Storage** - Hourly snapshots = 24× more data than daily
  - New table? Or extend existing schema?
- 📈 **Calculation** - Need to track floor_price more frequently
  - Adds complexity to ingestion pipeline

**Options:**
1. **Simple (MVP):** Use daily snapshots, accept jagged charts
2. **Medium:** Store 4-hour snapshots (6 data points for 24h)
3. **Complex:** Store hourly snapshots (24 data points for 24h)

**What we need:**
- [ ] Decide on sparkline approach (simple vs. complex)
- [ ] Design schema for price snapshots if needed
- [ ] Update ingestion pipeline if storing more frequent snapshots
- [ ] Frontend can handle different data granularities

**Mitigation:**
- Start simple (daily data) for MVP
- Frontend can interpolate between daily points for smoother appearance
- Add hourly snapshots later if needed (separate table)

---

### 5. Image/Asset Data Sources
**Risk Level: MEDIUM** ⚠️

**Why it matters:**
- UI requires images/avatars for each booster box
- Need reliable source for box images
- Manual curation doesn't scale

**Challenges:**
- 🖼️ **Source** - Where do images come from?
  - Marketplace API? (might not provide)
  - Scraping? (legal/technical issues)
  - Manual upload? (doesn't scale)
  - External CDN/service? (cost)
- 🖼️ **Format/Size** - Consistent image dimensions?
- 🖼️ **Missing images** - Fallback for boxes without images?
- 🖼️ **Updates** - Images change over time?

**What we need:**
- [ ] Identify image source(s)
- [ ] Design image storage (CDN, S3, etc.)
- [ ] Image processing pipeline (resize, optimize)
- [ ] Fallback/default image strategy

**Mitigation:**
- Start with placeholder/default image
- Add real images incrementally
- Use marketplace API if available
- Consider Scryfall API for MTG images (if applicable)

---

## 🟡 Important but Less Critical

### 6. Authentication & Security Implementation
**Risk Level: MEDIUM** ⚠️

**Challenges:**
- JWT token management (refresh tokens, expiration)
- Password security (hashing, requirements)
- Mobile token storage (Keychain/Keystore)
- Web token storage (httpOnly cookies vs. localStorage)
- CORS configuration
- Rate limiting per user

**Why it's manageable:**
- Well-documented patterns exist
- FastAPI has good auth libraries
- Can use existing libraries (python-jose, passlib)

---

### 7. Testing Strategy
**Risk Level: MEDIUM** ⚠️

**Challenges:**
- Testing ingestion pipeline (need mock marketplace API responses)
- Testing calculation accuracy (need known test data)
- Testing edge cases (relists, partial sales, etc.)
- Integration testing with real APIs (rate limits, costs)
- Performance testing at scale

**Why it's manageable:**
- Can create comprehensive test datasets
- Use API mocking for development
- Gradual rollout with monitoring

---

### 8. Total Supply Estimates (for Listed %)
**Risk Level: LOW-MEDIUM** ⚠️

**Challenges:**
- Marketplace APIs might not provide total supply
- Need to estimate or skip listed percentage initially
- Could affect UI display

**Mitigation:**
- Skip listed percentage initially (just show absolute counts)
- Add later if supply data becomes available
- Not critical for MVP

---

## 📊 Priority Action Items

### Before Coding Starts:

1. **🔴 CRITICAL: Get Marketplace API Access**
   - Choose marketplace(s)
   - Get credentials
   - Review API documentation
   - Test with sample requests

2. **🔴 CRITICAL: Validate Data Quality**
   - Fetch sample data for 10-20 boxes
   - Inspect data format and completeness
   - Identify missing fields
   - Test edge cases (relists, etc.)

3. **🟡 IMPORTANT: Design Testing Strategy**
   - Create test datasets
   - Mock API responses for development
   - Plan edge case testing

4. **🟡 IMPORTANT: Decide Sparkline Approach**
   - Simple (daily) vs. Complex (hourly)
   - Impacts schema and ingestion pipeline

5. **🟢 NICE-TO-HAVE: Image Source Strategy**
   - Can start with placeholders
   - Add real images incrementally

---

## 🎯 Recommended Approach

### Phase 0: Validation (Before Coding)
1. Get marketplace API access and documentation
2. Fetch sample data (10-20 boxes for 1 week)
3. Manually validate data quality and edge cases
4. Test calculation logic on sample data
5. Design test datasets based on real data patterns

### Phase 1: MVP (Minimal Viable Product)
1. Build ingestion for ONE marketplace
2. Track 50-100 boxes (manageable scale)
3. Simple sparklines (daily data, interpolated)
4. Basic error handling
5. Manual monitoring/review period

### Phase 2: Scale & Refine
1. Expand to more boxes (1000+)
2. Add multiple marketplaces
3. Improve edge case handling (relists, etc.)
4. Optimize performance (caching, indexing)
5. Add hourly snapshots for sparklines

---

## 💡 Key Recommendations

1. **Start Small** - Track fewer boxes initially, validate accuracy
2. **Validate Early** - Test calculations on real data before scaling
3. **Monitor Closely** - Build in logging/monitoring from day 1
4. **Be Conservative** - Better to under-count sales than over-count
5. **Plan for Failure** - APIs fail, data is messy, design for resilience
6. **Iterate** - MVP first, refine based on real-world data patterns

---

## 🔍 Biggest Unknown Right Now

**The #1 challenge is marketplace API integration because:**
- It's the foundation (everything depends on it)
- We don't have API access yet
- Data quality is unknown
- Rate limits are unknown
- Real data patterns (edge cases) are unknown

**Recommendation:** Start by getting API access and exploring the data. Once we understand the data quality and patterns, we can refine the ingestion and calculation logic accordingly.


