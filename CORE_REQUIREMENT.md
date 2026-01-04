# Core System Requirement

## PRIMARY OBJECTIVE: FULL AUTOMATION + EXTENSIBILITY

**The entire screenshot data entry system must be:**
1. **FULLY AUTOMATED** with ZERO manual intervention
2. **EXTENSIBLE** to easily add new metrics in the future

---

## Core Principle

**User sends screenshot → System automatically processes everything → All data appears in all applicable fields**

**Future metrics → Easy to add without major refactoring → System adapts automatically**

See `ARCHITECTURE_EXTENSIBILITY.md` for extensibility design requirements.

---

## Automation Requirements

### 1. Complete Automation Flow

```
User Action: Send screenshot with "This is data for [BOX NAME]"
    ↓
System Automatically:
    1. Extracts all data from screenshot
    2. Applies all filters (JP, 25% below floor, eBay title matching)
    3. Detects and removes duplicates
    4. Processes individual listings and sales
    5. Calculates ALL metrics (no manual calculation)
    6. Saves to database (all fields)
    7. Updates leaderboard (all fields)
    8. Updates box detail pages (all fields)
    9. Recalculates rankings (all time periods)
    ↓
Result: All data automatically visible in UI
```

### 2. Zero Manual Steps

**NO manual data entry required for:**
- Floor price
- Listings count
- Sales data
- Volume calculations
- Any derived metrics
- Rankings
- Any field displayed in the UI

**NO manual calculations required:**
- All metrics calculate automatically
- All formulas run automatically
- All aggregations happen automatically

**NO manual database updates:**
- All fields save automatically
- All records update automatically
- All timestamps set automatically

### 3. Accuracy Requirements

The system must be:
- **Accurate**: All calculations follow specifications exactly
- **Reliable**: Handles edge cases correctly
- **Consistent**: Same input produces same output
- **Complete**: All applicable fields are populated
- **Validated**: Data integrity checks prevent errors

### 4. Complete Field Population

**Every field that is displayed or used must be automatically populated:**

#### Database Fields (box_metrics_unified table):
- `floor_price_usd` - Auto-populated from screenshot
- `floor_price_1d_change_pct` - Auto-calculated
- `floor_price_30d_change_pct` - Auto-calculated
- `unified_volume_usd` - Auto-calculated from sales
- `unified_volume_7d_ema` - Auto-calculated
- `unified_volume_30d_sma` - Auto-calculated
- `volume_mom_change_pct` - Auto-calculated
- `active_listings_count` - Auto-populated from screenshot
- `boxes_sold_per_day` - Auto-calculated from sales
- `boxes_sold_30d_avg` - Auto-calculated
- `boxes_added_today` - Auto-detected from listings
- `avg_boxes_added_per_day` - Auto-calculated
- `days_to_20pct_increase` - Auto-calculated (T₊ / net_burn_rate)
- `expected_days_to_sell` - Auto-calculated
- `liquidity_score` - Auto-calculated
- `visible_market_cap_usd` - Auto-calculated
- `listed_percentage` - Auto-calculated
- All other derived metrics - Auto-calculated

#### Leaderboard Display Fields:
- All metrics automatically available
- Rankings automatically calculated
- All sortable fields automatically populated

#### Box Detail Page Fields:
- All metrics automatically available
- Charts automatically include new data
- Time series automatically updated
- All calculations automatically performed

### 5. Data Processing Automation

**Extraction (Automatic):**
- Extract individual listings (price, quantity, seller, title, platform)
- Extract individual sales (price, quantity, date, seller, title, platform)
- Extract floor price (TCGPlayer)
- Extract all visible data from screenshot

**Filtering (Automatic):**
- Apply eBay title matching (automatic check)
- Apply JP filter (automatic exclusion)
- Apply 25% below floor filter (automatic exclusion)
- All filtering happens automatically

**Duplicate Detection (Automatic):**
- Compare listings: seller + price + quantity + platform
- Compare sales: seller + price + quantity + date + platform
- Skip duplicates automatically
- Detect updates automatically (price changes)

**Calculations (Automatic):**
- All volume metrics (daily, 7d EMA, 30d SMA, MoM)
- All price metrics (current, 1d change, 30d change)
- All supply metrics (listings, added, averages)
- All demand metrics (sold, averages)
- All derived metrics (liquidity, market cap, days to 20%, etc.)
- All rankings (daily, weekly, monthly)

**Storage (Automatic):**
- Save all data to database automatically
- Update existing records automatically
- Create new records automatically
- Maintain data integrity automatically

### 6. Error Handling

The system must handle errors automatically:
- Invalid data → Skip and log (don't break)
- Missing fields → Use defaults or skip (don't break)
- Calculation errors → Return None/null (don't break)
- Database errors → Log and continue (don't break)

**The system must NEVER require manual intervention to fix errors.**

### 7. Integration Automation

**Database Integration:**
- All fields automatically mapped
- All calculations automatically saved
- All updates automatically applied

**API Integration:**
- All endpoints automatically return updated data
- All queries automatically include new metrics
- All responses automatically formatted

**Frontend Integration:**
- All fields automatically display
- All charts automatically update
- All rankings automatically refresh
- All metrics automatically visible

---

## Success Criteria

The system is successful when:

1. ✅ User sends screenshot
2. ✅ System processes everything automatically
3. ✅ All data appears in database automatically
4. ✅ All fields populate automatically
5. ✅ All calculations run automatically
6. ✅ All metrics update automatically
7. ✅ Leaderboard updates automatically
8. ✅ Box detail pages update automatically
9. ✅ Rankings recalculate automatically
10. ✅ User sees all data immediately (no manual steps)

**If ANY step requires manual intervention, the system has FAILED.**

---

## Implementation Priority

**MUST HAVE (Critical):**
- Full automation (no manual steps)
- Accurate calculations (follow specifications exactly)
- Complete field population (all applicable fields)
- Reliable operation (handles errors gracefully)

**SHOULD HAVE:**
- Fast processing
- Clear error messages (if errors occur)
- Data validation
- Logging for debugging

**NICE TO HAVE:**
- Progress indicators
- Batch processing
- Advanced features

---

## Testing Requirements

Every feature must be tested for:
1. **Automation**: Does it run without manual steps?
2. **Accuracy**: Are calculations correct?
3. **Completeness**: Are all fields populated?
4. **Reliability**: Does it handle edge cases?
5. **Integration**: Does data flow to all systems?

---

## 8. Extensibility and Adaptability

**The system must be designed to easily add new metrics in the future.**

### Architecture Requirements for Extensibility

**Modular Design:**
- Calculations should be modular (one calculation = one function/method)
- New calculations can be added without modifying existing code
- Calculation registry/pluggable system for easy additions

**Database Extensibility:**
- Database schema can be extended with new fields
- Migration system supports adding new metric columns
- Fields can be nullable to support gradual rollout

**API Extensibility:**
- API responses include all available metrics (existing + new)
- New metrics automatically included in responses
- Backward compatible (new fields don't break existing clients)

**Frontend Extensibility:**
- Frontend can display new metrics when available
- New metrics automatically appear (optional display)
- UI can be extended to show new metrics

**Configuration-Driven:**
- Metric definitions can be configured (not hardcoded)
- Calculation formulas can be updated/extended
- Filtering rules can be extended

### Adding New Metrics (Future Process)

When a new metric needs to be added:

1. **Define the metric** in calculation specification
2. **Add database field** (migration)
3. **Implement calculation function** (modular)
4. **Register calculation** (plug into system)
5. **Update API responses** (automatic inclusion)
6. **Update frontend display** (optional, when needed)

**The system architecture should make steps 1-4 straightforward and not require major refactoring.**

### Design Principles for Extensibility

- **Separation of Concerns**: Extraction, filtering, calculation, storage are separate
- **Open/Closed Principle**: Open for extension, closed for modification
- **Interface-Based**: Calculations follow consistent interfaces
- **Data-Driven**: Metrics defined by data structure, not hardcoded logic
- **Plugin Architecture**: New calculations can be "plugged in"

---

## Bottom Line

**This system exists to automate data entry completely. If it requires any manual work, it has failed its primary purpose.**

The system must:
- Work automatically
- Be accurate
- Populate all fields
- Require zero manual intervention
- **Be extensible and adaptable for future metrics**

Anything less is a failure.

