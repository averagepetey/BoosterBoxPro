# Manual-First Development Approach

> **Strategy:** Build the app with manual data entry first, then seamlessly swap to API integration later.

## 🎯 Why Manual-First?

**Benefits:**
- ✅ **Build UI/UX immediately** - No waiting for API access or integration
- ✅ **Test core functionality** - Validate metrics, rankings, calculations work correctly
- ✅ **Iterate quickly** - Change data instantly, see results immediately
- ✅ **Validate concept** - Prove the app works before investing in API costs
- ✅ **Seamless transition** - Same database schema, just swap data source

**Perfect for:**
- MVP development
- Testing and validation
- UI/UX iteration
- Demo purposes
- Learning the data structure

---

## 📊 Data Entry Method: Screenshot Upload

### Primary Method: Screenshot-Based Entry

**How It Works:**
1. Take screenshot of marketplace page (TCGplayer, eBay, etc.)
2. Upload screenshot via web interface or API
3. System extracts data using OCR + AI/ML
4. Review and confirm extracted values
5. Save to database

**Best for:** Quick daily updates, minimal typing, natural workflow

**Workflow:**
```
1. Browse marketplace (TCGplayer/eBay) on your device
2. Take screenshot of listing page
3. Upload screenshot to admin panel
4. System extracts: floor price, listings count, prices, etc.
5. Review extracted values (edit if needed)
6. Select box and date
7. Save → Data appears in app immediately
```

### Screenshot Requirements

**What to Screenshot:**
- TCGplayer product listing page (shows all listings with prices)
- eBay sold listings page (for sales data)
- Marketplace search results page
- Any page showing relevant metrics

**What Data Gets Extracted:**
- Floor price (lowest listing price)
- Active listings count
- Prices of top listings
- Any visible metrics (volume, sales count, etc.)

### Implementation Features

**Image Upload Interface:**
- Drag-and-drop image upload
- File picker support
- Multiple format support (PNG, JPG, JPEG)
- Mobile-friendly (camera upload)

**AI/OCR Processing:**
- OCR text extraction from screenshot
- AI parsing to identify structured data (prices, counts, etc.)
- Pattern recognition for marketplace layouts
- Confidence scoring for extracted values

**Review & Edit Interface:**
- Display extracted values in editable form
- Highlight low-confidence extractions
- Allow manual correction before saving
- Support for multiple boxes in one screenshot (if applicable)

### Alternative: API Endpoint (For Programmatic Access)

**For developers/scripts:**
- REST API endpoint for direct data entry
- Same format as screenshot extraction output
- Useful for batch imports or automation

**Example:**
```bash
POST /api/v1/admin/manual-metrics
{
  "date": "2024-12-29",
  "booster_box_id": "uuid-here",
  "floor_price_usd": 120.00,
  "active_listings_count": 45,
  "boxes_sold_today": 3,
  "daily_volume_usd": 360.00,
  "visible_market_cap_usd": 5400.00
}
```

---

## 🗄️ Database Schema (Unchanged)

**Key Point:** The database schema stays exactly the same! We're just populating it manually instead of via API.

### Manual Entry → Same Tables

**For Daily Metrics:**
- Insert directly into `box_metrics_unified` table
- Skip raw data tables (`tcg_listings_raw`, `ebay_sales_raw`) for now
- Calculate derived metrics (EMAs, days_to_20pct) from manual entries

**For Box Registry:**
- Still use `booster_boxes` table
- Manually create entries for 10 One Piece boxes
- Add image URLs, names, etc. manually

---

## 🔄 Transition Path: Manual → API

### Phase 1: Manual Mode (MVP)
```
User Input → Admin Panel → Database → API → Frontend
```

**What you enter:**
- Daily metrics per box
- Floor price, listings, sales, volume, etc.

**What the system does:**
- Stores in `box_metrics_unified`
- Calculates rankings, EMAs, days_to_20pct
- Serves via API to frontend
- Everything works exactly as designed!

### Phase 2: API Integration (Later)
```
Marketplace APIs → Ingestion Jobs → Raw Tables → Calculation Pipeline → Unified Metrics → API → Frontend
```

**Transition Steps:**
1. Keep manual entry working (backup/fallback)
2. Build API ingestion jobs (run in parallel)
3. Compare manual vs API data (validation)
4. Switch API to primary, manual to backup
5. Eventually remove manual entry (optional)

**No Code Changes Needed:**
- Same database tables
- Same API endpoints
- Same frontend code
- Just swap data source!

---

## 🛠️ Implementation Plan

### Step 1: Build Screenshot Upload System

**Tech Stack:**
- Image upload interface (React/Next.js with drag-and-drop)
- FastAPI endpoint: `POST /api/v1/admin/upload-screenshot`
- OCR Service: Tesseract or Google Cloud Vision API
- AI/ML Service: OpenAI Vision API or Claude for structured extraction
- Image storage: Local filesystem or cloud storage (S3, etc.)

**Features:**
- Drag-and-drop image upload
- Image preview
- Processing status indicator
- Extracted data review/edit form
- Date picker
- Box selector (dropdown)
- Save confirmation

**Processing Pipeline:**
```
1. Upload screenshot
2. OCR extraction (extract all text from image)
3. AI parsing (identify structured data: prices, counts, metrics)
4. Return extracted values with confidence scores
5. User reviews/edits values
6. Select box and date
7. Save to database
```

**Example Implementation:**
```python
# FastAPI endpoint
@router.post("/admin/upload-screenshot")
async def upload_screenshot(
    file: UploadFile,
    current_user: User = Depends(require_admin)
):
    # Save uploaded image
    # Run OCR extraction
    # Run AI parsing to extract structured data
    # Return extracted values with confidence scores
    return {"extracted_data": {...}, "confidence": {...}}

@router.post("/admin/confirm-extracted-metrics")
async def confirm_extracted_metrics(
    data: ExtractedMetricsInput,  # User-reviewed values
    current_user: User = Depends(require_admin)
):
    # Insert into box_metrics_unified
    # Calculate derived metrics (EMAs, etc.)
    # Return success
```

### Step 2: Build Frontend App

**Use manual data:**
- Same API endpoints (`GET /api/v1/booster-boxes`)
- Same response format
- Frontend doesn't know data is manual!

**Features:**
- Leaderboard table
- Box detail pages
- Rankings, sparklines, etc.
- All working with manual data

### Step 3: Add API Integration (Later)

**When ready:**
- Build marketplace adapters
- Add ingestion jobs
- Populate raw data tables
- Run calculation pipeline
- Same `box_metrics_unified` table gets populated automatically

**Frontend:** No changes needed!

**Screenshot system:** Can remain as backup/validation method

---

## 📝 Manual Entry Workflow

### Daily Routine (Manual Mode)

1. **Morning:** Check marketplace websites
2. **Enter Data:** Use admin panel to input:
   - Floor price (lowest listing)
   - Active listings count
   - Boxes sold (estimate or count)
   - Boxes added (new listings)
   - Volume USD (calculate from sales)
   - Market cap (sum of all listings)
3. **Save:** Data appears in app immediately
4. **Verify:** Check leaderboard, rankings update correctly

### Data Sources (Manual Mode)

**Where to get data:**
- TCGplayer website (browse listings manually)
- eBay sold listings (count manually)
- Your own tracking spreadsheet
- Marketplace APIs (if you have access, but enter manually)

**Time Investment:**
- ~5-10 minutes per day for 10 boxes
- Can batch enter multiple days
- Can backfill historical data

---

## 🎨 Admin Panel UI Mockup

### Main Screen
```
┌─────────────────────────────────────────┐
│  Manual Metrics Entry                   │
├─────────────────────────────────────────┤
│                                         │
│  Date: [2024-12-29] 📅                 │
│                                         │
│  Box: [One Piece OP-01 ▼]              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Floor Price:     [$120.00]     │   │
│  │ Active Listings: [45]          │   │
│  │ Boxes Sold:      [3]           │   │
│  │ Boxes Added:     [2]           │   │
│  │ Volume USD:      [$360.00]     │   │
│  │ Market Cap:      [$5,400.00]   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Save]  [Save & Next Box]  [Cancel]  │
│                                         │
│  Recent Entries:                        │
│  • OP-01 - Dec 29 - $120.00            │
│  • OP-02 - Dec 29 - $95.00             │
│                                         │
└─────────────────────────────────────────┘
```

### Bulk Entry Screen
```
┌─────────────────────────────────────────┐
│  Bulk Entry - 2024-12-29                │
├─────────────────────────────────────────┤
│                                         │
│  [OP-01] Floor: [120] Listings: [45]  │
│  [OP-02] Floor: [95]  Listings: [32]  │
│  [OP-03] Floor: [110] Listings: [28]   │
│  ...                                    │
│                                         │
│  [Save All]  [Import CSV]               │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔐 Security & Access

### Admin Authentication

**Simple Approach (MVP):**
- Single admin password
- Environment variable
- Basic auth or simple JWT

**Production Approach:**
- Full user system
- Admin role/permissions
- Audit logging
- Rate limiting

### Access Control

**Manual Entry Endpoints:**
- Admin only (not public)
- Rate limited (prevent abuse)
- Logged (audit trail)

**Public API:**
- Same as always
- No changes needed
- Reads from same database

---

## ✅ Advantages of This Approach

1. **Start Building Immediately**
   - No waiting for API access
   - No API costs during development
   - Full control over data

2. **Validate Everything**
   - Test all calculations
   - Verify rankings work
   - Check UI/UX flows
   - Ensure metrics make sense

3. **Iterate Quickly**
   - Change data instantly
   - Test edge cases easily
   - Try different scenarios
   - See results immediately

4. **Seamless Transition**
   - Same database schema
   - Same API endpoints
   - Same frontend code
   - Just swap data source

5. **Fallback Option**
   - Keep manual entry as backup
   - Use if APIs fail
   - Use for testing
   - Use for corrections

---

## 🚀 Recommended Build Order

### Phase 0: Manual Entry System
1. ✅ Create admin panel (simple form)
2. ✅ Build manual metrics endpoint
3. ✅ Add authentication (basic)
4. ✅ Test data entry workflow

### Phase 1: Core App (Manual Data)
1. ✅ Build database schema
2. ✅ Create 10 One Piece boxes manually
3. ✅ Enter sample data (7-14 days)
4. ✅ Build API endpoints (read from manual data)
5. ✅ Build frontend app
6. ✅ Test everything works!

### Phase 2: API Integration (Later)
1. ⏳ Get marketplace API access
2. ⏳ Build ingestion jobs
3. ⏳ Populate raw data tables
4. ⏳ Run calculation pipeline
5. ⏳ Compare manual vs API data
6. ⏳ Switch to API as primary source

---

## 📋 Manual Entry Checklist

**Daily Metrics to Enter:**
- [ ] Date
- [ ] Box selection
- [ ] Floor price (USD)
- [ ] Active listings count
- [ ] Boxes sold today
- [ ] Boxes added today
- [ ] Daily volume (USD)
- [ ] Visible market cap (USD)

**Optional Metrics:**
- [ ] Lowest 3 prices (for floor calculation)
- [ ] Highest listing price
- [ ] Average listing price
- [ ] Notes/comments

**Derived Metrics (Auto-Calculated):**
- ✅ 7-day EMA of volume
- ✅ 30-day SMA of volume
- ✅ Days to +20% increase
- ✅ Rank change direction
- ✅ Floor price 1-day change %

---

## 🎯 Next Steps

1. **Decide on Admin Panel Approach**
   - Web form? (Recommended)
   - CSV import?
   - API endpoint only?

2. **Build Manual Entry System**
   - Simple admin panel
   - Data entry endpoint
   - Validation logic

3. **Start Entering Data**
   - Create 10 boxes
   - Enter 7-14 days of data
   - Test all features

4. **Build Frontend App**
   - Use manual data
   - Everything works!
   - Iterate on UI/UX

5. **Add API Integration Later**
   - When ready
   - Seamless transition
   - No frontend changes needed

---

**This approach lets you build and validate the entire app before investing in API integration!** 🎉


