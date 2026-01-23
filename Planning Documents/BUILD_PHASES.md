# Build Phases (Locked Order)

> **This document defines the authoritative build order. Phases must be completed sequentially. Each phase builds on the previous.**

## 🎯 Build Strategy: Manual-First Approach

**Primary Approach:** We're building with **manual data entry first**, then adding API integration later.

**Why Manual-First:**
- ✅ Build UI/UX immediately without waiting for API access
- ✅ Test and validate all functionality before investing in API costs
- ✅ Iterate quickly with instant data changes
- ✅ Same database schema - seamless transition to APIs later
- ✅ Frontend code requires no changes when APIs are added

**Manual Entry:** See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for complete details on manual entry workflow.

**Future API Integration:** Phases marked as "Future" (Phase 2B, Phase 4, Phase 5B) will be implemented after MVP is complete and validated with manual data.

---

## 🧱 Phase Breakdown

### Phase 0 — UX + API Planning (No Logic)

**Goal:** Design interfaces and API contracts before building logic.

**Actionable Steps:**

1. **Leaderboard Screen Design**
   - Create wireframe mockup (Figma/Sketch/pen & paper)
   - Define: Box avatar, name, current rank, volume metric, price change indicator, rank change arrows
   - Layout: Top 10 boxes in vertical list, pull-to-refresh, infinite scroll for top 50
   - Design empty state (no data message)
   - Define color scheme for rank indicators (green up, red down)

2. **Box Detail Screen Design (Advanced Analytics)**
   - Create wireframe mockup
   - Define clear navigation: Clicking/tapping any row in leaderboard → Navigate to detail screen
   - Define sections:
     - **Header:** Large box image/avatar, product name, set name, current rank with change indicator, favorite button
     - **Key Metrics Card:** Floor price (prominent), volume, liquidity score, expected days to sell, days to +20%, active listings
     - **Price Chart:** Interactive line chart showing floor price trend (last 30 days default, with time range selector)
     - **Advanced Metrics Table:** Time-series data table (date, floor price, volume, listings, sales, market cap) - sortable, exportable
     - **Rank History:** Chart/graph showing rank position over time
   - Design back button/navigation (return to leaderboard)
   - Design favorite/unfavorite button placement
   - Define navigation flow: Leaderboard row click/tap → Detail screen → Back button → Leaderboard
   - Note: Detail screen provides "advanced analytics" beyond the summary metrics shown in leaderboard

3. **API Endpoint Specifications**
   - Document `GET /api/v1/booster-boxes` response shape:
     - Array of objects with: `id`, `product_name`, `image_url`, `current_rank`, `rank_change` (+1/-1/0), `unified_volume_7d_ema`, `floor_price_usd`, `floor_price_change_24h`, `liquidity_score`
   - Document `GET /api/v1/booster-boxes/{id}` response shape:
     - Single object with all detail fields: full metrics, time-series data, historical prices
   - Document `GET /api/v1/booster-boxes/{id}/time-series` response shape:
     - Array of daily data points: `date`, `floor_price_usd`, `volume`, `listings_count`

4. **Create Mock Data Files**
   - Create `mock_data/leaderboard.json` with 10 sample box objects matching API spec
   - Create `mock_data/box_detail_{id}.json` with full detail response
   - Create `mock_data/time_series_{id}.json` with 30 days of sample data
   - Ensure mock data matches real data structure (same field names, types)

5. **OpenAPI/Swagger Specification**
   - Write OpenAPI 3.0 YAML file documenting all endpoints
   - Include request/response schemas using mock data examples
   - Define error response shapes (400, 404, 500)
   - Include authentication requirements (if Phase 8 planned)

6. **UI Component Inventory**
   - List all reusable components needed: BoxCard, MetricCard, PriceChart, RankIndicator
   - Define component props/interfaces (TypeScript types or prop definitions)
   - Document component states (loading, error, empty, populated)

**Deliverables:**
- UI mockups/wireframes (Figma file or images)
- API specification (OpenAPI/Swagger YAML)
- Mock data JSON files (3-5 files in `mock_data/` directory)
- API response examples (embedded in OpenAPI spec)

**No Real Implementation:**
- No frontend logic yet
- No backend code
- Just design and contracts

**Exit Criteria:**
- API shapes locked in (OpenAPI spec complete and reviewed)
- UI designs approved (mockups signed off)
- Mock data represents real structure (fields match Phase 5 metrics)

---

### Phase 1 — Core Data Foundation

**Goal:** Create permanent identity system for booster boxes.

**Data Entry Strategy:**
> **💡 RECOMMENDED:** Use manual data entry first! See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for details.
> - Build admin panel for manual metrics entry
> - Enter data manually to test everything
> - Swap to API integration later (seamless transition)

**Actionable Steps:**

1. **Database Setup**
   - Install PostgreSQL 15+ (local or cloud instance)
   - Create database: `boosterboxpro` (or similar)
   - Set up connection pool configuration
   - Configure database connection environment variables

2. **Create Core Schema Migration**
   - Create Alembic migration: `alembic init migrations`
   - Write migration for `booster_boxes` table with fields:
     - `id` (UUID, primary key)
     - `external_product_id` (VARCHAR(255), unique, nullable - optional for manual mode)
     - `product_name` (VARCHAR(500), required)
     - `set_name` (VARCHAR(255))
     - `game_type` (VARCHAR(100), default 'One Piece')
     - `release_date` (DATE, nullable)
     - `image_url` (VARCHAR(500), nullable)
     - `estimated_total_supply` (INT, nullable)
     - `reprint_risk` (ENUM: 'LOW', 'MEDIUM', 'HIGH', default 'LOW')
     - `created_at`, `updated_at` (TIMESTAMP)
   - Add indexes: `external_product_id`, `game_type`
   - Run migration: `alembic upgrade head`

3. **Create SQLAlchemy Models**
   - Create `models/booster_box.py` with BoosterBox model
   - Add type hints and relationships
   - Create Base model class if needed
   - Add `__repr__` method for debugging

4. **Manual Box Entry System (Choose One Approach)**
   
   **Option A: Admin API Endpoint (Recommended)**
   - Create FastAPI endpoint: `POST /api/v1/admin/boxes`
   - Accept JSON payload: `product_name`, `set_name`, `image_url`, etc.
   - Validate required fields (Pydantic model)
   - Generate UUID for new box
   - Insert into database via SQLAlchemy
   - Return created box with 201 status
   - Add basic authentication (simple API key for now, upgrade in Phase 8)

   **Option B: CSV Import Script**
   - Create `scripts/import_boxes.py`
   - Read CSV file with columns: product_name, set_name, image_url, etc.
   - Parse and validate each row
   - Insert into database
   - Handle duplicates (skip or update)

   **Option C: Direct Database Insert**
   - Create SQL insert script
   - Manually insert 10 boxes via psql or admin tool

5. **Register 10 One Piece Booster Boxes**
   - Research and compile list of 10 One Piece booster boxes:
     - OP-01 Romance Dawn Booster Box
     - OP-02 Paramount War Booster Box
     - OP-03 Pillars of Strength Booster Box
     - OP-04 Kingdoms of Intrigue Booster Box
     - OP-05 Awakening of the New Era Booster Box
     - (Add 5 more boxes)
   - For each box, collect: product name, set name, release date, image URL
   - Enter all 10 boxes using chosen method from Step 4
   - Verify all boxes have unique UUIDs in database

6. **Create Snapshot Schema Placeholders**
   - Create Alembic migration for `tcg_listings_raw` table (empty, no data yet)
   - Create migration for `tcg_box_metrics_daily` table (empty)
   - Create migration for `ebay_sales_raw` table (empty)
   - Create migration for `ebay_box_metrics_daily` table (empty)
   - Create migration for `box_metrics_unified` table (empty)
   - All tables should have proper foreign keys to `booster_boxes(id)`
   - Run migrations: `alembic upgrade head`

7. **Create Manual Metrics Entry Endpoint**
   - Create `POST /api/v1/admin/manual-metrics` endpoint
   - Accept JSON payload: `booster_box_id`, `metric_date`, `floor_price_usd`, `active_listings_count`, `tcg_volume_usd`
   - Validate box exists (404 if not found)
   - Insert/update metrics in `tcg_box_metrics_daily` table (for manual mode)
   - Support bulk entry (array of metrics)
   - Return success confirmation

8. **Create Basic Admin Interface (Optional but Recommended)**
   - Create simple HTML form or React component for manual entry
   - Form fields: Box dropdown, date picker, floor price, listings count, volume
   - Submit to manual-metrics endpoint
   - Show success/error messages
   - List recent entries

9. **Enter Sample Data**
   - Enter 7-14 days of sample metrics for each of the 10 boxes
   - Use realistic values (research actual One Piece box prices)
   - Vary values slightly day-to-day to simulate real market data
   - Verify data appears correctly in database queries

10. **Database Verification**
    - Query `booster_boxes` table: should have exactly 10 rows
    - Query `tcg_box_metrics_daily` table: should have 70-140 rows (7-14 days × 10 boxes)
    - Verify UUIDs are unique
    - Verify foreign keys work (try to delete a box, should cascade or error appropriately)

**Deliverables:**
- PostgreSQL database with schema
- `booster_boxes` table with 10 rows (One Piece boxes)
- `external_product_id` field ready for marketplace mapping (nullable for now)
- All snapshot/metrics tables created (empty, ready for Phase 2+)
- Admin endpoint: `POST /api/v1/admin/manual-metrics` working
- Sample data: 7-14 days of metrics for all boxes

**Key Concept:**
- This creates a **permanent identity system**
- Each box has a stable UUID regardless of marketplace changes
- Foundation for all future phases
- **Manual entry allows immediate development without API access**

**Exit Criteria:**
- Database schema migrations run successfully
- 10 boxes registered in `booster_boxes` table
- Manual entry system working (endpoint tested with sample data)
- Sample data entered (7-14 days of metrics for all boxes)
- All snapshot/metrics tables exist (empty but ready)
- Can query boxes and metrics from database

---

### Phase 2 — Manual Metrics Entry & Calculation

> **💡 PRIMARY APPROACH:** We're building with manual data entry first. This allows us to build and validate the entire app without waiting for API access. API integration will be added in a future phase.

**Goal:** Build manual data entry system and calculate unified metrics from manually entered data.

**Strategy:** See **[MANUAL_FIRST_APPROACH.md](./MANUAL_FIRST_APPROACH.md)** for complete details on the manual-first approach.

**Actionable Steps:**

1. **Enhance Manual Metrics Entry Endpoint** (Build on Phase 1)
   - Enhance `POST /api/v1/admin/manual-metrics` from Phase 1
   - Accept comprehensive metrics payload:
     - `booster_box_id`, `metric_date`
     - `floor_price_usd` (required)
     - `active_listings_count` (required)
     - `boxes_sold_today` (optional, for volume calculation)
     - `boxes_added_today` (optional)
     - `daily_volume_usd` (optional, can calculate from sales × floor_price)
     - `visible_market_cap_usd` (optional, can calculate from listings × floor_price)
   - Validate all required fields
   - Insert/update directly into `box_metrics_unified` table (simplified manual flow)
   - Support bulk entry (array of metrics for multiple boxes on same date)
   - Return success confirmation with calculated/derived metrics

2. **Create Admin Panel for Manual Entry** (Recommended)
   - Create simple web interface for manual data entry
   - Options:
     - Simple HTML form with JavaScript
     - React component (if using React frontend)
     - Next.js admin page (if using Next.js)
   - Form features:
     - Date picker (default to today, allow selecting past dates for backfill)
     - Box selector dropdown (all boxes from database)
     - Metric input fields:
       - Floor Price (USD, required)
       - Active Listings Count (integer, required)
       - Boxes Sold Today (integer, optional)
       - Boxes Added Today (integer, optional)
       - Daily Volume USD (decimal, optional - can auto-calculate)
       - Visible Market Cap USD (decimal, optional - can auto-calculate)
     - Save button
     - "Save & Next Box" button (for bulk entry)
     - Recent entries display (last 5-10 entries)
   - Form validation (required fields, numeric validation)
   - Success/error messages
   - Auto-calculate optional fields if not provided

3. **Implement Metrics Calculation from Manual Data**
   - Create `services/manual_metrics_calculator.py`
   - Method: `calculate_metrics_from_manual_entry(manual_data: dict) -> UnifiedMetrics`
   - Logic:
     - Use manual entry data directly (floor_price, listings_count already provided)
     - Calculate derived metrics:
       - `visible_market_cap_usd = floor_price_usd × active_listings_count` (if not provided)
       - `daily_volume_usd = boxes_sold_today × floor_price_usd` (if not provided, use provided value if given)
       - Calculate 7-day EMA of volume (needs historical data)
       - Calculate 30-day SMA of volume (needs historical data)
     - Store directly into `box_metrics_unified` table (simplified manual flow)
   - Handle edge cases: First entry (no historical data for EMA), missing optional fields

4. **Create Unified Metrics Calculation Service** (Simplified for Manual Mode)
   - Create `services/unified_metrics_calculator.py`
   - Method: `calculate_unified_metrics_for_manual(box_id, date, manual_data) -> UnifiedMetrics`
   - For manual mode, simplified calculation:
     - Use provided floor_price directly
     - Use provided active_listings_count directly
     - Calculate volume EMAs from historical unified metrics (if available)
     - Calculate liquidity score (simplified: based on listings count and sales velocity)
     - Calculate expected_days_to_sell: `active_listings_count / boxes_sold_per_day_avg`
     - Calculate days_to_20_percent (if enough data available)
   - Store results in `box_metrics_unified` table

5. **Implement Historical Data Query for EMA Calculations**
   - When entering new manual data, query historical metrics from `box_metrics_unified`
   - Calculate 7-day EMA and 30-day SMA using historical volume data
   - Handle cases with <7 days of data (use available data, log warning)
   - Update unified metrics with calculated EMAs

6. **Enter Initial Sample Data**
   - Enter 14-30 days of sample metrics for all 10 boxes
   - Use realistic values (research actual One Piece box prices from TCGplayer/eBay)
   - Vary values day-to-day to simulate real market fluctuations
   - Verify EMAs calculate correctly with historical data
   - Verify all derived metrics populate correctly

7. **Create CSV Import Option** (Optional Enhancement)
   - Create endpoint: `POST /api/v1/admin/import-csv`
   - Accept CSV file upload with columns: date, box_name, floor_price, active_listings, boxes_sold, etc.
   - Parse CSV, validate data, bulk insert metrics
   - Return import summary (rows processed, errors, etc.)
   - Useful for backfilling historical data

8. **Database Verification**
   - Query `box_metrics_unified` table: should have 14-30 days × 10 boxes = 140-300 rows
   - Verify all fields populated correctly
   - Verify EMAs calculated (check values make sense)
   - Verify calculated metrics (market cap, volume, etc.)
   - Test updating existing date (upsert logic)

**Deliverables:**
- Enhanced manual metrics entry endpoint (`POST /api/v1/admin/manual-metrics`)
- Admin panel for manual data entry (web interface)
- Metrics calculation service for manual data
- Unified metrics calculator (simplified for manual mode)
- Historical data query for EMA calculations
- Sample data: 14-30 days of metrics for all 10 boxes
- CSV import functionality (optional)

**What This Enables:**
- Full app functionality with manual data
- Leaderboard working (rankings based on unified metrics)
- All metrics displayed correctly
- Rankings, sparklines, and trends all functional
- **App is fully usable with manual data entry**

**Exit Criteria:**
- Manual entry endpoint working and tested
- Admin panel functional (can enter data via UI)
- Sample data entered (14-30 days for all boxes)
- Unified metrics table populated correctly
- EMAs calculated correctly from historical data
- All derived metrics (liquidity score, days to sell, etc.) calculated
- Can query unified metrics and see correct data
- Ready for frontend development (Phase 7)

---

### Phase 2B — Future: Marketplace API Integration (Optional Later Phase)

> **⚠️ FUTURE PHASE:** This phase will be implemented after the app is built and validated with manual data. API integration will seamlessly replace manual entry while keeping the same database structure and API endpoints.

**Goal:** Automate data collection by integrating with TCGplayer and eBay APIs.

**When to Implement:**
- After MVP is complete and validated
- After frontend is built and tested with manual data
- When ready to scale beyond manual entry
- When API access is obtained (TCGGO, TCGAPIs, or eBay Developer Account)

**Data Collection Options:**
1. **TCGGO API** (free tier: 100 requests/day)
2. **TCGAPIs Business plan** (£199/month)
3. **eBay API** (free, requires developer account)
4. **Scraping** (Not recommended - see Analysis documents for risks)

**See Analysis/API_SERVICE_ANALYSIS.md and Analysis/TCGGO_API_ANALYSIS.md for detailed API integration plans.**

**Key Implementation Notes:**
- Will populate `tcg_listings_raw` and `ebay_sales_raw` tables
- Will calculate metrics from raw data (same unified metrics table)
- Frontend code requires NO changes (same API endpoints)
- Can run in parallel with manual entry initially (validation/backup)

---

### Phase 3 — Unified Metrics Calculation (Manual Data)

**Goal:** Calculate aggregated unified metrics from manually entered data.

**Actionable Steps:**

1. **Create Metrics Calculation Service**
   - Create `services/metrics_calculator.py`
   - Create `services/ema_calculator.py` for EMA/SMA calculations
   - Implement EMA calculation function:
     - Formula: `EMA_today = (price_today × α) + (EMA_yesterday × (1-α))`
     - Alpha (α) for 7-day EMA = 2/(7+1) = 0.25
     - Alpha (α) for 30-day SMA = simple average (no smoothing)
   - Add unit tests for EMA calculations (verify against known values)

2. **Implement Daily Aggregated Metrics Calculation** (Manual Mode)
   - Create method: `calculate_daily_unified_metrics_from_manual(box_id, date) -> UnifiedMetrics`
   - Get metrics from `box_metrics_unified` table (populated by manual entry in Phase 2)
   - For manual mode, data comes directly from manual entry:
     - Floor price: From manual entry
     - Active listings count: From manual entry
     - Daily volume: From manual entry (or calculated from boxes_sold × floor_price)
   - Calculate derived metrics from manual data

3. **Calculate EMA-Smoothed Volume** (From Manual Data)
   - Create method: `calculate_volume_ema(box_id, date, window_days=7) -> Decimal`
   - Get last 30 days of daily volume from `box_metrics_unified` (populated from manual entries)
   - Calculate 7-day EMA of volume (using formula from Step 1)
   - Calculate 30-day SMA (simple average of last 30 days)
   - Handle edge cases: Less than 7 days of data (use available data, log warning)
   - Update unified metrics with calculated EMAs

4. **Calculate Absorption Rate** (From Manual Data)
   - Create method: `calculate_absorption_rate(box_id, date) -> Decimal`
   - Formula: `absorption_rate = boxes_sold / boxes_listed`
   - Get boxes_sold from manual entry (`boxes_sold_today` field)
   - Get boxes_listed from manual entry (`active_listings_count` field)
   - Handle division by zero (return 0 if no listings)
   - Bound result: max 1.0 (can't absorb more than 100%)

5. **Calculate Liquidity Score** (Simplified for Manual Mode)
   - Create method: `calculate_liquidity_score(box_id, date) -> Decimal`
   - Formula (simplified for manual mode): `absorption_rate × 0.5 + (normalized_listings_count × 0.3) + (volume_velocity × 0.2)`
   - Components from manual data:
     - Absorption rate: `boxes_sold / active_listings_count`
     - Normalized listings count: `active_listings_count / max_expected` (cap at 1.0)
     - Volume velocity: Normalized 7-day EMA of volume (0.0-1.0 scale)
   - Result should be 0.0 to 1.0
   - Note: Full liquidity score with eBay data will be added in future API integration phase

6. **Update Unified Metrics Model** (Already exists from Phase 1)
   - Ensure `box_metrics_unified` table exists (created in Phase 1)
   - Verify all required fields exist
   - Create SQLAlchemy model: `models/unified_box_metrics.py` (if not already created)
   - Fields: `id`, `booster_box_id`, `metric_date`, `floor_price_usd`, `active_listings_count`, `unified_volume_usd`, `unified_volume_7d_ema`, `unified_volume_30d_sma`, `liquidity_score`, `expected_days_to_sell`, `visible_market_cap_usd`, `days_to_20_percent`
   - Add foreign key to `booster_boxes`

7. **Implement Unified Metrics Storage** (Update repository)
   - Update or create repository: `repositories/unified_metrics_repository.py`
   - Methods: `save_unified_metrics()`, `get_metrics_for_date()`, `get_metrics_range()`, `get_latest_metrics()`
   - Upsert logic (update if exists for date+box, insert if new)
   - Add unique constraint on (booster_box_id, metric_date) if not already present

8. **Integrate Metrics Calculation with Manual Entry**
   - When manual metrics are entered (Phase 2), automatically trigger metrics calculation
   - After saving manual entry, calculate derived metrics (EMAs, liquidity score, etc.)
   - Update unified metrics table with calculated values
   - This happens synchronously or as background task after manual entry

9. **Create Metrics Recalculation Script** (For Backfilling/Updates)
   - Create script: `scripts/recalculate_metrics.py`
   - For each box, for each date with manual data:
     - Recalculate all derived metrics (EMAs, liquidity score, etc.)
     - Update unified metrics table
   - Useful when:
     - Adding new calculation logic
     - Fixing calculation bugs
     - Recalculating EMAs with more historical data
   - Run script to recalculate metrics for all historical data
   - Verify EMA calculations work correctly with historical data

10. **Add Market Cap and Expected Days to Sell Calculations**
    - Calculate `visible_market_cap_usd = floor_price_usd × active_listings_count`
    - Calculate `expected_days_to_sell = active_listings_count / boxes_sold_per_day_avg`
      - Get average boxes sold per day from last 30 days of manual entries
      - Bound result: 1-365 days
    - Store in `box_metrics_unified` table
    - These calculations use manual entry data directly

11. **Verification and Testing**
    - Enter new manual data for one box, verify metrics calculated correctly
    - Verify all fields populated correctly in `box_metrics_unified`:
      - Floor price matches manual entry
      - Volume EMA is calculated (check against manual calculation)
      - Absorption rate is 0.0-1.0
      - Liquidity score is 0.0-1.0
      - Expected days to sell is reasonable (1-365)
    - Query `box_metrics_unified` table, verify data looks correct
    - Test edge cases: Box with no listings, box with 1 listing, box with many listings
    - Test with <7 days of data (EMA should still work with available data)

**Deliverables:**
- Unified metrics calculation service (`services/unified_metrics_calculator.py`)
- EMA calculator utility (`services/ema_calculator.py`)
- Metrics calculation integrated with manual entry flow
- `box_metrics_unified` table populated with calculated metrics
- Volume EMAs calculated (7-day EMA, 30-day SMA)
- Absorption rate calculated
- Liquidity score calculated (simplified for manual mode)
- Market cap proxy calculated
- Expected days to sell calculated
- Metrics recalculation script for backfilling/updates

**What This Enables:**
- **App is fully functional** (all metrics calculated and ready for frontend)
- Volume-based rankings (unified volume from manual data)
- Complete liquidity metrics
- Floor price trends
- All derived metrics available for leaderboard and detail views

**Exit Criteria:**
- Metrics calculation integrated with manual entry (runs after each entry)
- `box_metrics_unified` table has metrics for all boxes with manual data
- EMA calculations verified (manual check of one box's EMA value)
- Can query unified metrics for leaderboard (SELECT * FROM box_metrics_unified WHERE metric_date = today)
- All metrics fields populated correctly
- Recalculation script works for backfilling historical data

---

### Phase 4 — Future: eBay Integration (Optional Later Phase)

> **⚠️ FUTURE PHASE:** This phase adds eBay as a secondary demand signal. Will be implemented after manual MVP is complete and validated.

**Goal:** Add eBay as secondary demand signal (not pricing) to enhance unified metrics.

**Actionable Steps:**

1. **eBay API Setup**
   - Sign up for eBay Developer Account (developer.ebay.com)
   - Create app and obtain credentials:
     - App ID (Client ID)
     - Client Secret
     - Dev ID (if required for API)
   - Choose API: eBay Finding API or eBay Browse API (for sold listings)
   - Store credentials in environment variables
   - Review API rate limits (requests per day/hour)

2. **Create eBay Adapter Module**
   - Create `adapters/ebay/__init__.py`
   - Create `adapters/ebay/client.py` with eBayAPIClient class
   - Implement OAuth 2.0 authentication (if required by API)
   - Implement API key authentication (if using simpler API)
   - Add rate limiting (respect eBay API limits)
   - Add retry logic with exponential backoff
   - Add request logging

3. **Implement Sold Listings Fetching**
   - Create method: `fetch_completed_sales(search_query: str, days_back: int = 30) -> List[Sale]`
   - Search parameters:
     - Search query: Box product name (e.g., "One Piece OP-01 Booster Box")
     - Filter: Completed listings only (sold items)
     - Date range: Last 30 days (or configurable)
   - Map API response to internal Sale dataclass:
     - `ebay_item_id`, `sale_date`, `sale_timestamp`, `sold_price_usd`, `quantity`, `seller_id`, `listing_type`
   - Handle pagination (eBay API pagination)
   - Handle API errors (rate limits, authentication failures)

4. **Create Raw Sales Storage**
   - Ensure `ebay_sales_raw` table exists (created in Phase 1)
   - Create SQLAlchemy model: `models/ebay_sale.py`
   - Fields: `id`, `booster_box_id`, `sale_date`, `sale_timestamp`, `ebay_item_id`, `sold_price_usd`, `quantity`, `seller_id`, `listing_type`, `raw_data` (JSONB)
   - Create repository: `repositories/ebay_sale_repository.py`
   - Methods: `save_sale()`, `get_sales_for_date_range()`, `get_sales_for_box()`
   - Add unique constraint on `ebay_item_id` (one sale per item)

5. **Implement Sales Ingestion Logic**
   - Create method: `ingest_ebay_sales(box_id: UUID) -> int`
   - For each box:
     - Build search query from box.product_name
     - Fetch completed sales from last 30 days
     - For each sale:
       - Check if sale already exists (by ebay_item_id)
       - If new, save to `ebay_sales_raw`
   - Return count of new sales ingested
   - Handle duplicate sales (skip if ebay_item_id already exists)

6. **Create eBay Ingestion Celery Task**
   - Create `tasks/ingest_ebay_sales.py`
   - Task logic:
     - Get all boxes from `booster_boxes` table
     - For each box:
       - Call ingest_ebay_sales(box_id)
       - Add delay between boxes (respect rate limits: 1-2 seconds)
       - Log progress (box processed, sales found)
   - Add error handling (skip box if API fails, continue with next)

7. **Schedule eBay Ingestion Job**
   - Configure Celery Beat to run every 12 hours (or 6 hours if API limits allow)
   - Schedule at different times than TCGplayer (e.g., 6 AM and 6 PM UTC)
   - Add to `celery_config.py`:
     ```python
     'ingest-ebay-sales': {
         'task': 'tasks.ingest_ebay_sales.run_ingestion',
         'schedule': crontab(hour='6,18', minute=0),  # 6 AM and 6 PM
     }
     ```

8. **Implement Sales Aggregation Logic**
   - Create `services/ebay_metrics_calculator.py`
   - Create method: `calculate_daily_ebay_metrics(box_id, date) -> eBayMetrics`
   - Get all sales for date from `ebay_sales_raw`
   - Calculate:
     - `sales_count` = count of sales for date
     - `median_sold_price_usd` = median of sold_price_usd values
     - `total_quantity_sold` = sum of quantity fields
     - Handle edge cases: No sales (return 0/None)

9. **Calculate Velocity Acceleration (Momentum)**
   - Create method: `calculate_velocity_acceleration(box_id, date) -> Decimal`
   - Get last 7 days of sales counts from `ebay_box_metrics_daily`
   - Calculate: `acceleration = (sales_count_today - sales_count_7d_avg) / sales_count_7d_avg`
   - Positive = accelerating demand, negative = slowing
   - Handle division by zero (return 0 if no historical sales)
   - Bound result: -1.0 to 1.0 (100% decrease to 100% increase)

10. **Create eBay Metrics Storage**
    - Ensure `ebay_box_metrics_daily` table exists (created in Phase 1)
    - Create SQLAlchemy model: `models/ebay_box_metrics.py`
    - Fields: `id`, `booster_box_id`, `metric_date`, `sales_count`, `median_sold_price_usd`, `total_quantity_sold`, `velocity_acceleration`
    - Create repository: `repositories/ebay_metrics_repository.py`
    - Methods: `save_daily_metrics()`, `get_metrics_for_date_range()`

11. **Create Daily eBay Metrics Calculation Job**
    - Create Celery task: `tasks/calculate_ebay_metrics.py`
    - Task logic:
      - Get all boxes with eBay sales data
      - For each box:
        - Get yesterday's date
        - Calculate daily metrics (sales count, median price)
        - Calculate velocity acceleration (needs historical data)
        - Save to `ebay_box_metrics_daily`
    - Schedule to run after eBay ingestion (e.g., 30 minutes after)

12. **Link Boxes to eBay Search Terms**
    - Add field to `booster_boxes` table: `ebay_search_query` (VARCHAR, nullable)
    - Create migration to add field
    - Populate search queries for each box:
      - Format: "One Piece [SET_NAME] Booster Box"
      - Test searches manually in eBay to verify results
    - Use this field in ingestion task (Step 5)

13. **Initial eBay Data Ingestion**
    - Run ingestion task manually
    - Verify sales data in `ebay_sales_raw` table
    - Check search queries are finding relevant sales (manual verification)
    - Run for 7-14 days to build historical data
    - Calculate metrics and verify data looks correct

14. **Verification and Testing**
    - Verify sales are being ingested (query `ebay_sales_raw`)
    - Verify metrics are calculated correctly:
      - Sales count matches raw data count
      - Median price is correct (manual calculation)
      - Velocity acceleration makes sense (positive/negative based on trend)
    - Test with boxes that have no eBay sales (should handle gracefully)

**Deliverables:**
- eBay adapter module (`adapters/ebay/`)
- eBay API authentication working (OAuth or API key)
- Daily/12-hour ingestion job scheduled
- `ebay_sales_raw` table populated with completed sales
- Sales aggregation logic working
- `ebay_box_metrics_daily` table populated with daily metrics
- Velocity acceleration calculated (momentum indicator)
- Boxes linked to eBay search queries

**What This Enhances:**
- Momentum signals (demand spikes from velocity acceleration)
- Liquidity scoring (eBay sales frequency added in Phase 5)
- Volume weighting (for unified metrics in Phase 5)
- **Never used for pricing** (floor price stays TCGplayer-only)

**Exit Criteria:**
- eBay API credentials configured and tested
- Sales ingestion job runs successfully (verified in logs)
- `ebay_sales_raw` table has sales data for boxes with eBay listings
- `ebay_box_metrics_daily` table has metrics for boxes with sales
- Velocity acceleration calculated (can query and see positive/negative values)
- Ready for unified metrics phase (both TCGplayer and eBay data available)

---

### Phase 5 — Enhanced Unified Metrics (Manual Data)

**Goal:** Calculate final unified metrics from manual data. Note: eBay blending will be added in future API integration phase.

**Actionable Steps:**

1. **Ensure Unified Metrics Table Exists**
   - Verify `box_metrics_unified` table exists (created in Phase 1)
   - Schema should include:
     - `id`, `booster_box_id`, `metric_date`
     - `unified_volume_7d_ema`, `unified_volume_30d_sma`
     - `floor_price_usd` (from TCGplayer only)
     - `liquidity_score` (final blended score)
     - `visible_market_cap_usd` (TCGplayer only)
     - `days_to_20_percent` (projected)
     - `expected_days_to_sell` (average days to sell if listed today)
     - `active_listings_count` (TCGplayer)
     - All other unified fields
   - Create migration if table doesn't exist or fields missing
   - Add `expected_days_to_sell` field to schema if not present (DECIMAL(8,2), nullable)

2. **Create Unified Metrics Calculator Service**
   - Create `services/unified_metrics_calculator.py`
   - Main method: `calculate_unified_metrics(box_id, date) -> UnifiedMetrics`
   - This service will orchestrate all calculations below

3. **Implement Unified Volume Calculation** (Manual Mode - Simplified)
   - Create method: `calculate_unified_volume(box_id, date) -> Decimal`
   - For manual mode: Volume comes directly from manual entry
   - Use `unified_volume_7d_ema` and `unified_volume_30d_sma` calculated in Phase 3
   - These EMAs are already calculated from manual entry data
   - Note: When eBay integration is added (future phase), will blend with weighted formula: `(Manual × 0.7) + (eBay × 0.3)`

4. **Implement Final Liquidity Score** (Manual Mode - Simplified)
   - Create method: `calculate_final_liquidity_score(box_id, date) -> Decimal`
   - For manual mode (no eBay data yet):
     - Use liquidity score calculated in Phase 3 (simplified formula)
     - Formula: `(absorption_rate × 0.5) + (normalized_listings_count × 0.3) + (volume_velocity × 0.2)`
   - Bound result: 0.0 to 1.0
   - Note: When eBay integration is added (future phase), will blend: `(Manual × 0.5) + (velocity_acceleration × 0.3) + (eBay_frequency × 0.2)`

5. **Market Cap Proxy** (From Manual Data)
   - Create method: `calculate_market_cap_proxy(box_id, date) -> Decimal`
   - Get `floor_price_usd` from `box_metrics_unified` (from manual entry)
   - Get `active_listings_count` from `box_metrics_unified` (from manual entry)
   - Formula: `visible_market_cap_usd = floor_price_usd × active_listings_count`
   - Store in `box_metrics_unified.visible_market_cap_usd`

6. **Implement Days-to-20% Projection**
   - Create method: `calculate_days_to_20_percent(box_id, date) -> Optional[int]`
   - Logic:
     - Get current `floor_price_usd` from TCGplayer
     - Calculate target price: `target_price = floor_price_usd × 1.20` (20% increase)
     - Count listings below target price from `tcg_listings_raw` (for current date)
     - Calculate average daily buy rate (last 30 days):
       - Get 30-day average of `inferred_sales` or `tcg_volume` converted to boxes sold
     - Formula: `days_to_20_percent = boxes_below_target / average_daily_buy_rate`
   - Bound result: Minimum 1 day, Maximum 180 days (cap at 180)
   - Handle edge cases:
     - No listings below target (return None or 0)
     - No sales history (return None)
     - Division by zero (return None)

7. **Implement Expected Days to Sell**
   - Create method: `calculate_expected_days_to_sell(box_id, date) -> Optional[float]`
   - Logic:
     - Get `active_listings_count` from `tcg_box_metrics_daily` (boxes currently listed on TCGplayer)
     - Get `boxes_sold_per_day` from unified metrics (or calculate from last 30 days average):
       - Use `boxes_sold_30d_avg` if available, otherwise calculate: `total_boxes_sold_last_30d / 30`
       - Combine TCGplayer and eBay sales: Use weighted average (TCG × 0.7 + eBay × 0.3)
     - Formula: `expected_days_to_sell = active_listings_count / boxes_sold_per_day`
     - This represents: If you listed your box today, how many days on average until it sells (assuming random order)
   - Bound result: Minimum 1 day, Maximum 365 days (cap at 365)
   - Handle edge cases:
     - No active listings (return None - no listings to compare against)
     - No sales history (boxes_sold_per_day = 0): Return 365 (max) or None
     - Very low sales (boxes_sold_per_day < 0.1): Return 365 (max) to avoid unrealistic predictions
     - Division by zero: Return 365 (max)
   - Note: This metric complements liquidity_score - high liquidity = low expected days, low liquidity = high expected days

8. **Create Unified Metrics Model**
   - Create SQLAlchemy model: `models/unified_box_metrics.py`
   - Map all calculated fields to database columns, including:
     - `expected_days_to_sell` (DECIMAL or FLOAT, nullable)
   - Add foreign key to `booster_boxes`
   - Add unique constraint on `(booster_box_id, metric_date)`

9. **Create Unified Metrics Repository**
   - Create `repositories/unified_metrics_repository.py`
   - Methods:
     - `save_unified_metrics()` - Upsert metrics for date+box
     - `get_metrics_for_date()` - Get metrics for all boxes on date
     - `get_metrics_for_box()` - Get time-series for one box
     - `get_latest_metrics()` - Get most recent metrics for all boxes

10. **Create Daily Unified Metrics Calculation Job**
    - Create Celery task: `tasks/calculate_unified_metrics.py`
    - Task logic:
      - Get all boxes from `booster_boxes`
      - For each box:
        - Get yesterday's date (calculate for previous day)
        - Check if unified metrics already exist for that date (skip if exists)
        - Get TCGplayer metrics from `tcg_box_metrics_daily` (for date)
        - Get eBay metrics from `ebay_box_metrics_daily` (for date, nullable)
        - Call `unified_metrics_calculator.calculate_unified_metrics()` (includes expected_days_to_sell)
        - Save results to `box_metrics_unified` via repository
    - Add error handling (skip box if calculation fails, log error)
    - Add logging (log progress, any calculation issues)

11. **Schedule Unified Metrics Job**
    - Configure Celery Beat to run after both TCGplayer and eBay metrics:
      - Schedule at 4 AM UTC (1 hour after TCGplayer metrics at 3 AM)
    - Add to `celery_config.py`:
      ```python
      'calculate-unified-metrics': {
          'task': 'tasks.calculate_unified_metrics.run_daily_calculation',
          'schedule': crontab(hour=4, minute=0),
      }
      ```
    - Or use task chaining (run after metrics calculations complete)

12. **Backfill Historical Unified Metrics**
    - Create script: `scripts/backfill_unified_metrics.py`
    - For each box, for each date with both TCGplayer and eBay metrics (if available):
      - Calculate unified metrics retroactively (including expected_days_to_sell)
      - Save to database
    - Run once to populate metrics for existing historical data
    - Verify calculations match manual calculations for sample dates

13. **Verify Calculations**
    - Manual verification for one box on one date:
      - Check weighted volume formula: Verify 70/30 split
      - Check liquidity score: Verify 50/30/20 blend
      - Check days-to-20%: Manually count listings below target, verify calculation
      - Check expected_days_to_sell: Verify formula (listings_count / boxes_sold_per_day)
        - Example: 100 listings, 5 boxes sold/day = 20 days (verify calculation matches)
    - Query `box_metrics_unified` table, verify data looks correct
    - Check for NULLs (should only be NULL if data unavailable, not calculation errors)

14. **Add Indexes for Performance**
    - Add indexes to `box_metrics_unified` table:
      - Index on `(booster_box_id, metric_date)` (for time-series queries)
      - Index on `(metric_date, unified_volume_7d_ema)` (for ranking queries)
      - Index on `metric_date` (for latest metrics queries)
    - Create migration for indexes (and expected_days_to_sell field if not already in schema)
    - Run migration

15. **Create Query Helpers**
    - Create helper methods in repository:
      - `get_top_boxes_by_volume(date, limit=10)` - Get top N boxes by volume
      - `get_rank_for_box(box_id, date)` - Get current rank for box
      - These will be used in Phase 6 (Rankings)

**Deliverables:**
- Unified metrics calculation service (`services/unified_metrics_calculator.py`)
- Daily unified metrics Celery task scheduled
- `box_metrics_unified` table populated with calculated metrics
- Weighted volume formula implemented (70/30 TCG/eBay split)
- Final liquidity score implemented (50/30/20 blend)
- Market cap proxy calculated (TCGplayer only)
- Days-to-20% projection implemented (bounded 1-180 days)
- Expected days to sell implemented (bounded 1-365 days)
- Database indexes for performance
- Query helpers for rankings

**Key Rule:**
- **All rankings read from `box_metrics_unified` ONLY**
- No direct queries to per-marketplace tables from API
- Single source of truth for frontend

**Exit Criteria:**
- Unified metrics job runs successfully daily (verified in logs)
- `box_metrics_unified` table has metrics for all boxes with source data
- All formulas verified (manual check of calculations)
- Weighted volume correctly combines TCGplayer and eBay
- Liquidity score correctly blends all components
- Days-to-20% calculation working (bounded correctly)
- Expected days to sell calculation working (bounded 1-365 days, handles edge cases)
- Can query unified metrics for all boxes
- Data ready for rankings (Phase 6)

---

### Phase 6 — Rankings & Caching

**Goal:** Calculate rankings and optimize performance before frontend.

**Actionable Steps:**

1. **Add Rank Field to Unified Metrics Table**
   - Create Alembic migration to add `current_rank` field to `box_metrics_unified` table
   - Add `previous_rank` field (for rank change detection)
   - Add index on `(metric_date, current_rank)` for leaderboard queries
   - Run migration: `alembic upgrade head`

2. **Create Ranking Calculation Service**
   - Create `services/ranking_calculator.py`
   - Method: `calculate_ranks_for_date(date: date) -> Dict[UUID, int]`
   - Logic:
     - Query `box_metrics_unified` for date
     - Order by `unified_volume_7d_ema` DESC (highest volume = rank 1)
     - Assign rank: 1, 2, 3, etc. (handle ties: same rank for equal volumes)
   - Return dictionary: `{box_id: rank}`

3. **Implement Rank Change Detection**
   - Method: `calculate_rank_changes(date: date) -> Dict[UUID, int]`
   - Get current ranks (from Step 2)
   - Get previous ranks from `previous_rank` field (yesterday's current_rank)
   - Calculate change: `rank_change = previous_rank - current_rank`
   - Positive = moved up, negative = moved down, 0 = no change
   - Return dictionary: `{box_id: rank_change}`

4. **Create Daily Ranking Calculation Job**
   - Create Celery task: `tasks/calculate_ranks.py`
   - Task logic:
     - Get yesterday's date (calculate ranks for previous day)
     - Call `ranking_calculator.calculate_ranks_for_date(yesterday)`
     - For each box:
       - Update `box_metrics_unified.current_rank` for that date
       - Store previous rank before updating (save to `previous_rank`)
     - Calculate rank changes using previous rank
     - Update rank_change field (add to table if needed)
   - Add error handling and logging

5. **Schedule Ranking Job**
   - Configure Celery Beat to run after unified metrics calculation
   - Schedule at 4:30 AM UTC (30 minutes after unified metrics at 4 AM)
   - Add to `celery_config.py`:
     ```python
     'calculate-ranks': {
         'task': 'tasks.calculate_ranks.run_daily_calculation',
         'schedule': crontab(hour=4, minute=30),
     }
     ```

6. **Setup Redis**
   - Install Redis: `sudo apt-get install redis` (Linux) or `brew install redis` (Mac)
   - Or use cloud Redis (Redis Cloud, AWS ElastiCache, etc.)
   - Install Python Redis client: `pip install redis`
   - Configure Redis connection (host, port, password if needed)
   - Store connection config in environment variables
   - Test connection: `redis-cli ping` (should return PONG)

7. **Create Redis Cache Service**
   - Create `services/cache_service.py`
   - Create CacheService class with methods:
     - `get(key: str) -> Optional[Any]`
     - `set(key: str, value: Any, ttl: int = 300)`
     - `delete(key: str)`
     - `exists(key: str) -> bool`
   - Serialize/deserialize JSON for complex objects
   - Handle Redis connection errors gracefully (log and continue without cache)

8. **Implement Leaderboard Caching**
   - Create cache keys:
     - `leaderboard:top10:{date}` - Top 10 boxes for date
     - `leaderboard:top50:{date}` - Top 50 boxes for date
     - `box:detail:{box_id}:{date}` - Individual box metrics for date
   - Create method: `cache_leaderboard(date: date, limit: int = 10)`
   - Logic:
     - Query `box_metrics_unified` ordered by `current_rank` ASC, limit N
     - Serialize results to JSON
     - Store in Redis with TTL: 15 minutes (900 seconds)
   - Create method: `get_cached_leaderboard(date: date, limit: int) -> Optional[List]`
   - Check cache first, return if exists, else return None

9. **Implement Cache Warming Strategy**
   - Create Celery task: `tasks/warm_cache.py`
   - Task logic:
     - Get today's date
     - Call `cache_service.cache_leaderboard(today, limit=10)`
     - Call `cache_service.cache_leaderboard(today, limit=50)`
     - For each box, cache detail: `cache_service.cache_box_detail(box_id, today)`
   - Schedule to run after ranking calculation (4:35 AM UTC)
   - Add to Celery Beat config

10. **Create Leaderboard Query Service**
    - Create `services/leaderboard_service.py`
    - Method: `get_top_boxes(date: date, limit: int = 10) -> List[BoxMetrics]`
    - Logic:
      - Try cache first: `cache_service.get_cached_leaderboard(date, limit)`
      - If cache miss:
        - Query database: SELECT from `box_metrics_unified` WHERE metric_date = date ORDER BY current_rank ASC LIMIT limit
        - Cache result for next time
      - Return list of box metrics with ranks

11. **Performance Optimization**
    - Add database indexes (if not already present):
      - Index on `(metric_date, current_rank)` for leaderboard queries
      - Index on `(booster_box_id, metric_date)` for box detail queries
    - Verify query performance:
      - Run EXPLAIN ANALYZE on leaderboard query
      - Target: <50ms for top 10 query, <100ms for top 50
    - If queries are slow:
      - Review query plans, add missing indexes
      - Consider materialized views if needed
      - Optimize JOINs if any

12. **Performance Benchmarking**
    - Create benchmark script: `scripts/benchmark_queries.py`
    - Test scenarios:
      - Leaderboard top 10 (cached): Should be <10ms
      - Leaderboard top 10 (uncached): Should be <50ms
      - Leaderboard top 50 (cached): Should be <10ms
      - Leaderboard top 50 (uncached): Should be <200ms
      - Box detail (cached): Should be <10ms
      - Box detail (uncached): Should be <50ms
    - Run benchmarks and document results
    - Optimize until all targets met

13. **Create Cache TTL Strategy**
    - Define TTL values:
      - Leaderboard cache: 15 minutes (900 seconds)
      - Box detail cache: 10 minutes (600 seconds)
      - Time-series cache: 30 minutes (1800 seconds)
    - Document strategy in code comments
    - Make TTLs configurable via environment variables

14. **Backfill Historical Ranks**
    - Create script: `scripts/backfill_ranks.py`
    - For each date with unified metrics but no ranks:
      - Calculate ranks retroactively
      - Update `current_rank` field
      - Calculate rank changes
    - Run once for existing historical data

15. **Verification**
    - Query `box_metrics_unified` table, verify ranks assigned (1, 2, 3, etc.)
    - Verify rank changes calculated correctly (compare to manual calculation)
    - Test cache: Set value, retrieve value, verify TTL expiration
    - Run benchmarks: Verify all queries meet <200ms target

**Deliverables:**
- Ranking calculation service (`services/ranking_calculator.py`)
- Daily ranking Celery task scheduled
- `current_rank` and `previous_rank` fields added to `box_metrics_unified`
- Rank change detection working (up/down arrows data ready)
- Redis cache service (`services/cache_service.py`)
- Leaderboard caching implemented
- Cache warming job scheduled
- Performance benchmarks: All queries <200ms (cached <10ms)
- Database indexes optimized

**Why Before Frontend:**
- **Performance locked before frontend goes live**
- Frontend depends on fast, cached endpoints
- No point building UI if backend is slow

**Exit Criteria:**
- Ranking job runs successfully daily (verified in logs)
- All boxes have ranks assigned in `box_metrics_unified` table
- Rank changes calculated correctly (verified manually)
- Redis caching working (can get/set/delete keys)
- Leaderboard queries <200ms uncached, <10ms cached (verified via benchmarks)
- Cache TTL strategy defined and documented
- Cache warming job runs after rankings

---

### Phase 7 — API Layer

**Goal:** Expose read-only endpoints for frontend consumption.

**Actionable Steps:**

1. **Setup FastAPI Application**
   - Create `app/main.py` with FastAPI app instance
   - Configure CORS middleware (allow frontend domain)
   - Configure JSON serialization (ensure Decimal → float conversion)
   - Add request logging middleware
   - Add error handling middleware (catch exceptions, return 500)

2. **Create Pydantic Response Models**
   - Create `schemas/booster_box.py` with response models
   - Model: `LeaderboardBoxResponse` (matches Phase 0 spec):
     - `id` (UUID), `product_name` (str), `image_url` (str), `current_rank` (int)
     - `rank_change` (int, +1/-1/0), `unified_volume_7d_ema` (float)
     - `floor_price_usd` (float), `floor_price_change_24h` (float), `liquidity_score` (float)
   - Model: `BoxDetailResponse` (full box details for advanced analytics):
     - All fields from LeaderboardBoxResponse (for consistency)
     - Additional detail fields:
       - `set_name`, `release_date`, `game_type`, `reprint_risk`
       - `visible_market_cap_usd`, `days_to_20_percent`, `expected_days_to_sell`
       - `liquidity_score`, `absorption_rate`
     - `time_series_data`: Array of daily metrics (last 30 days) for chart and table
       - Each entry: `date`, `floor_price_usd`, `volume`, `listings_count`, `sales_count`, `market_cap`
     - `rank_history`: Array of rank positions over time (last 30 days)
       - Each entry: `date`, `rank`, `rank_change`
   - This model supports the advanced analytics detail page shown when user clicks on a box from the leaderboard
   - Model: `TimeSeriesDataPoint`:
     - `date` (date), `floor_price_usd` (float), `volume` (float), `listings_count` (int)

3. **Create API Router Module**
   - Create `routers/booster_boxes.py`
   - Import FastAPI Router
   - Create router instance: `router = APIRouter(prefix="/api/v1/booster-boxes", tags=["booster-boxes"])`
   - Include router in main app

4. **Implement Leaderboard Endpoint**
   - Create endpoint: `GET /api/v1/booster-boxes`
   - Query parameters:
     - `limit` (int, default=10, max=50)
     - `date` (date, optional, default=today)
   - Logic:
     - Call `leaderboard_service.get_top_boxes(date, limit)` (from Phase 6)
     - Map database models to Pydantic response models
     - Return JSON response
   - Add response model: `List[LeaderboardBoxResponse]`
   - Handle errors: 404 if no data, 400 for invalid parameters

5. **Calculate Price Change (24h)**
   - Create helper: `calculate_price_change_24h(box_id, date) -> float`
   - Get today's floor_price from `box_metrics_unified`
   - Get yesterday's floor_price from `box_metrics_unified`
   - Calculate: `change = ((today - yesterday) / yesterday) × 100`
   - Handle missing data: Return None or 0 if no yesterday data
   - Add this to leaderboard response mapping

6. **Implement Box Detail Endpoint**
   - Create endpoint: `GET /api/v1/booster-boxes/{box_id}`
   - Path parameter: `box_id` (UUID)
   - Query parameter: `date` (date, optional, default=today)
   - Logic:
     - Get box from `booster_boxes` table (verify exists, 404 if not)
     - Get unified metrics from `box_metrics_unified` for date
     - Combine box data + metrics data
     - Map to `BoxDetailResponse` model
     - Return JSON response
   - Add caching: Check cache first, cache result if miss

7. **Implement Time-Series Endpoint**
   - Create endpoint: `GET /api/v1/booster-boxes/{box_id}/time-series`
   - Path parameter: `box_id` (UUID)
   - Query parameters:
     - `start_date` (date, optional, default=30 days ago)
     - `end_date` (date, optional, default=today)
   - Logic:
     - Verify box exists (404 if not)
     - Query `box_metrics_unified` for date range:
       - SELECT * WHERE booster_box_id = box_id AND metric_date BETWEEN start_date AND end_date
       - ORDER BY metric_date ASC
     - Map to `List[TimeSeriesDataPoint]`
     - Return JSON response
   - Add caching for common queries (last 30 days)

8. **Implement Sparkline Data Endpoint**
   - Create endpoint: `GET /api/v1/booster-boxes/{box_id}/sparkline`
   - Path parameter: `box_id` (UUID)
   - Query parameter: `days` (int, default=30)
   - Logic:
     - Get last N days of floor_price_usd from `box_metrics_unified`
     - Return simple array: `[price1, price2, price3, ...]`
     - Return JSON: `{"prices": [123.45, 124.50, ...]}`
   - Optimized for small payload (sparklines need minimal data)

9. **Add Response Validation**
   - Ensure all Decimal fields converted to float (JSON serialization)
   - Handle NULL values (return None in JSON)
   - Validate UUID format in path parameters
   - Validate date formats in query parameters
   - Return 422 for validation errors

10. **Add Error Handling**
    - Create custom exceptions:
      - `BoxNotFoundError` (404)
      - `InvalidDateError` (400)
    - Create error handler middleware
    - Map exceptions to appropriate HTTP status codes
    - Return consistent error response format:
      ```json
      {"error": "Box not found", "detail": "..."}
      ```

11. **Enable OpenAPI Documentation**
    - FastAPI auto-generates OpenAPI schema
    - Access docs at `/docs` (Swagger UI)
    - Access schema at `/openapi.json`
    - Verify all endpoints appear in docs
    - Verify response models documented correctly
    - Add endpoint descriptions (docstrings)

12. **Add API Versioning**
    - Use `/api/v1/` prefix for all endpoints
    - Prepare for future v2 (structure allows easy versioning)
    - Document versioning strategy

13. **Performance Testing**
    - Test all endpoints with realistic data:
      - Leaderboard (10 boxes): Should be <10ms (cached) or <50ms (uncached)
      - Box detail: Should be <10ms (cached) or <50ms (uncached)
      - Time-series (30 days): Should be <100ms
    - Use `time` module or profiling tools
    - Verify cache is working (first request slower, second request faster)

14. **Integration Testing**
    - Create test file: `tests/test_api.py`
    - Test each endpoint:
      - Test successful responses (200)
      - Test 404 for non-existent box
      - Test 400 for invalid parameters
      - Test response shape matches Pydantic models
    - Run tests: `pytest tests/test_api.py`

15. **Update OpenAPI Spec (If Needed)**
    - Compare auto-generated OpenAPI spec to Phase 0 specification
    - Ensure response shapes match exactly
    - Add any missing descriptions or examples
    - Export spec: Save `/openapi.json` to file for frontend team

16. **Prepare for Authentication (Phase 8)**
    - Add dependency injection placeholder for auth:
      - Create `dependencies/auth.py` with `get_current_user()` function
      - Make it optional for now (return None)
      - Add to endpoints as dependency (but don't enforce yet)
    - Structure allows easy addition of auth in Phase 8

**Deliverables:**
- FastAPI application (`app/main.py`)
- API router (`routers/booster_boxes.py`)
- Pydantic response models (`schemas/booster_box.py`)
- Leaderboard endpoint: `GET /api/v1/booster-boxes` working
- Box detail endpoint: `GET /api/v1/booster-boxes/{id}` working
- Time-series endpoint: `GET /api/v1/booster-boxes/{id}/time-series` working
- Sparkline endpoint: `GET /api/v1/booster-boxes/{id}/sparkline` working
- OpenAPI documentation accessible at `/docs`
- All endpoints return responses matching Phase 0 specification
- Error handling implemented (404, 400, 422, 500)
- Performance verified (<200ms for all endpoints)

**Key Principle:**
- **Frontend consumes precomputed data only**
- No real-time calculations in API
- All data comes from unified metrics table
- Fast, simple queries

**Exit Criteria:**
- All endpoints working (tested with curl/Postman)
- API docs complete (accessible at `/docs`, all endpoints documented)
- Response shapes match Phase 0 specification (verified manually)
- Performance targets met (<200ms, cached <10ms)
- Integration tests passing
- Ready for frontend integration (frontend can consume API)

---

### Phase 8 — Monetization

**Goal:** Add authentication and payment system.

**Actionable Steps:**

1. **Create Users Database Schema**
   - Create Alembic migration for `users` table:
     - `id` (UUID, primary key)
     - `email` (VARCHAR, unique, not null)
     - `hashed_password` (VARCHAR, not null)
     - `created_at` (TIMESTAMP)
     - `trial_started_at` (TIMESTAMP, nullable)
     - `trial_ended_at` (TIMESTAMP, nullable)
     - `subscription_status` (ENUM: 'trial', 'active', 'expired', 'cancelled')
     - `stripe_customer_id` (VARCHAR, nullable, unique)
     - `stripe_subscription_id` (VARCHAR, nullable)
   - Add indexes: `email`, `stripe_customer_id`
   - Run migration: `alembic upgrade head`

2. **Create User Model**
   - Create SQLAlchemy model: `models/user.py`
   - Map all fields from database schema
   - Add password hashing helper methods
   - Add methods: `verify_password()`, `is_trial_active()`, `has_active_subscription()`

3. **Implement Password Hashing**
   - Install: `pip install passlib[bcrypt]`
   - Create utility: `utils/password.py`
   - Functions:
     - `hash_password(password: str) -> str` (use bcrypt)
     - `verify_password(plain_password: str, hashed_password: str) -> bool`
   - Test password hashing and verification

4. **Create JWT Authentication**
   - Install: `pip install python-jose[cryptography]`
   - Create utility: `utils/jwt.py`
   - Functions:
     - `create_access_token(data: dict, expires_delta: timedelta) -> str`
     - `decode_access_token(token: str) -> dict`
   - Configure JWT secret key (from environment variable)
   - Configure token expiration (e.g., 7 days for access token)

5. **Create User Repository**
   - Create `repositories/user_repository.py`
   - Methods:
     - `create_user(email: str, password: str) -> User`
     - `get_user_by_email(email: str) -> Optional[User]`
     - `get_user_by_id(user_id: UUID) -> Optional[User]`
     - `update_user(user: User) -> User`

6. **Implement User Registration Endpoint**
   - Create endpoint: `POST /api/v1/auth/register`
   - Request body: `{"email": "user@example.com", "password": "password123"}`
   - Logic:
     - Validate email format and password strength
     - Check if email already exists (return 409 Conflict if exists)
     - Hash password
     - Create user with `trial_started_at = now()`, `trial_ended_at = now() + 7 days`
     - Set `subscription_status = 'trial'`
     - Save to database
     - Return 201 Created with user data (no password)
   - Add Pydantic models for request/response

7. **Implement User Login Endpoint**
   - Create endpoint: `POST /api/v1/auth/login`
   - Request body: `{"email": "user@example.com", "password": "password123"}`
   - Logic:
     - Get user by email (return 401 if not found)
     - Verify password (return 401 if incorrect)
     - Create JWT access token (include user_id in token payload)
     - Return 200 OK with token: `{"access_token": "...", "token_type": "bearer"}`
   - Add Pydantic models for request/response

8. **Create Authentication Dependency**
   - Update `dependencies/auth.py` (placeholder from Phase 7)
   - Function: `get_current_user(token: str = Depends(oauth2_scheme)) -> User`
   - Logic:
     - Extract token from Authorization header (Bearer token)
     - Decode JWT token (return 401 if invalid)
     - Get user by ID from token payload
     - Return user (return 401 if user not found)
   - Use FastAPI's `HTTPBearer` for token extraction

9. **Add Authentication to API Endpoints**
   - Update all endpoints from Phase 7:
     - Add `user: User = Depends(get_current_user)` to each endpoint
     - Endpoints now require valid JWT token
   - Test endpoints with and without token (should return 401 without token)

10. **Setup Stripe Account**
    - Sign up for Stripe account (stripe.com)
    - Obtain API keys:
      - Publishable key (public)
      - Secret key (private)
    - Store keys in environment variables
    - Install Stripe Python SDK: `pip install stripe`
    - Test connection: `stripe.Customer.list(limit=1)`

11. **Create Stripe Service**
    - Create `services/stripe_service.py`
    - Methods:
      - `create_customer(email: str) -> stripe.Customer`
      - `create_subscription(customer_id: str, price_id: str) -> stripe.Subscription`
      - `cancel_subscription(subscription_id: str) -> stripe.Subscription`
      - `get_subscription(subscription_id: str) -> stripe.Subscription`
    - Handle Stripe API errors gracefully

12. **Implement Trial Logic**
    - Create service: `services/subscription_service.py`
    - Method: `check_trial_status(user: User) -> bool`
    - Logic:
      - If `trial_started_at` is NULL, return False (no trial started)
      - If `trial_ended_at` > now(), return True (trial active)
      - Otherwise, return False (trial expired)
    - Method: `has_active_access(user: User) -> bool`
    - Logic:
      - Return True if trial active OR subscription active
      - Check `subscription_status == 'active'` OR trial active

13. **Create Payment Intent Endpoint**
    - Create endpoint: `POST /api/v1/payments/create-intent`
    - Requires authentication (user must be logged in)
    - Logic:
      - Get or create Stripe customer for user
      - Create Stripe PaymentIntent for subscription
      - Return client_secret for frontend Stripe.js integration
    - Add Pydantic models for request/response

14. **Implement Stripe Webhook Handler**
    - Create endpoint: `POST /api/v1/webhooks/stripe`
    - Verify webhook signature (Stripe webhook secret)
    - Handle events:
      - `customer.subscription.created` - Update user subscription_status to 'active'
      - `customer.subscription.updated` - Update subscription status
      - `customer.subscription.deleted` - Update subscription_status to 'cancelled'
      - `invoice.payment_succeeded` - Ensure subscription is active
      - `invoice.payment_failed` - Handle payment failure
    - Update user record in database based on webhook events

15. **Implement Paywall Middleware**
    - Create dependency: `dependencies/paywall.py`
    - Function: `require_active_subscription(user: User = Depends(get_current_user)) -> User`
    - Logic:
      - Check if user has active access (trial or subscription)
      - If no active access, raise HTTPException 403 Forbidden
      - Return user if access granted
    - Add this dependency to all API endpoints (except auth endpoints)

16. **Update User Model with Subscription Methods**
    - Add method to User model: `has_active_access() -> bool`
    - Add method: `days_remaining_in_trial() -> int`
    - Add method: `is_subscription_active() -> bool`
    - Use these methods in paywall checks

17. **Create Subscription Management Endpoints**
    - Endpoint: `GET /api/v1/users/me/subscription`
      - Returns current subscription status, trial info
    - Endpoint: `POST /api/v1/users/me/subscription/cancel`
      - Cancels Stripe subscription
      - Updates user subscription_status to 'cancelled'
    - Endpoint: `GET /api/v1/users/me`
      - Returns current user info (email, subscription status)

18. **Add Subscription Status to API Responses (Optional)**
    - Add subscription info to user context
    - Include trial days remaining in API responses
    - Frontend can show trial countdown

19. **Testing Authentication Flow**
    - Test registration: Create new user, verify user created
    - Test login: Login with credentials, verify JWT token returned
    - Test protected endpoints: Access with token (should work), without token (should fail)
    - Test trial: Verify new user gets 7-day trial
    - Test paywall: Verify expired trial blocks API access

20. **Testing Stripe Integration**
    - Use Stripe test mode
    - Test customer creation
    - Test subscription creation
    - Test webhook handling (use Stripe CLI: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe`)
    - Test payment flow end-to-end

21. **Add Rate Limiting (Optional but Recommended)**
    - Install: `pip install slowapi`
    - Add rate limiting to auth endpoints (prevent brute force)
    - Add rate limiting to API endpoints (prevent abuse)
    - Configure limits: e.g., 5 requests/minute for login, 100 requests/minute for API

22. **Security Hardening**
    - Ensure passwords are never returned in API responses
    - Use HTTPS in production (TLS/SSL)
    - Store JWT secret securely (environment variable, never in code)
    - Store Stripe keys securely (environment variables)
    - Add CORS restrictions (only allow frontend domain)
    - Add request rate limiting

**Deliverables:**
- Users table and model (`models/user.py`)
- Password hashing utility (`utils/password.py`)
- JWT authentication utility (`utils/jwt.py`)
- User repository (`repositories/user_repository.py`)
- Registration endpoint: `POST /api/v1/auth/register`
- Login endpoint: `POST /api/v1/auth/login`
- Authentication dependency (`dependencies/auth.py`)
- Stripe service (`services/stripe_service.py`)
- Subscription service (`services/subscription_service.py`)
- Payment intent endpoint: `POST /api/v1/payments/create-intent`
- Stripe webhook handler: `POST /api/v1/webhooks/stripe`
- Paywall middleware (`dependencies/paywall.py`)
- Subscription management endpoints
- All API endpoints protected with authentication and paywall

**Exit Criteria:**
- Users can register (verified via endpoint test)
- Users can login and receive JWT token (verified)
- 7-day trial automatically assigned on registration (verified in database)
- Trial expiration blocks API access (verified: expired trial returns 403)
- Stripe customer created when user subscribes (verified in Stripe dashboard)
- Payment processing working (verified with Stripe test cards)
- Webhook handler updates subscription status (verified via Stripe CLI)
- Paywall enforced on all API endpoints (verified: unauthorized access returns 401/403)
- Subscription cancellation working (verified: cancels in Stripe and database)
- Ready for public launch (all authentication and payment flows tested)

---

## 📊 Key Metrics (Defined Early)

These metrics are defined and implemented across phases 3-5:

### Volume
- **Formula:** Weighted TCG + eBay
- **Weighting:** (TCG × 0.7) + (eBay × 0.3)
- **Primary Ranking Metric:** unified_volume_7d_ema

### Liquidity Score
- **Formula:** Absorption × velocity × consistency
- **Components:** (Boxes Sold / Boxes Listed × 0.5) + (7d Velocity EMA × 0.3) + (eBay Frequency × 0.2)
- **Purpose:** Ranking & signals, not pricing

### Market Cap Proxy
- **Formula:** Listings × floor price
- **Source:** TCGplayer only
- **Note:** Proxy, not actual market cap

### Days to +20% Projection
- **Formula:** Remaining boxes to price tier ÷ Average daily buy rate (30d)
- **Bounded:** Max 180 days
- **Label:** Always labeled as "Projected"
- **Note:** Not a promise, just a signal

### Expected Days to Sell
- **Formula:** Active listings count ÷ Average boxes sold per day (30d)
- **Bounded:** Min 1 day, Max 365 days
- **Sources:** TCGplayer listings count + weighted sales velocity (TCG × 0.7 + eBay × 0.3)
- **Purpose:** Estimate how long it would take to sell a box if listed today (assuming random order)
- **Label:** Always labeled as "Expected" or "Projected"
- **Note:** Based on historical sales velocity and current market depth, not a guarantee

---

## 🚧 Explicit Non-Goals (MVP)

These are **explicitly out of scope** for MVP:

- ❌ Portfolio tracking
- ❌ Perfect sales accuracy
- ❌ Supply estimates
- ❌ Real-time updates (daily snapshots only)
- ❌ ML predictions
- ❌ Multi-market deduplication (at listing level)
- ❌ Multi-language support
- ❌ Social features (beyond favorites)
- ❌ Push notifications

**Focus:** Core market intelligence only.

---

## 🧭 Engineering Principles

These principles guide all implementation decisions:

1. **Conservative > aggressive**
   - Better to undercount than overcount
   - Prefer false negatives to false positives

2. **Under-count > over-count**
   - Volume calculations err on low side
   - Sales inference is conservative

3. **Precompute everything**
   - All expensive calculations done in background jobs
   - API is read-only, fast queries only

4. **No cross-market raw data mixing**
   - TCGplayer and eBay stay separate at raw level
   - Unification only at metrics layer

5. **MVP first, accuracy second, scale third**
   - Get working product first
   - Refine accuracy with real data
   - Scale after validation

---

## 🥇 Build Priority (If Anything Slips)

If timeline is compressed, prioritize in this order:

1. **Box registry** (Phase 1)
   - Foundation for everything else

2. **TCGplayer and eBay ingestion** (Phases 2, 4)
   - Data collection is critical

3. **Daily metrics** (Phases 3, 5)
   - Needed for any functionality

4. **Leaderboard** (Phase 6)
   - Core user-facing feature

5. **Paywall** (Phase 8)
   - Monetization, but can launch without it initially

**Can Defer:**
- Phase 0 (UX planning) - Can be done in parallel
- Phase 7 (API layer) - Can use basic endpoints
- Some Phase 8 features (can launch with basic auth first)

---

## 📋 Phase Dependencies

**Manual-First Build Path (MVP):**
```
Phase 0 (UX Planning)
  ↓ (no dependency)
Phase 1 (Box Registry)
  ↓
Phase 2 (Manual Metrics Entry)
  ↓
Phase 3 (Unified Metrics Calculation)
  ↓
Phase 5 (Enhanced Unified Metrics)
  ↓
Phase 6 (Rankings & Caching)
  ↓
Phase 7 (API Layer)
  ↓
Phase 8 (Monetization)
```

**Future API Integration Phases (Post-MVP):**
```
Phase 2B (Future: TCGplayer API Integration) ──┐
  ↓                                            │
Phase 4 (Future: eBay Integration) ────────────┼──┐
  ↓                                            │  │
Phase 5B (Future: Enhanced Metrics with APIs) ←┘  │
  ↓                                               │
(Enhance Phase 3/5 calculations with API data) ←─┘
```

**Parallel Work Possible:**
- Phase 0 can be done anytime
- Phase 7 (API Layer) can start after Phase 5 (doesn't need Phase 6 complete)
- Frontend development can start after Phase 7
- Future API phases (2B, 4, 5B) can be done in any order after MVP is complete

---

## ✅ Exit Criteria Summary

Each phase must meet these criteria before moving to next:

- **Phase 0:** API shapes locked, UI designs approved
- **Phase 1:** 10 boxes registered, mappings complete
- **Phase 2:** Daily snapshots working, raw data stored
- **Phase 3:** Metrics calculated, app usable (basic)
- **Phase 4:** eBay sales ingested, metrics calculated
- **Phase 5:** Unified metrics working, formulas correct
- **Phase 6:** Rankings fast, caching working (<200ms)
- **Phase 7:** API endpoints working, docs complete
- **Phase 8:** Auth + payments working, ready to launch

---

## 🎯 MVP Definition

**MVP = Phases 0-7 Complete (Manual-First):**
- Phase 0: UX + API planning
- Phase 1: Box registry (10 boxes manually created)
- Phase 2: Manual metrics entry system + admin panel
- Phase 3: Unified metrics calculation from manual data
- Phase 5: Enhanced unified metrics (all derived metrics)
- Phase 6: Rankings & caching
- Phase 7: API layer (frontend-ready endpoints)
- **App is fully functional with manual data entry**

**MVP + Monetization = Phases 0-8:**
- Everything above + authentication + payments (Phase 8)
- Ready for public launch with paywall
- Manual data entry workflow for data updates

**Future Enhancement (Post-MVP):**
- Phase 2B: TCGplayer API integration (automation)
- Phase 4: eBay integration (enhanced metrics)
- Phase 5B: Enhanced unified metrics with API data blending
- These phases add automation but don't change frontend or core functionality

