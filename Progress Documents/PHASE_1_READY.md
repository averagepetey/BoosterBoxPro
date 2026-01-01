# Phase 1 — Core Data Foundation — READY TO START

**Status:** Phase 0 Complete ✅ → Ready for Phase 1 Implementation

**Date:** 2024-12-29

---

## 🎯 Phase 1 Goal

Create permanent identity system for booster boxes and establish the database foundation.

**Key Deliverables:**
- PostgreSQL database with complete schema
- 10 One Piece booster boxes registered
- Manual metrics entry system working
- Sample data populated (7-14 days)

---

## 📋 Phase 1 Implementation Steps

### Step 1: Project Setup & Dependencies
**Estimated Time:** 30-45 minutes

- [ ] Create Python virtual environment
- [ ] Install core dependencies:
  - FastAPI
  - SQLAlchemy 2.0 (async)
  - Alembic (migrations)
  - Pydantic (validation)
  - PostgreSQL driver (asyncpg)
  - python-dotenv (environment variables)
- [ ] Create `requirements.txt` or `pyproject.toml`
- [ ] Set up project structure:
  ```
  app/
  ├── __init__.py
  ├── main.py              # FastAPI app
  ├── config.py            # Configuration
  ├── database.py          # DB connection
  ├── models/              # SQLAlchemy models
  ├── schemas/             # Pydantic schemas
  ├── routers/             # API routes
  ├── repositories/        # Data access layer
  └── services/            # Business logic
  migrations/              # Alembic migrations
  scripts/                  # Utility scripts
  ```

---

### Step 2: Database Setup
**Estimated Time:** 30-45 minutes

- [ ] Install PostgreSQL 15+ (local or cloud)
  - Option A: Local installation
  - Option B: Cloud service (Supabase, Neon, AWS RDS, etc.)
- [ ] Create database: `boosterboxpro`
- [ ] Set up connection configuration
- [ ] Create `.env` file with database credentials:
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@localhost/boosterboxpro
  ```
- [ ] Test database connection

---

### Step 3: Database Schema (Alembic Migrations)
**Estimated Time:** 1-2 hours

- [ ] Initialize Alembic: `alembic init migrations`
- [ ] Configure Alembic for async SQLAlchemy
- [ ] Create migration for `booster_boxes` table:
  - UUID primary key
  - product_name, set_name, game_type
  - image_url, release_date
  - estimated_total_supply, reprint_risk
  - created_at, updated_at timestamps
- [ ] Create migrations for placeholder tables:
  - `tcg_listings_raw` (empty, for future API integration)
  - `tcg_box_metrics_daily` (empty)
  - `ebay_sales_raw` (empty)
  - `ebay_box_metrics_daily` (empty)
  - `box_metrics_unified` (will store manual metrics)
- [ ] Add proper foreign keys and indexes
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify tables created successfully

---

### Step 4: SQLAlchemy Models
**Estimated Time:** 1 hour

- [ ] Create `models/__init__.py` with Base class
- [ ] Create `models/booster_box.py`:
  - BoosterBox model with all fields
  - Type hints
  - Relationships (for future metrics)
  - `__repr__` method
- [ ] Create `models/unified_box_metrics.py`:
  - UnifiedBoxMetrics model
  - Foreign key to booster_boxes
  - All metric fields from schema
- [ ] Test models can be imported and used

---

### Step 5: FastAPI Application Setup
**Estimated Time:** 45 minutes

- [ ] Create `app/main.py`:
  - FastAPI app instance
  - CORS middleware
  - Database connection lifecycle
  - Error handlers
- [ ] Create `app/database.py`:
  - Async database session
  - Connection pool configuration
- [ ] Create `app/config.py`:
  - Settings from environment variables
  - Database URL, etc.
- [ ] Test FastAPI app starts: `uvicorn app.main:app --reload`

---

### Step 6: Admin Endpoints (Box Registry)
**Estimated Time:** 1-2 hours

- [ ] Create `schemas/booster_box.py`:
  - Pydantic models for request/response
  - BoxCreate, BoxResponse schemas
- [ ] Create `routers/admin.py`:
  - `POST /api/v1/admin/boxes` - Create new box
  - Basic authentication (API key for now)
- [ ] Create `repositories/booster_box_repository.py`:
  - Methods: create_box(), get_box_by_id(), list_boxes()
- [ ] Test endpoint with Postman/curl

---

### Step 7: Register 10 One Piece Boxes
**Estimated Time:** 30 minutes

- [ ] Research One Piece booster boxes (OP-01 through OP-10)
- [ ] Collect data for each box:
  - Product name
  - Set name
  - Release date
  - Image URL (or placeholder)
- [ ] Use admin endpoint to register all 10 boxes
- [ ] Verify all boxes in database with unique UUIDs

**Boxes to Register:**
1. OP-01 Romance Dawn Booster Box
2. OP-02 Paramount War Booster Box
3. OP-03 Pillars of Strength Booster Box
4. OP-04 Kingdoms of Intrigue Booster Box
5. OP-05 Awakening of the New Era Booster Box
6. OP-06 Wings of the Captain Booster Box
7. OP-07 Absolute Justice Booster Box
8. OP-08 Advent of the Emperor Booster Box
9. OP-09 Age of Pirates Booster Box
10. OP-10 Dawn of the New Era Booster Box

---

### Step 8: Manual Metrics Entry Endpoint
**Estimated Time:** 1-2 hours

- [ ] Create `schemas/metrics.py`:
  - ManualMetricsInput schema
  - MetricsResponse schema
- [ ] Create `POST /api/v1/admin/manual-metrics` endpoint:
  - Accept: booster_box_id, metric_date, floor_price_usd, active_listings_count, etc.
  - Validate box exists
  - Insert/update in `box_metrics_unified` table
  - Support bulk entry (array of metrics)
- [ ] Create `repositories/unified_metrics_repository.py`:
  - Methods: save_metrics(), get_metrics_for_date()
- [ ] Test endpoint with sample data

---

### Step 9: Enter Sample Data
**Estimated Time:** 1 hour

- [ ] Enter 7-14 days of sample metrics for all 10 boxes
- [ ] Use realistic values (can reference mock_data for structure)
- [ ] Vary values day-to-day to simulate market fluctuations
- [ ] Verify data appears correctly in database

---

### Step 10: Verification & Testing
**Estimated Time:** 30 minutes

- [ ] Query `booster_boxes` table: Should have 10 rows
- [ ] Query `box_metrics_unified` table: Should have 70-140 rows
- [ ] Test foreign key constraints
- [ ] Test UUID uniqueness
- [ ] Verify all endpoints work correctly

---

## 🛠️ Prerequisites Before Starting

### Required Software
- [ ] Python 3.11+ installed
- [ ] PostgreSQL 15+ installed (or cloud database access)
- [ ] Git (for version control)
- [ ] Code editor/IDE (VS Code, PyCharm, etc.)

### Decisions Needed
- [ ] **Database Location:** Local PostgreSQL or cloud service?
- [ ] **Box Entry Method:** API endpoint (recommended) or CSV import?
- [ ] **Image URLs:** Use placeholder images or find actual box images?

---

## 📦 Initial Dependencies to Install

```bash
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy[asyncio]>=2.0.0
alembic>=1.12.0
asyncpg>=0.29.0  # PostgreSQL async driver
pydantic>=2.0.0
python-dotenv>=1.0.0

# Optional but recommended
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0  # For testing API endpoints
```

---

## ✅ Phase 1 Exit Criteria

Before moving to Phase 2, verify:

- [ ] Database schema migrations run successfully
- [ ] 10 boxes registered in `booster_boxes` table
- [ ] Manual metrics entry endpoint working (`POST /api/v1/admin/manual-metrics`)
- [ ] Sample data entered (7-14 days of metrics for all boxes)
- [ ] All snapshot/metrics tables exist (empty but ready)
- [ ] Can query boxes and metrics from database
- [ ] FastAPI app runs without errors
- [ ] Admin endpoints return correct responses

---

## 🚀 Quick Start Command Sequence

Once prerequisites are met, you can start with:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install fastapi uvicorn sqlalchemy[asyncio] alembic asyncpg pydantic python-dotenv

# 3. Initialize Alembic
alembic init migrations

# 4. Set up database connection
# (Configure DATABASE_URL in .env file)

# 5. Create first migration
alembic revision --autogenerate -m "Initial schema"

# 6. Run migrations
alembic upgrade head

# 7. Start FastAPI app
uvicorn app.main:app --reload
```

---

## 📝 Notes

- **Manual-First Approach:** We're building with manual data entry, so no API credentials needed yet
- **Database Schema:** Matches ARCHITECTURE_PLAN.md exactly
- **Mock Data:** Can reference `mock_data/` files for data structure examples
- **Type Safety:** Use Pydantic models matching OpenAPI spec from Phase 0

---

**Ready to begin Phase 1 when you are!** 🚀

