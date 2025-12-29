# BoosterBoxPro - Sealed TCG Market Intelligence

Mobile-first application (with website support) tracking sealed TCG booster box markets using public marketplace listing data.

**Platform Strategy:** 
- Primary focus: Mobile app (iOS/Android)
- Secondary: Responsive website (reuses same API)
- Both platforms consume identical REST API endpoints

## 📋 Planning Documents

All planning documents are organized in the **[Planning Documents](./Planning%20Documents/)** directory.

### Quick Navigation

**🔴 Critical (Read First):**
1. **[MANUAL_FIRST_APPROACH.md](./Planning%20Documents/MANUAL_FIRST_APPROACH.md)** - 🎯 RECOMMENDED START HERE ⭐
   - Build with manual data entry first
   - Seamless transition to APIs later
   - Perfect for MVP development
   - Admin panel for easy data entry

2. **[REMAINING_UNKNOWNS.md](./Planning%20Documents/REMAINING_UNKNOWNS.md)** - ⚠️ DECISIONS NEEDED ⚠️
   - Critical unknowns blocking Phase 1
   - Pre-Phase 1 checklist
   - Questions to answer

3. **[BUILD_PHASES.md](./Planning%20Documents/BUILD_PHASES.md)** - ⭐ LOCKED BUILD ORDER ⭐
   - Sequential build phases (0-8)
   - Phase dependencies and exit criteria
   - MVP definition

4. **[IMPLEMENTATION_DECISIONS.md](./Planning%20Documents/IMPLEMENTATION_DECISIONS.md)** - ⭐ AUTHORITATIVE DECISIONS ⭐
   - All locked-in engineering decisions
   - Engineering rules and constraints
   - Scope control

**📐 Architecture & Design:**
4. **[ARCHITECTURE_PLAN.md](./Planning%20Documents/ARCHITECTURE_PLAN.md)** - Complete system architecture
5. **[MARKETPLACE_STRATEGY.md](./Planning%20Documents/MARKETPLACE_STRATEGY.md)** - Dual marketplace architecture
6. **[TECH_STACK.md](./Planning%20Documents/TECH_STACK.md)** - Technology stack decisions
7. **[DATA_FLOW.md](./Planning%20Documents/DATA_FLOW.md)** - Visual flow diagrams

**🎨 UI & Features:**
8. **[UI_REQUIREMENTS.md](./Planning%20Documents/UI_REQUIREMENTS.md)** - UI specifications
9. **[FAVORITES_FEATURE.md](./Planning%20Documents/FAVORITES_FEATURE.md)** - User favorites feature

**🔧 Data Collection:**
10. **[API_SERVICE_ANALYSIS.md](./Planning%20Documents/API_SERVICE_ANALYSIS.md)** - TCGAPIs analysis
11. **[TCGGO_API_ANALYSIS.md](./Planning%20Documents/TCGGO_API_ANALYSIS.md)** - TCGGO API analysis
12. **[SCRAPING_AGENT_DESIGN.md](./Planning%20Documents/SCRAPING_AGENT_DESIGN.md)** - Scraping agent architecture
13. **[DETECTION_RISKS.md](./Planning%20Documents/DETECTION_RISKS.md)** - Bot detection methods
14. **[TCGPLAYER_DETECTION_ASSESSMENT.md](./Planning%20Documents/TCGPLAYER_DETECTION_ASSESSMENT.md)** - Detection likelihood

**📚 Reference:**
15. **[QUICK_REFERENCE.md](./Planning%20Documents/QUICK_REFERENCE.md)** - Formulas and logic lookup
16. **[CHALLENGES.md](./Planning%20Documents/CHALLENGES.md)** - Challenge analysis
17. **[PLANNING_SUMMARY.md](./Planning%20Documents/PLANNING_SUMMARY.md)** - Planning status summary

## 🎯 Core Concept

Each booster box is modeled as an independent market. The app surfaces:
- **Liquidity** (visible market cap - TCGplayer)
- **Supply pressure** (boxes added per day - TCGplayer)
- **Demand velocity** (boxes sold per day - unified)
- **Time-to-price-pressure** (estimated days until 20% floor increase)

**Primary Signal:** Unified volume (7-day EMA) - weighted combination of TCGplayer (70%) + eBay (30%), used for ranking and discovery.

**Marketplace Strategy:**
- **TCGplayer (Primary):** Authoritative for floor price, supply, active listings
- **eBay (Secondary):** Demand signals only (sold listings), not used for pricing
- **Unified Metrics:** Combined at metric layer only, never mix raw listings
- See [MARKETPLACE_STRATEGY.md](./Planning%20Documents/MARKETPLACE_STRATEGY.md) for details

**User Features:**
- **Favorites / My List** - Users can favorite boxes to track in personal list
- **Authentication** - Required for favorites feature (email/password)
- **Personalized View** - See favorite status on leaderboard, dedicated "My List" view

## 🚦 Key Decisions Needed

Before implementation, confirm:

1. **Marketplace APIs**
   - [ ] Which marketplace(s) to integrate first? (TCGplayer, eBay, etc.)
   - [ ] Do you have API credentials/rate limits?
   - [ ] Webhooks available or polling only?

2. **Floor Price Calculation**
   - [ ] 5th percentile (recommended)
   - [ ] Average of bottom 3 listings
   - [ ] Absolute minimum

3. **Relist Window**
   - [ ] 24 hours (recommended)
   - [ ] Different threshold?

4. **Data Retention**
   - [ ] How long to keep raw `listing_snapshots`?
   - [ ] Partition after X days?

5. **Reprint Risk Management**
   - [ ] Manual admin panel
   - [ ] Community voting
   - [ ] External data source

6. **Multi-Marketplace Strategy**
   - [ ] Aggregate listings from multiple sources?
   - [ ] How to handle duplicate listings?

## 📊 Core Metrics

1. **Visible Market Cap** = Σ(listings.price × listings.quantity)
2. **Daily Volume USD** = Σ(sales.units × sales.price) [PRIMARY SIGNAL]
3. **Boxes Sold Per Day** = total_units_sold / day
4. **Supply Inflow** = new_units_listed / day
5. **Days to +20% Increase** = (active_listings × 0.85) / boxes_sold_per_day
6. **Reprint Risk** = LOW | MEDIUM | HIGH (qualitative overlay)

## 🔄 Daily Workflow

```
02:00 UTC - Ingestion Job
  ├─ Fetch current listings from marketplace APIs
  ├─ Compare with previous day's snapshot
  ├─ Detect changes (sales, new listings, etc.)
  ├─ Store new snapshot
  └─ Trigger calculation pipeline

02:30 UTC (after ingestion) - Calculation Pipeline
  ├─ Calculate market cap, volume, demand velocity
  ├─ Calculate EMAs/SMAs for trending metrics
  ├─ Calculate supply inflow
  ├─ Calculate days to 20% increase
  └─ Store all metrics

API responses computed on-the-fly using pre-calculated metrics
```

## 📱 API Endpoints

### Public Endpoints
- `GET /api/v1/booster-boxes?sort=volume&limit=10` - Top boxes by volume (default)
- `GET /api/v1/booster-boxes?sort=market_cap&limit=10` - Top boxes by market cap
- `GET /api/v1/booster-boxes/{id}` - Single box details
- `GET /api/v1/booster-boxes/{id}/time-series?metric=volume&days=30` - Historical data

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (get JWT token)
- `GET /api/v1/users/me` - Get current user info

### Favorites (Authenticated)
- `GET /api/v1/users/me/favorites` - Get my list of favorited boxes
- `POST /api/v1/users/me/favorites/{booster_box_id}` - Add favorite
- `DELETE /api/v1/users/me/favorites/{booster_box_id}` - Remove favorite
- `GET /api/v1/users/me/favorites/{booster_box_id}` - Check favorite status

## 🗄️ Database Schema Overview

- **booster_boxes** - Product master data
- **listing_snapshots** - Daily snapshots of all listings
- **listing_changes** - Audit log of listing state transitions
- **daily_derived_metrics** - Pre-computed metrics per box per day

See [ARCHITECTURE_PLAN.md](./Planning%20Documents/ARCHITECTURE_PLAN.md) for full schema details.

## 🛠️ Tech Stack

See **[TECH_STACK.md](./Planning%20Documents/TECH_STACK.md)** for complete technology stack decisions.

### Backend (Locked)
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, auto docs, type hints)
- **Database:** PostgreSQL 15+ (managed: Supabase/Neon)
- **Cache:** Redis 7+ (managed: Redis Cloud/Upstash)
- **Task Queue:** Celery + Redis
- **ORM:** SQLAlchemy 2.0 (async)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Data Processing:** pandas, numpy, pendulum

### Frontend (Recommended)
- **Mobile App:** React Native + TypeScript (recommended for MVP)
- **Website:** Next.js 14+ (React) + TypeScript
- **State Management:** React Query / TanStack Query
- **Styling:** Tailwind CSS (web)

### Infrastructure (Recommended for MVP)
- **Backend Hosting:** Railway or Render
- **Database:** Supabase or Neon (managed Postgres)
- **Redis:** Redis Cloud or Upstash
- **CI/CD:** GitHub Actions
- **Containerization:** Docker + Docker Compose

## ✅ Next Steps

### 🎯 Recommended: Manual-First Approach

1. ✅ Review **[MANUAL_FIRST_APPROACH.md](./Planning%20Documents/MANUAL_FIRST_APPROACH.md)** - Build with manual data entry first!
2. ✅ Review all planning documents
3. **Phase 0: Manual Entry System**
   - Build admin panel for data entry
   - Create manual metrics endpoint
   - Enter sample data (7-14 days)
4. **Phase 1: Core App (Manual Data)**
   - Set up backend project structure
   - Implement database migrations
   - Create 10 One Piece boxes manually
   - Build API endpoints (reads from manual data)
   - Build frontend app (mobile + web)
   - Test everything works!
5. **Phase 2: API Integration (Later)**
   - Get marketplace API access (when ready)
   - Build ingestion pipeline
   - Build calculation pipeline
   - Transition from manual to API (seamless!)

### Alternative: API-First Approach

1. ⚠️ **CRITICAL: Get Marketplace API Access** (see CHALLENGES.md)
2. Make decisions on open questions (see Key Decisions section)
3. **Phase 0: Validation** (Recommended before coding)
   - Test marketplace API with sample data
   - Validate data quality and edge cases
   - Create test datasets
4. **Phase 1 (Backend - Mobile-First):**
   - Set up backend project structure
   - Implement database migrations
   - Build ingestion pipeline
   - Build calculation pipeline
   - Create API endpoints (mobile-optimized)
5. **Phase 2 (Mobile App):**
   - Choose mobile framework (React Native/Flutter/Native)
   - Build mobile app consuming API
6. **Phase 3 (Website):**
   - Build responsive website using same API
   - Add web-specific features if needed (larger tables, more data)
7. Testing and deployment

---

## ⚠️ Biggest Challenges

See **[CHALLENGES.md](./Planning%20Documents/CHALLENGES.md)** for detailed analysis of:
1. **Marketplace API Integration** - Foundation, needs API access first
2. **Volume Calculation Accuracy** - Many edge cases to handle correctly
3. **Database Performance** - Need to scale efficiently
4. **Sparkline Data** - Decide on data frequency
5. **Image Sources** - Where do box images come from?

**Recommendation:** Use manual-first approach to start building immediately. Get API access later when ready to automate.

---

**Status:** Planning Phase ✅ - Ready to Start Building!

**Recommended Path:** Use manual-first approach (see MANUAL_FIRST_APPROACH.md) to build immediately without waiting for API access.

