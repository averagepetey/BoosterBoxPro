# Data Storage Architecture Explanation

## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed


## Overview
The system uses a **three-layer unified timeline architecture**:
1. **Layer 1**: Historical baseline (JSON, static past) - seeds early timeline
2. **Layer 2**: Daily observations (Database + JSON with `source="screenshot"`) - authoritative present
3. **Layer 3**: Derived metrics (computed from unified timeline) - never stored, always calculated

**Core Principle**: "We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."

**See `THREE_LAYER_DATA_MODEL.md` for detailed explanation of the unified timeline architecture.**

---

## 📊 Storage Locations

### 1. **PostgreSQL Database** (Primary Storage)
**Location**: PostgreSQL database via SQLAlchemy ORM

#### Tables:

**A. `booster_boxes` Table**
- **Purpose**: Master product catalog - stores basic box information
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `product_name` - Full name (e.g., "One Piece - OP-11 A Fist of Divine Speed Booster Box")
  - `set_name` - Set name
  - `game_type` - Usually "One Piece"
  - `release_date`, `image_url`, `estimated_total_supply`, `reprint_risk`
- **File**: `app/models/booster_box.py`
- **Data Entry**: Pre-populated, rarely changes

**B. `box_metrics_unified` Table** ⭐ **PRIMARY METRICS TABLE**
- **Purpose**: Stores daily metrics for each box
- **Key Fields**:
  - `booster_box_id` (UUID) - Foreign key to `booster_boxes`
  - `metric_date` (DATE) - One row per box per day
  - `floor_price_usd` - Lowest listing price
  - `unified_volume_7d_ema` - **PRIMARY RANKING METRIC**
  - `unified_volume_usd` - 30-day volume estimate
  - `boxes_sold_per_day` - Actual sales for THIS specific day
  - `boxes_sold_30d_avg` - 30-day average sales
  - `active_listings_count` - Listings within 20% of floor
  - `boxes_added_today` - New listings added
  - `days_to_20pct_increase`, `liquidity_score`, etc.
- **File**: `app/models/unified_box_metrics.py`
- **Unique Constraint**: One row per `(booster_box_id, metric_date)`
- **Data Entry**: Updated daily via screenshot processing

---

### 2. **JSON Files** (Historical Backup/Fallback)
**Location**: `data/` directory

#### A. `historical_entries.json`
- **Purpose**: Historical raw data (listings, sales) + metadata
- **Structure**:
  ```json
  {
    "box-uuid-here": [
      {
        "date": "2026-01-03",
        "source": "screenshot",
        "data_type": "combined",
        "floor_price_usd": 300.00,
        "active_listings_count": 20,
        "boxes_sold_today": 5,
        "daily_volume_usd": 1500.00,
        "raw_listings": [...],  // Full listing details
        "raw_sales": [...]      // Full sales details
      }
    ]
  }
  ```
- **Used For**:
  - Duplicate detection (checking if data already exists)
  - Historical calculations (30-day averages, price history)
  - Fallback when database query fails
- **File**: `scripts/historical_data_manager.py` manages this
- **Data Entry**: Written during screenshot processing

#### B. `leaderboard.json` (Legacy/Optional)
- **Purpose**: Static fallback data for leaderboard display
- **Status**: Legacy file, mostly replaced by database queries
- **Usage**: Only used if box has no database metrics

---

## 🔄 Data Flow: From Input to Storage

### **Step 1: Data Entry**
**Entry Point**: `scripts/enter_box_data.py`

```python
# User edits this script with:
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]  # List of listing dicts
SALES = [...]     # List of sales dicts
```

**Then runs**: `python scripts/enter_box_data.py`

---

### **Step 2: Processing Pipeline**
**File**: `scripts/automated_screenshot_processor.py`

The `process_screenshot_data()` function runs through these steps:

1. **Formatting** (`data_extraction_formatter.py`)
   - Validates data structure
   - Normalizes formats

2. **Box Lookup**
   - Queries `booster_boxes` table to find box by name
   - Gets box UUID

3. **Duplicate Detection** (`duplicate_detection_service.py`)
   - Checks `historical_entries.json` for existing listings/sales
   - Removes duplicates based on seller, price, date

4. **Filtering** (`data_filtering_service.py`)
   - Removes JP items, cases, double packs
   - Filters listings >25% below floor
   - Matches eBay titles to box name

5. **Data Aggregation**
   - Counts `boxes_sold_today` from sales
   - Calculates `daily_volume_usd` (sum of sale prices × quantities)
   - Counts `active_listings_count` (listings within 20% of floor)
   - Determines `floor_price` (lowest listing)

6. **Metric Calculation** (`metrics_calculator.py`)
   - **Queries database** for all existing metrics for this box
   - **Queries JSON** for historical entries
   - **Merges both sources** to get complete historical picture
   - Calculates:
     - `boxes_sold_30d_avg` - Average across all dates (including zeros)
     - `unified_volume_7d_ema` - 7-day exponential moving average
     - `unified_volume_30d_sma` - 30-day simple moving average
     - `days_to_20pct_increase`, `liquidity_score`, etc.

7. **Save to Database** (`_save_to_database()`)
   - **Checks if row exists** for `(box_id, date)`
   - **If exists**: Updates existing row
   - **If new**: Creates new row in `box_metrics_unified`
   - Stores **calculated metrics** (not raw data)

8. **Save to JSON** (`_save_to_historical_data()`)
   - Appends entry to `historical_entries.json`
   - Stores **raw data** (listings, sales) + metadata
   - Used for future duplicate detection and historical calculations

---

### **Step 3: Data Retrieval (API Endpoints)**

#### **Leaderboard Endpoint**: `/booster-boxes`
**File**: `main.py` (lines 127-311)

**Process**:
1. Queries all boxes from `booster_boxes` table
2. For each box:
   - Gets **latest metrics** from `box_metrics_unified` (ORDER BY metric_date DESC LIMIT 1)
   - Falls back to `leaderboard.json` if no database metrics
3. Enhances with historical data:
   - Calls `get_box_price_history()` - reads from `historical_entries.json`
   - Calls `get_box_30d_avg_sales()` - calculates from JSON (tries DB, falls back to JSON)
   - Uses historical data to override/improve database values
4. Sorts by requested metric (default: `unified_volume_usd`)
5. Returns paginated results

#### **Box Detail Endpoint**: `/booster-boxes/{box_id}`
- Gets latest metrics from database
- Gets full price history from `historical_entries.json`
- Combines both for comprehensive view

---

## 🔑 Key Concepts

### **Dual Storage Strategy**
- **Database**: Fast queries, structured data, latest metrics
- **JSON**: Raw historical data, duplicate detection, fallback

### **Data Synchronization**
- When you process data, it saves to **BOTH** database and JSON
- Database stores **calculated metrics** (aggregated, ready to use)
- JSON stores **raw data** (listings/sales details, for future calculations)

### **Historical Calculations**
Functions like `get_box_30d_avg_sales()` and `get_box_price_history()`:
1. **Try database first** (most accurate, up-to-date)
2. **Fall back to JSON** (if database query fails or no data)
3. **Merge both sources** when calculating averages across all dates

### **Box Identification**
- Boxes identified by **UUID** in database
- UUID mapping exists for boxes with old/new UUIDs:
  - `DB_TO_LEADERBOARD_UUID_MAP` - Maps database UUIDs to old JSON UUIDs
  - Used to merge historical data from different sources

---

## 📝 Data Entry Workflow

**Current Method**: Edit `scripts/enter_box_data.py`

```python
BOX_NAME = "op-11"
ENTRY_DATE = "2026-01-04"
FLOOR_PRICE = 300.00
LISTINGS = [...]
SALES = [...]
```

**What Happens**:
1. Script calls `process_screenshot_data()`
2. Data goes through full pipeline
3. Saves to database (updates/creates row in `box_metrics_unified`)
4. Saves to JSON (appends to `historical_entries.json`)
5. Frontend updates automatically (queries database + JSON)

---

## 🎯 Where Data Lives

| Data Type | Storage Location | Accessed By |
|-----------|-----------------|-------------|
| **Box master data** | `booster_boxes` table | Database queries |
| **Daily metrics** | `box_metrics_unified` table | Database queries, API endpoints |
| **Raw historical data** | `data/historical_entries.json` | Historical services, duplicate detection |
| **Calculated averages** | Calculated on-the-fly | `get_box_30d_avg_sales()`, `get_box_price_history()` |
| **Legacy/fallback** | `data/leaderboard.json` | Only if no database metrics exist |

---

## ⚠️ Important Notes

1. **Database is Source of Truth** for current metrics
2. **JSON is Backup** for raw data and historical calculations
3. **Average Calculations** merge both sources to ensure accuracy
4. **One Row Per Day** in database - processing same date twice **updates** existing row
5. **Raw Data Preserved** in JSON for future recalculations if needed

