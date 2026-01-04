# Data Extraction Requirements from Screenshots

## Overview

Screenshots will contain detailed information about listings and sales. This document specifies exactly what data is available and how it should be extracted and processed.

---

## Screenshot Data Available

### Listings Screenshots
Screenshots will show **individual listings** with:
- ✅ Price (listing price)
- ✅ Shipping cost
- ✅ Quantity available
- ✅ Seller identifier/username
- ✅ Listing title/description
- ✅ Platform (eBay or TCGPlayer)
- ✅ Listing ID or date (for duplicate detection)

### Sales Screenshots
Screenshots will show **individual sales** with:
- ✅ Sale price
- ✅ Shipping cost (if applicable)
- ✅ Quantity sold
- ✅ Sale date
- ✅ Seller identifier/username
- ✅ Sale title/description
- ✅ Platform (eBay or TCGPlayer)
- ✅ Sale ID or timestamp (for duplicate detection)

---

## Critical Extraction Rules

### 1. eBay Title Matching (CRITICAL)

**For eBay listings and sales:**
- **Only count items where the title/description matches the booster box name**
- Use best judgment to identify legitimate matches
- Filter out listings/sales that don't clearly refer to the specific booster box

**Examples:**
- Box: "OP-01" 
  - ✅ Count: "One Piece OP-01 Booster Box"
  - ✅ Count: "OP-01 Romance Dawn Booster Box"
  - ❌ Skip: "OP-02 Booster Box" (different box)
  - ❌ Skip: "OP-01 Cards" (not a box)
  - ❌ Skip: "One Piece Cards" (not specific)

- Box: "EB-01"
  - ✅ Count: "EB-01 Booster Box"
  - ✅ Count: "Egghead Booster Box EB-01"
  - ❌ Skip: "EB-02 Booster Box" (different box)

**Judgment Criteria:**
- Title must reference the exact set code (OP-01, EB-01, etc.)
- Title should indicate it's a booster box (not individual cards)
- If ambiguous, err on the side of exclusion (better to miss one than include wrong data)

### 2. Filtering Rules

#### Always Exclude:
- Items with "JP" in title or description (Japanese versions)
- Items priced 25% or more below current floor price (suspiciously low)

#### eBay-Specific:
- Items where title doesn't match booster box name (see above)

### 3. Duplicate Detection (CRITICAL)

#### For Listings:
Compare: `seller + price + quantity + platform + listing_id`

- If exact match exists in previous data → **SKIP (duplicate)**
- If seller + quantity + platform match but price changed → **UPDATE (not new listing)**
- If seller + quantity + platform are new → **NEW LISTING**

#### For Sales:
Compare: `seller + price + quantity + date + platform + sale_id`

- If exact match exists → **SKIP (duplicate)**
- Sales are typically unique, but check to prevent double-counting

---

## Data Extraction Process

### Step 1: Extract Individual Items
From each screenshot, extract:
1. All individual listings (with all fields listed above)
2. All individual sales (with all fields listed above)

### Step 2: Apply Filters
For each item (listing or sale):

1. **eBay Title Check** (eBay only):
   - Does title match booster box name?
   - Use best judgment for legitimate matches
   - If NO → Skip item

2. **JP Filter**:
   - Does title/description contain "JP"?
   - If YES → Skip item

3. **Price Filter**:
   - Is price 25% or more below current floor price?
   - If YES → Skip item

4. **Passes all filters** → Continue to next step

### Step 3: Duplicate Detection
For each filtered item:

1. **Check against previous data**:
   - Listings: Compare seller + price + quantity + platform + listing_id
   - Sales: Compare seller + price + quantity + date + platform + sale_id

2. **Decision**:
   - Exact match → Skip (duplicate)
   - No match → Process item
   - Listing with seller+quantity+platform match but price change → Update (not new)

### Step 4: Aggregate Data
After filtering and duplicate detection:

1. **Listings**:
   - Count total listings → `active_listings_count`
   - Calculate price ladder (prices + quantities) → For T₊ calculation
   - Count new listings → `boxes_added_today`

2. **Sales**:
   - Sum prices × quantities for current day → `daily_volume_usd`
   - Sum quantities for current day → `boxes_sold_today`
   - Aggregate by date for historical calculations

---

## Example Extraction Flow

### Input: Screenshot with 10 listings, 5 sales

1. **Extract all items** (10 listings, 5 sales)

2. **Apply filters**:
   - Listing 1: eBay, title "OP-01 Booster Box" → ✅ Pass
   - Listing 2: eBay, title "OP-02 Booster Box" → ❌ Skip (wrong box)
   - Listing 3: TCGPlayer, contains "JP" → ❌ Skip (JP filter)
   - Listing 4: Price $50, floor $100 → ❌ Skip (25% below)
   - Listing 5-10: Pass filters → ✅ Continue
   - Sales 1-5: All pass filters → ✅ Continue

3. **Duplicate detection**:
   - Check against previous data
   - Listing 5: Matches previous listing → ❌ Skip (duplicate)
   - Listing 6-10: New → ✅ Process
   - Sales 1-5: All new → ✅ Process

4. **Result**:
   - 5 listings processed (after filters and duplicates)
   - 5 sales processed
   - `active_listings_count` = 5
   - `boxes_added_today` = 5 (all new)
   - `daily_volume_usd` = sum of 5 sales
   - `boxes_sold_today` = sum of quantities from 5 sales

---

## Best Practices

1. **Conservative Filtering**: When in doubt, exclude rather than include
2. **Strict Duplicate Detection**: Better to skip a duplicate than double-count
3. **eBay Title Matching**: Use context clues (set codes, "booster box" terminology)
4. **Document Decisions**: Log any ambiguous cases for review
5. **Validate Totals**: Compare aggregated counts to verify extraction accuracy

---

## Error Handling

If data is unclear or ambiguous:
- **eBay Title Match**: If uncertain, exclude (conservative approach)
- **Price Filter**: Use current floor price, if unavailable use last known floor price
- **Duplicate Detection**: If seller/ID unavailable, use price + quantity + date as fallback
- **Missing Fields**: Skip item if critical fields (price, quantity) are missing

