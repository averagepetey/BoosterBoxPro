# Build Plan: Fully Automated Screenshot Data Entry System

## Overview

This plan outlines the implementation of the fully automated screenshot data entry system that processes screenshots, extracts data, calculates all metrics, and automatically populates all fields in the database, leaderboard, and box detail pages.

---

## Build Phases

### Phase 1: Database Schema Updates
**Goal**: Add missing fields to support all calculations

**Tasks**:
1. Create migration to add missing fields:
   - `unified_volume_30d_sma` (Numeric(12, 2), nullable)
   - `volume_mom_change_pct` (Numeric(6, 2), nullable)
   - `avg_boxes_added_per_day` (Numeric(8, 2), nullable)
2. Update `UnifiedBoxMetrics` model to include new fields
3. Run migration

**Files to Modify**:
- `migrations/versions/002_add_missing_metrics.py` (NEW)
- `app/models/unified_box_metrics.py`

---

### Phase 2: Enhanced Filtering System
**Goal**: Implement all filtering rules (JP, 25% below floor, eBay title matching)

**Tasks**:
1. Create filtering module with:
   - JP filter (exclude "JP" in title/description)
   - Low price filter (exclude 25%+ below floor)
   - eBay title matching (only count matching titles)
2. Create title matching utility for eBay listings/sales
3. Test filtering logic

**Files to Create**:
- `app/services/data_filtering.py` (NEW)

**Files to Modify**:
- Update data extraction to use filters

---

### Phase 3: Duplicate Detection System
**Goal**: Prevent duplicate data entry

**Tasks**:
1. Create duplicate detection module:
   - Listing duplicates (seller + price + quantity + platform)
   - Sales duplicates (seller + price + quantity + date + platform)
   - Price change detection (UPDATE vs NEW)
2. Integrate with historical data manager
3. Test duplicate detection

**Files to Create**:
- `app/services/duplicate_detection.py` (NEW) or enhance existing

**Files to Modify**:
- `scripts/historical_data_manager.py`
- `scripts/chat_data_entry.py`

---

### Phase 4: Enhanced Metrics Calculator
**Goal**: Implement all calculations per specification

**Tasks**:
1. Add missing volume metrics:
   - 30-day volume SMA
   - Month-over-month volume change
2. Enhance Days to 20% calculation (T₊ / net_burn_rate):
   - Price ladder data handling
   - T₊ calculation (sum quantities below +20% tier)
   - Net burn rate calculation
3. Add avg_boxes_added_per_day calculation (30d average, capped)
4. Add all recommended metrics (if implementing)
5. Ensure all calculations follow specification exactly

**Files to Modify**:
- `scripts/metrics_calculator.py` (major enhancement)
- Possibly create separate calculation modules:
  - `scripts/calculations/volume_metrics.py` (NEW)
  - `scripts/calculations/price_metrics.py` (NEW)
  - `scripts/calculations/supply_metrics.py` (NEW)

---

### Phase 5: Data Extraction and Formatting
**Goal**: Process AI-extracted data into system format

**Tasks**:
1. Create data extraction formatter:
   - Converts AI-extracted data to structured format
   - Handles individual listings (price, quantity, seller, title, platform)
   - Handles individual sales (price, quantity, date, seller, title, platform)
   - Validates required fields
2. Create price ladder builder (for T₊ calculation)
3. Create data aggregation functions

**Files to Create**:
- `scripts/data_extraction_formatter.py` (NEW)

---

### Phase 6: Automated Processing Pipeline
**Goal**: Complete end-to-end automation

**Tasks**:
1. Create main processing script that:
   - Takes AI-extracted data
   - Applies filters
   - Detects duplicates
   - Calculates all metrics
   - Saves to database
   - Updates leaderboard JSON (if still used)
2. Integrate with existing `chat_data_entry.py`
3. Ensure all calculations run automatically
4. Ensure all fields populate automatically

**Files to Create**:
- `scripts/automated_screenshot_processor.py` (NEW) or enhance existing

**Files to Modify**:
- `scripts/chat_data_entry.py`
- `scripts/manual_data_entry.py` (if needed)

---

### Phase 7: Historical Data Manager Enhancements
**Goal**: Support price ladder data and enhanced duplicate detection

**Tasks**:
1. Enhance historical data storage to support:
   - Price ladder data (temporary, for T₊ calculation)
   - Individual listing/sale tracking (for duplicate detection)
2. Update merge logic
3. Support T₊ calculation data requirements

**Files to Modify**:
- `scripts/historical_data_manager.py`

---

### Phase 8: Testing and Validation
**Goal**: Ensure system works correctly

**Tasks**:
1. Create test data
2. Test complete flow:
   - Data extraction
   - Filtering
   - Duplicate detection
   - Calculations
   - Database storage
   - API responses
3. Validate all metrics calculate correctly
4. Validate all fields populate correctly
5. Test edge cases

**Files to Create**:
- `scripts/test_automated_system.py` (NEW)

---

### Phase 9: Documentation
**Goal**: Document usage

**Tasks**:
1. Create usage guide
2. Update README
3. Document workflow
4. Create examples

**Files to Create**:
- `scripts/README_AUTOMATED_SCREENSHOT_PROCESSING.md` (NEW)

---

## Implementation Order (Recommended)

1. **Phase 1** (Database) - Foundation
2. **Phase 2** (Filtering) - Data quality
3. **Phase 3** (Duplicates) - Data integrity
4. **Phase 4** (Calculations) - Core functionality
5. **Phase 5** (Extraction) - Data processing
6. **Phase 6** (Pipeline) - Integration
7. **Phase 7** (Historical) - Data management
8. **Phase 8** (Testing) - Validation
9. **Phase 9** (Documentation) - Usage

---

## Key Design Decisions

### 1. Data Flow
```
AI Extraction (Chat) → Formatter → Filters → Duplicate Check → 
Calculations → Database → API → Frontend
```

### 2. Modular Calculations
- Each metric calculation is a separate function
- Calculations can be registered/plugged in
- Easy to add new metrics later

### 3. Filtering First
- Apply filters before processing
- Prevents bad data from entering system
- Ensures data quality

### 4. Duplicate Detection
- Check against historical data
- Skip exact duplicates
- Handle updates (price changes)

### 5. Automatic Calculations
- All metrics calculate automatically
- No manual intervention
- Calculations run in pipeline

---

## Critical Requirements to Verify

- ✅ All volume metrics calculate automatically
- ✅ Days to 20% uses T₊ calculation correctly
- ✅ eBay title matching works correctly
- ✅ Duplicate detection prevents duplicates
- ✅ All filters apply correctly
- ✅ All fields populate automatically
- ✅ Database updates automatically
- ✅ API includes all fields
- ✅ Frontend displays all fields

---

## Success Criteria

The system is successful when:
1. User sends screenshot → AI extracts data
2. Data formats correctly
3. Filters apply automatically
4. Duplicates detected and skipped
5. All metrics calculate automatically
6. Database updates automatically
7. Leaderboard shows updated data
8. Box detail pages show updated data
9. Rankings update automatically
10. Zero manual intervention required

---

## Next Steps

Start with Phase 1 (Database Schema Updates) and proceed through phases sequentially.

