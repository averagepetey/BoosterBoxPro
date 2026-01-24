# Pre-Launch Checklist - Complete Requirements

> **Goal:** Launch-ready by end of week  
> **Status:** ~60% Complete  
> **Last Updated:** January 23, 2026

This document consolidates ALL requirements from GTM assessment, BUILD_PHASES, and planning documents.

---

## 🔴 CRITICAL BLOCKERS (Must Complete Before Launch)

### 1. Authentication & User System (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot monetize, cannot protect content  
**Source:** GTM_READINESS_ASSESSMENT.md, BUILD_PHASES.md Phase 8

#### Database Schema
- [ ] Create `users` table migration (Alembic)
  - `id` (UUID, primary key)
  - `email` (VARCHAR, unique, not null)
  - `hashed_password` (VARCHAR, not null)
  - `created_at` (TIMESTAMP)
  - `trial_started_at` (TIMESTAMP, nullable)
  - `trial_ended_at` (TIMESTAMP, nullable)
  - `subscription_status` (ENUM: 'trial', 'active', 'expired', 'cancelled')
  - `stripe_customer_id` (VARCHAR, nullable, unique)
  - `stripe_subscription_id` (VARCHAR, nullable)
  - `is_admin` (BOOLEAN, default false)
  - `is_active` (BOOLEAN, default true)
  - `token_version` (INTEGER, default 1) - for token revocation
  - Indexes: `email`, `stripe_customer_id`
- [ ] Run migration: `alembic upgrade head`

#### User Model & Utilities
- [ ] Create `app/models/user.py` (SQLAlchemy model)
- [ ] Create `app/utils/password.py` (password hashing with bcrypt)
  - `hash_password(password: str) -> str`
  - `verify_password(plain_password: str, hashed_password: str) -> bool`
- [ ] Create `app/utils/jwt.py` (JWT token management)
  - `create_access_token(data: dict, expires_delta: timedelta) -> str`
  - `decode_access_token(token: str) -> dict`
- [ ] Create `app/repositories/user_repository.py`
  - `create_user(email: str, password: str) -> User`
  - `get_user_by_email(email: str) -> Optional[User]`
  - `get_user_by_id(user_id: UUID) -> Optional[User]`
  - `update_user(user: User) -> User`

#### Authentication Endpoints
- [ ] `POST /api/v1/auth/register`
  - Validate email format and password strength
  - Check if email exists (return 409 if exists)
  - Hash password
  - Create user with `trial_started_at = now()`, `trial_ended_at = now() + 7 days`
  - Set `subscription_status = 'trial'`
  - Return 201 with user data (no password)
- [ ] `POST /api/v1/auth/login`
  - Get user by email (return 401 if not found)
  - Verify password (return 401 if incorrect)
  - Create JWT access token (include user_id in payload)
  - Return 200 with token: `{"access_token": "...", "token_type": "bearer"}`

#### Authentication Dependencies
- [ ] Update `app/dependencies/auth.py`
  - `get_current_user(token: str = Depends(oauth2_scheme)) -> User`
  - Extract token from Authorization header (Bearer token)
  - Decode JWT token (return 401 if invalid)
  - Get user by ID from token payload
  - Validate token version (revocation check)
  - Return user (return 401 if user not found)

#### Protect API Endpoints
- [ ] Add `user: User = Depends(get_current_user)` to all endpoints:
  - `GET /booster-boxes` (leaderboard)
  - `GET /booster-boxes/{box_id}` (box detail)
  - `GET /booster-boxes/{box_id}/time-series`
- [ ] Test endpoints with and without token (should return 401 without token)

**Estimated Time:** 1-2 days  
**Dependencies:** None

---

### 2. Stripe Payment Integration (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot monetize  
**Source:** GTM_READINESS_ASSESSMENT.md, BUILD_PHASES.md Phase 8

#### Stripe Setup
- [ ] Sign up for Stripe account (stripe.com)
- [ ] Obtain API keys:
  - Publishable key (public)
  - Secret key (private)
  - Webhook secret (for webhook handler)
- [ ] Store keys in environment variables:
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
- [ ] Install Stripe Python SDK: `pip install stripe`
- [ ] Test connection: `stripe.Customer.list(limit=1)`

#### Stripe Service
- [ ] Create `app/services/stripe_service.py`
  - `create_customer(email: str) -> stripe.Customer`
  - `create_subscription(customer_id: str, price_id: str) -> stripe.Subscription`
  - `cancel_subscription(subscription_id: str) -> stripe.Subscription`
  - `get_subscription(subscription_id: str) -> stripe.Subscription`
  - Handle Stripe API errors gracefully

#### Subscription Service
- [ ] Create `app/services/subscription_service.py`
  - `check_trial_status(user: User) -> bool`
  - `has_active_access(user: User) -> bool` (trial OR subscription active)

#### Payment Endpoints
- [ ] `POST /api/v1/payments/create-intent`
  - Requires authentication
  - Get or create Stripe customer for user
  - Create Stripe PaymentIntent for subscription
  - Return `client_secret` for frontend Stripe.js integration
- [ ] `POST /api/v1/webhooks/stripe`
  - Verify webhook signature (Stripe webhook secret)
  - Handle events:
    - `customer.subscription.created` - Update user `subscription_status` to 'active'
    - `customer.subscription.updated` - Update subscription status
    - `customer.subscription.deleted` - Update `subscription_status` to 'cancelled'
    - `invoice.payment_succeeded` - Ensure subscription is active
    - `invoice.payment_failed` - Handle payment failure
  - Update user record in database based on webhook events

#### Paywall Middleware
- [ ] Create `app/dependencies/paywall.py`
  - `require_active_subscription(user: User = Depends(get_current_user)) -> User`
  - Check if user has active access (trial or subscription)
  - If no active access, raise HTTPException 403 Forbidden
  - Return user if access granted
- [ ] Add this dependency to all API endpoints (except auth endpoints)

#### Subscription Management Endpoints
- [ ] `GET /api/v1/users/me/subscription`
  - Returns current subscription status, trial info
- [ ] `POST /api/v1/users/me/subscription/cancel`
  - Cancels Stripe subscription
  - Updates user `subscription_status` to 'cancelled'
- [ ] `GET /api/v1/users/me`
  - Returns current user info (email, subscription status)

#### User Model Methods
- [ ] Add methods to User model:
  - `has_active_access() -> bool`
  - `days_remaining_in_trial() -> int`
  - `is_subscription_active() -> bool`

#### Testing
- [ ] Test customer creation
- [ ] Test subscription creation
- [ ] Test webhook handling (use Stripe CLI: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe`)
- [ ] Test payment flow end-to-end
- [ ] Test trial expiration blocks API access

**Estimated Time:** 1-2 days  
**Dependencies:** Stripe account setup

---

### 3. Production Deployment (0% Complete)
**Status:** ❌ NOT DEPLOYED  
**Impact:** Cannot launch publicly  
**Source:** GTM_READINESS_ASSESSMENT.md

#### Hosting Provider Selection
- [ ] Choose backend hosting (Railway, Render, or AWS)
- [ ] Choose frontend hosting (Vercel recommended for Next.js)
- [ ] Choose database hosting (Supabase, Neon, or Railway's Postgres)
- [ ] Set up accounts (can use free tiers initially)

#### Backend Deployment
- [ ] Deploy backend API to production
- [ ] Configure production environment variables:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `ADMIN_API_KEY`
  - `APIFY_API_TOKEN`
  - `ENVIRONMENT=production`
- [ ] Set up SSL/HTTPS (usually auto-provided)
- [ ] Test backend API endpoints in production

#### Frontend Deployment
- [ ] Deploy frontend to production (Vercel)
- [ ] Configure production environment variables:
  - `NEXT_PUBLIC_API_URL` (backend API URL)
  - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
- [ ] Test frontend in production
- [ ] Verify API calls work from production frontend

#### Database Setup
- [ ] Set up production database
- [ ] Run migrations in production: `alembic upgrade head`
- [ ] Seed initial data (18 booster boxes)
- [ ] Test database connection

#### Domain & SSL
- [ ] Configure domain name (optional: can use provider subdomain initially)
- [ ] Set up SSL certificate (usually auto-provided)
- [ ] Test HTTPS access

#### Monitoring & Logging
- [ ] Set up basic error logging
- [ ] Set up uptime monitoring (optional but recommended)
- [ ] Configure error alerts (optional)

**Estimated Time:** 1-2 days  
**Dependencies:** Hosting account setup

---

### 4. Data Validation & Accuracy (30% Complete)
**Status:** ⚠️ PARTIALLY WORKING  
**Impact:** Data quality issues could hurt credibility  
**Source:** GTM_READINESS_ASSESSMENT.md

#### Floor Price Validation
- [ ] Run listings scraper for all 18 boxes
- [ ] Verify floor prices are accurate (compare with manual inspection)
- [ ] Fix any boxes with incorrect floor prices
- [ ] Verify shipping costs are included in floor price

#### Listings Count Validation
- [ ] Verify listings count accuracy for all boxes
- [ ] Ensure day-over-day tracking is working for all boxes
- [ ] Test edge cases:
  - Boxes with no listings
  - Boxes with very low volume
  - Boxes with very high volume

#### Sales Data Validation
- [ ] Verify Apify sales data is accurate
- [ ] Ensure all 18 boxes have recent data (last 7 days)
- [ ] Check for missing metrics (volume, sales, etc.)
- [ ] Backfill any missing historical data

#### Data Completeness
- [ ] Verify all 18 boxes have:
  - Floor prices (with shipping)
  - Listings counts (within -15% to +20% range)
  - Sales data (from Apify)
  - Volume metrics
  - All calculated metrics (7-day volume, 30-day volume, etc.)

**Estimated Time:** 1 day  
**Dependencies:** Listings scraper, Apify integration

---

## 🟡 IMPORTANT (Should Complete Before Launch)

### 5. Chrome Extension Fix & Implementation (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Missing feature for TCGplayer integration  
**Source:** CHROME_EXTENSION_PLAN.md, chrome-extension/ directory

#### Extension Structure
- [ ] Review and finalize `manifest.json` (Manifest V3)
  - Permissions: `activeTab`, `storage`, `tabs`
  - Host permissions: `https://www.tcgplayer.com/*`
  - Background service worker configuration
  - Content scripts configuration
  - Popup action configuration

#### Background Service Worker
- [ ] Create `background.js` (service worker)
  - Handle extension installation/update
  - Manage API communication with backend
  - Store authentication tokens securely
  - Handle message passing between content scripts and popup

#### Content Script (TCGplayer Integration)
- [ ] Create `content/tcgplayer.js`
  - Detect TCGplayer product pages
  - Extract product information (name, set, price)
  - Match product to BoosterBoxPro database
  - Inject overlay/panel with box metrics
  - Display real-time data from API
  - Handle page navigation and dynamic content

#### Popup Interface
- [ ] Create `popup/popup.html`
  - User authentication/login
  - Display subscription status
  - Settings/preferences
  - Quick stats overview
- [ ] Create `popup/popup.js`
  - Handle authentication flow
  - Fetch and display user data
  - Manage API calls to backend
  - Store user preferences
- [ ] Create `popup/popup.css`
  - Match BoosterBoxPro design system
  - Responsive layout
  - Dark mode support

#### Content Panel/Overlay
- [ ] Create `content/panel.css`
  - Styled overlay matching app design
  - Non-intrusive positioning
  - Responsive to page layout
- [ ] Implement panel injection logic
  - Show/hide toggle
  - Position relative to product info
  - Display key metrics (floor price, volume, rank)

#### API Integration
- [ ] Connect to backend API endpoints
  - Authentication endpoint
  - Box detail endpoint (`/booster-boxes/{box_id}`)
  - Leaderboard endpoint (for rank lookup)
- [ ] Handle API authentication
  - Store JWT token securely
  - Refresh token logic
  - Handle expired tokens
- [ ] Error handling
  - Network errors
  - API errors
  - User-friendly error messages

#### Product Matching
- [ ] Implement product matching logic
  - Match TCGplayer product name to database
  - Handle variations in naming
  - Fallback strategies for unmatched products
- [ ] Cache product mappings
  - Store matches locally
  - Reduce API calls
  - Update cache periodically

#### Testing
- [ ] Test on all TCGplayer product pages
- [ ] Test authentication flow
- [ ] Test data display accuracy
- [ ] Test error scenarios
- [ ] Test performance (no page slowdown)
- [ ] Test browser compatibility (Chrome, Edge)

#### Chrome Web Store Preparation
- [ ] Create extension icons (all sizes: 16, 48, 128)
- [ ] Write extension description
- [ ] Create screenshots for store listing
- [ ] Prepare privacy policy
- [ ] Set up Chrome Web Store developer account
- [ ] Package extension for submission

**Estimated Time:** 2-3 days  
**Dependencies:** Backend API must be deployed and authenticated

---

### 6. Manual Tasks & UI Cleanup
**Status:** ⚠️ PARTIALLY COMPLETE  
**Impact:** User experience and data accuracy

#### Reprint Risk Management
- [ ] Create admin interface for reprint risk updates
  - Admin endpoint: `POST /admin/boxes/{box_id}/reprint-risk`
  - Update `reprint_risk` field (LOW, MEDIUM, HIGH)
  - Validation: only allow valid enum values
  - Log all changes with admin user ID
- [ ] Review all 18 boxes and set accurate reprint risk
  - Research historical reprint patterns
  - Set based on known reprint cadence
  - Document reasoning for each box
- [ ] Add reprint risk display to frontend
  - Show on leaderboard (if space allows)
  - Show prominently on box detail page
  - Use color coding (green/yellow/red)
- [ ] Create reprint risk update workflow
  - Document process for future updates
  - Set up alerts for boxes needing review

#### UI Cleanup - Remove Redundant Metrics
- [ ] Audit all displayed metrics on leaderboard
  - Identify duplicates (e.g., `unified_volume_usd` vs `volume_7d` vs `unified_volume_7d_ema`)
  - Identify confusing metrics (similar names, different calculations)
  - Document which metrics to keep vs remove
- [ ] Clean up leaderboard table
  - Remove redundant columns
  - Consolidate similar metrics
  - Keep only most useful metrics:
    - Rank
    - Product name
    - Floor price (with 1d change)
    - Volume (7d EMA - primary ranking metric)
    - Active listings count
    - Sales per day (or 30d avg)
  - Remove or hide:
    - `unified_volume_usd` (if `unified_volume_7d_ema` is shown)
    - `volume_7d` (if `unified_volume_7d_ema` is shown)
    - Duplicate volume metrics
- [ ] Clean up box detail page
  - Organize metrics into logical sections
  - Remove redundant metrics
  - Group related metrics together:
    - **Price Metrics**: Floor price, 1d change, 30d change
    - **Volume Metrics**: Daily volume, 7d volume, 30d volume (keep only most relevant)
    - **Sales Metrics**: Boxes sold per day, 30d average
    - **Market Metrics**: Active listings, listings added today
    - **Projections**: Days to +20%, liquidity score
  - Remove duplicates:
    - If showing `unified_volume_7d_ema`, don't also show `volume_7d` and `unified_volume_usd`
    - If showing `boxes_sold_30d_avg`, don't also show `boxes_sold_per_day` (or make it clear which is which)
- [ ] Update API responses
  - Remove redundant fields from responses
  - Document which metrics are primary vs secondary
  - Ensure frontend uses correct metrics
- [ ] Update frontend components
  - Remove unused metric displays
  - Update tooltips/help text to explain remaining metrics
  - Ensure consistent metric naming

#### Manual Data Entry Completion
- [ ] Complete any missing box data
  - Verify all 18 boxes have complete information
  - Fill in missing `set_name`, `release_date` if needed
  - Ensure all boxes have images (or placeholders)
- [ ] Review and clean up static data files
  - `data/leaderboard.json` - ensure it's not being used (should use database)
  - `mock_data/` - remove or document as test data only
  - Ensure all data comes from database/API, not static files
- [ ] Verify data consistency
  - All boxes have consistent field names
  - All dates are in correct format
  - All prices are in USD
  - All counts are integers

**Estimated Time:** 1-2 days  
**Dependencies:** None

---

### 7. Frontend-Backend Integration Testing
**Status:** ⚠️ PARTIALLY WORKING  
**Source:** GTM_READINESS_ASSESSMENT.md

- [ ] Verify discovered floor price (with shipping) displays correctly
- [ ] Ensure listings count shows in box detail
- [ ] Test all API endpoints return correct data
- [ ] Verify sorting/filtering works
- [ ] Test mobile responsiveness
- [ ] Check for API errors/edge cases
- [ ] End-to-end testing of all pages
- [ ] Verify data flow: scraper → API → frontend

**Estimated Time:** 0.5 days

---

### 8. Daily Automation Reliability
**Status:** ⚠️ SCRIPTS EXIST, NEED VERIFICATION  
**Source:** GTM_READINESS_ASSESSMENT.md, AUTOMATION_REQUIREMENTS.md

#### Cron Job Setup
- [ ] Verify cron jobs are scheduled correctly
- [ ] Test error handling (what happens if Apify fails?)
- [ ] Test error handling (what happens if scraper fails?)
- [ ] Set up alerts/notifications for failures
- [ ] Verify scripts run at correct times (12 PM ± 45 min)
- [ ] Test recovery from failures

#### Scripts to Verify
- [ ] `scripts/daily_refresh.sh` (Apify refresh)
- [ ] `scripts/listings_scraper.py` (listings scraper)
- [ ] Verify both scripts can run in production environment

**Estimated Time:** 0.5 days

---

### 9. User Experience Polish
**Status:** ⚠️ BASIC UI EXISTS  
**Source:** GTM_READINESS_ASSESSMENT.md

- [ ] Mobile responsiveness testing
- [ ] Loading states (spinners, skeletons)
- [ ] Error messages (user-friendly)
- [ ] Empty states (no data messages)
- [ ] Performance optimization (slow queries?)
- [ ] Accessibility (keyboard navigation, screen readers)

**Estimated Time:** 1 day

---

### 10. Security Hardening
**Status:** ⚠️ PARTIAL  
**Source:** BUILD_PHASES.md Phase 8, SECURITY_AUDIT_PLAN.md

- [ ] Ensure passwords are never returned in API responses
- [ ] Use HTTPS in production (TLS/SSL)
- [ ] Store JWT secret securely (environment variable, never in code)
- [ ] Store Stripe keys securely (environment variables)
- [ ] Add CORS restrictions (only allow frontend domain)
- [ ] Add rate limiting to auth endpoints (prevent brute force)
- [ ] Add rate limiting to API endpoints (prevent abuse)
- [ ] Configure limits: e.g., 5 requests/minute for login, 100 requests/minute for API

**Estimated Time:** 0.5 days

---

## 🟢 NICE-TO-HAVE (Can Add Post-Launch)

### 11. Documentation
- [ ] User-facing documentation
- [ ] FAQ page
- [ ] How-to guides
- [ ] Feature explanations
- [ ] Pricing information
- [ ] Terms of Service
- [ ] Privacy Policy

### 12. Advanced Features
- [ ] Favorites/My List feature
- [ ] Email notifications
- [ ] Price alerts
- [ ] Export data (CSV)
- [ ] Social sharing

---

## 📋 5-Day Action Plan

### Day 1 (Today): Authentication
- [ ] Create users table migration
- [ ] Create User model and utilities (password, JWT)
- [ ] Create user repository
- [ ] Implement registration endpoint
- [ ] Implement login endpoint
- [ ] Create authentication dependency
- [ ] Protect API endpoints with authentication
- [ ] Test authentication flow

### Day 2: Payments
- [ ] Set up Stripe account
- [ ] Create Stripe service
- [ ] Create subscription service
- [ ] Implement payment intent endpoint
- [ ] Implement Stripe webhook handler
- [ ] Create paywall middleware
- [ ] Add subscription management endpoints
- [ ] Test payment flow end-to-end

### Day 3: Data Validation & Manual Tasks
- [ ] Run listings scraper for all 18 boxes
- [ ] Verify floor prices are accurate
- [ ] Fix any data accuracy issues
- [ ] Test all API endpoints
- [ ] Verify frontend displays correct data
- [ ] **Manual Tasks:**
  - [ ] Create admin interface for reprint risk updates
  - [ ] Review and set reprint risk for all 18 boxes
  - [ ] Audit and remove redundant metrics from UI
  - [ ] Clean up leaderboard table (remove duplicates)
  - [ ] Clean up box detail page (organize metrics)
  - [ ] Complete any missing box data

### Day 4: Production Deployment
- [ ] Choose hosting providers
- [ ] Set up hosting accounts
- [ ] Deploy backend API to production
- [ ] Deploy frontend to production
- [ ] Configure production database
- [ ] Set up environment variables
- [ ] Test production environment

### Day 5: Chrome Extension & Final Polish
- [ ] **Chrome Extension:**
  - [ ] Build background service worker
  - [ ] Build content script for TCGplayer
  - [ ] Build popup interface
  - [ ] Implement API integration
  - [ ] Test extension functionality
  - [ ] Package for Chrome Web Store
- [ ] Final testing
- [ ] Bug fixes
- [ ] Mobile testing
- [ ] Security hardening
- [ ] Launch preparation

---

## ✅ Launch Readiness Checklist

### Must Have (Launch Blockers)
- [ ] Authentication working (register, login, JWT)
- [ ] Stripe payments working (subscription, trial)
- [ ] Paywall protecting content
- [ ] All 18 boxes have accurate data
- [ ] Floor prices are correct (with shipping)
- [ ] API endpoints working correctly
- [ ] Frontend displays correct data
- [ ] Production deployment live
- [ ] Daily automation running
- [ ] Error handling in place
- [ ] **Manual Tasks Complete:**
  - [ ] Reprint risk set for all boxes
  - [ ] Redundant metrics removed from UI
  - [ ] UI cleaned up and organized

### Should Have (Launch Quality)
- [ ] Mobile responsive
- [ ] Loading states
- [ ] Error messages
- [ ] Basic documentation
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] Chrome extension functional (if launching with extension)

### Nice to Have (Post-Launch)
- [ ] Favorites feature
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Mobile app

---

## 🚨 Risk Assessment

### High Risk Items
1. **Authentication/Payments** - Not implemented, critical blocker
2. **Data Accuracy** - Floor prices may be wrong for some boxes
3. **Production Deployment** - Not set up, unknown issues
4. **Automation Reliability** - May fail silently

### Medium Risk Items
1. **Frontend-Backend Integration** - May have display bugs
2. **Mobile Experience** - Not fully tested
3. **Error Handling** - May not handle all edge cases

### Low Risk Items
1. **Documentation** - Can add post-launch
2. **Advanced Features** - Can add post-launch

---

## 📊 Current Completion Status

**Overall GTM Readiness: ~60%**

- ✅ Backend API: 90% complete (local development)
- ✅ Data Collection: 85% complete (local scripts)
- ✅ Frontend: 70% complete (local development)
- ❌ Authentication: 0% complete (BLOCKER)
- ❌ Payments: 0% complete (BLOCKER)
- ❌ Production Deployment: 0% complete (not deployed yet)
- ❌ Chrome Extension: 0% complete (files exist but empty)
- ⚠️ Manual Tasks: 30% complete (reprint risk needs work, UI needs cleanup)
- ⚠️ Testing: 30% complete (local only)

---

## ❓ Questions to Answer

1. **Hosting:** Which providers? (Railway, Render, Vercel?)
2. **Database:** Supabase, Neon, or self-hosted?
3. **Domain:** What domain name?
4. **Pricing:** What subscription price?
5. **Trial:** 7 days? Or different?
6. **Payment:** Monthly? Annual? Both?

---

## 🚀 Next Steps

1. **Start with Authentication** (Day 1)
2. **Then Payments** (Day 2)
3. **Then Data Validation & Manual Tasks** (Day 3)
4. **Then Deployment** (Day 4)
5. **Then Chrome Extension & Final Polish** (Day 5)

**Ready to start?** Let's begin with authentication implementation.

---

## 📝 Notes

### Chrome Extension Priority
- Chrome extension can be launched post-MVP if needed
- However, it's a key differentiator and should be prioritized if time allows
- Can start with basic functionality and iterate

### Manual Tasks Priority
- Reprint risk management is important for data completeness
- UI cleanup is important for user experience
- These can be done in parallel with other tasks
- Consider assigning to a separate developer if available

