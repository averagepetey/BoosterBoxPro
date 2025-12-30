# Phase 3: Unified Metrics Calculation - Status Report

**Date:** Phase 3 Analysis  
**Status:** 🟡 **MOSTLY COMPLETE - Enhancements Needed**

---

## ✅ Already Completed

### 1. Metrics Calculation Services ✅
- ✅ `app/services/ema_calculator.py` - EMA/SMA calculations
- ✅ `app/services/metrics_calculator.py` - All unified metrics calculations
- ✅ All calculation methods implemented:
  - Volume EMA (7-day)
  - Volume SMA (30-day)
  - Absorption rate
  - Liquidity score
  - Expected days to sell
  - Visible market cap
  - 30-day boxes sold average

### 2. Integration ✅
- ✅ Metrics calculation automatically triggers after manual entry
- ✅ Integrated in `POST /api/v1/admin/manual-metrics` endpoint
- ✅ Integrated in bulk metrics endpoint
- ✅ Updates `box_metrics_unified` table automatically

### 3. Database & Models ✅
- ✅ `box_metrics_unified` table exists
- ✅ All required fields present
- ✅ SQLAlchemy model created
- ✅ Repository with upsert logic

---

## 🔨 What's Missing / Needs Enhancement

### 1. Metrics Recalculation Script ⏭️
**Status:** Not created yet

**Purpose:** Backfill/update historical metrics when:
- Adding new calculation logic
- Fixing bugs
- Recalculating with more historical data

**Need:** `scripts/recalculate_metrics.py`

---

### 2. Calculate Metrics from Raw Sales Data ⏭️
**Status:** Partially done - sales are saved but not aggregated into unified metrics

**Current State:**
- ✅ Sales can be extracted from screenshots → `ebay_sales_raw` table
- ❌ No service to aggregate sales data into daily volume metrics
- ❌ No endpoint to trigger metrics calculation from raw sales

**Need:**
- Service method to aggregate `ebay_sales_raw` by date
- Calculate daily volume, units sold from sales
- Populate `box_metrics_unified` from aggregated sales

---

### 3. Calculate Metrics from Raw Listing Data ⏭️
**Status:** Partially done - listings are saved but not aggregated

**Current State:**
- ✅ Listings can be extracted from screenshots → `tcg_listings_raw` table
- ❌ No service to aggregate listing data into floor price, active listings
- ❌ No endpoint to calculate unified metrics from raw listings

**Need:**
- Service method to aggregate `tcg_listings_raw` by date
- Calculate floor price (min price), active listings count
- Populate `box_metrics_unified` from aggregated listings

---

### 4. Days to 20% Increase Calculation ⏭️
**Status:** Not implemented

**Need:** Calculate how many days until listings would need 20% price increase based on supply/demand

---

### 5. Price Change Calculation ⏭️
**Status:** Not implemented

**Need:** Calculate `floor_price_1d_change_pct` (percentage change from previous day)

---

## 🎯 Phase 3 Enhancement Plan

### Priority 1: Recalculation Script
- Create script to recalculate all metrics for historical data
- Useful for backfilling after code changes

### Priority 2: Aggregate from Raw Data
- Service to calculate unified metrics from `tcg_listings_raw`
- Service to calculate unified metrics from `ebay_sales_raw`
- Endpoint to trigger aggregation

### Priority 3: Missing Calculations
- Days to 20% increase
- Price change percentage
- Other derived metrics

---

## 📊 Test Status

- ✅ Metrics calculation works with manual entry
- ✅ EMA calculations tested
- ⏭️ Need to test with raw sales/listing data
- ⏭️ Need to verify all edge cases

---

**Next Steps:** Build the missing pieces to complete Phase 3!

