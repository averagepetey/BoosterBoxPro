# Complete Remaining Tasks Checklist

> **Last Updated:** January 2026  
> **Status:** Comprehensive checklist compiled from all project documents

This document consolidates ALL remaining tasks from every markdown file in the project.

---

## 🔴 CRITICAL BLOCKERS (Must Complete Before Launch)

### 1. Authentication & User System (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot monetize, cannot protect content

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

---

### 2. Stripe Payment Integration (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot monetize

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

#### Stripe Products & Prices
- [ ] Create subscription products in Stripe Dashboard:
  - Free Plan (optional)
  - Premium Plan ($29/month recommended)
  - Pro Plan ($79/month)
- [ ] Copy Price IDs and add to `.env`:
  - `STRIPE_PRICE_ID_FREE=price_xxxxx`
  - `STRIPE_PRICE_ID_PREMIUM=price_xxxxx`
  - `STRIPE_PRICE_ID_PRO=price_xxxxx`

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

---

### 3. Production Deployment (0% Complete)
**Status:** ❌ NOT DEPLOYED  
**Impact:** Cannot launch publicly

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

---

### 4. Data Validation & Accuracy (30% Complete)
**Status:** ⚠️ PARTIALLY WORKING  
**Impact:** Data quality issues could hurt credibility

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

---

## 🟡 IMPORTANT (Should Complete Before Launch)

### 5. Chrome Extension Fix & Implementation (0% Complete)
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Missing feature for TCGplayer integration

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

---

### 7. Frontend-Backend Integration Testing
**Status:** ⚠️ PARTIALLY WORKING

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

#### Database Security (Supabase)
- [ ] Enable Row Level Security (RLS) on all tables
- [ ] Create RLS policies for `booster_boxes` table:
  - Authenticated users can read all boxes
  - Only admin/service role can write
  - Public access denied
- [ ] Create RLS policies for `unified_box_metrics` table:
  - Authenticated users can read all metrics
  - Only admin/service role can write
  - Public access denied
- [ ] Create RLS policies for `tcg_listings` table
- [ ] Create RLS policies for `tcg_sales` table
- [ ] Create RLS policies for `tcg_listing_changes` table
- [ ] Create RLS policies for `historical_entries` table (if applicable)
- [ ] Verify database URL uses SSL/TLS (sslmode=require)
- [ ] Use connection pooling (Supabase connection pooler)
- [ ] Remove direct database URL from client-side code
- [ ] Verify `.env` files are in `.gitignore`
- [ ] Rotate database passwords
- [ ] Enable "Require SSL" for all connections
- [ ] Configure IP allowlist if applicable
- [ ] Enable audit logging for database access
- [ ] Configure backup retention policy

#### Application Security
- [ ] Verify JWT secret is strong and stored in environment variables
- [ ] Implement JWT expiration and refresh tokens
- [ ] Add rate limiting to authentication endpoints
- [ ] Implement password requirements:
  - Minimum length (8+ characters)
  - Complexity requirements
  - Password hashing (bcrypt with proper salt rounds)
- [ ] Add account lockout after failed login attempts
- [ ] Implement session management
- [ ] Add CSRF protection for state-changing operations
- [ ] Verify admin API key is properly secured
- [ ] Implement rate limiting on all API endpoints
- [ ] Add request validation and sanitization
- [ ] Implement input validation for all user inputs
- [ ] Add CORS restrictions in production:
  - Only allow frontend domain(s)
  - Remove wildcard (*) origins
  - Configure allowed methods and headers explicitly
- [ ] Add request size limits
- [ ] Implement API versioning
- [ ] Log all API access for audit trail

#### Environment Variables & Secrets
- [ ] Audit all environment variables for sensitive data
- [ ] Move all secrets to secure secret management
- [ ] Verify `.env` files are in `.gitignore`
- [ ] Never commit credentials to git
- [ ] Rotate all API keys and secrets
- [ ] Use different credentials for development/staging/production

#### Data Protection
- [ ] Encrypt sensitive data at rest (database encryption)
- [ ] Use HTTPS/TLS for all API communications
- [ ] Verify data backups are encrypted
- [ ] Implement data retention policies
- [ ] Review data that's exposed in API responses (ensure no sensitive data)

#### Error Handling & Logging
- [ ] Remove sensitive information from error messages in production
- [ ] Implement proper error logging without exposing internals
- [ ] Add structured logging for security events
- [ ] Monitor for suspicious activity
- [ ] Implement alerting for security events

#### Dependencies & Supply Chain
- [ ] Audit all Python dependencies for known vulnerabilities
- [ ] Use `pip audit` or `safety` to check dependencies
- [ ] Keep all dependencies up to date
- [ ] Review and update `requirements.txt` regularly
- [ ] Use dependency pinning for production
- [ ] Scan for vulnerable packages

#### Frontend Security
- [ ] Verify no API keys or secrets in client-side code
- [ ] Implement proper authentication state management
- [ ] Add CSRF token handling (if applicable)
- [ ] Sanitize user inputs before display
- [ ] Implement Content Security Policy (CSP) headers
- [ ] Add XSS protection
- [ ] Verify environment variables prefixed with `NEXT_PUBLIC_` are safe to expose
- [ ] Review what data is sent to client (no sensitive data)
- [ ] Verify all API calls use HTTPS
- [ ] Implement proper error handling (don't expose internals)
- [ ] Add request/response validation
- [ ] Handle authentication tokens securely (httpOnly cookies if applicable)

**Estimated Time:** 0.5-1 day

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

### 13. Testing & Quality Assurance
- [ ] End-to-end testing
- [ ] API integration tests
- [ ] Frontend component tests
- [ ] Data accuracy validation
- [ ] Performance testing
- [ ] Security testing

### 14. Frontend TODOs
- [ ] Replace all `// TODO: Replace with API call` in `frontend/app/(dashboard)/releases/page.tsx`
- [ ] Replace all `// TODO: Replace with API call` in `frontend/app/(dashboard)/releases/[id]/page.tsx`
- [ ] Re-enable auth check in `frontend/components/auth/ProtectedRoute.tsx` (currently disabled)
- [ ] Implement actual subscription status checking in `ProtectedRoute.tsx`
- [ ] Implement forgot password page navigation in `LoginModal.tsx`
- [ ] Remove debug console.log statements from `SignupModal.tsx`
- [ ] Remove debug comments from `dashboard/page.tsx`
- [ ] Implement "Market Notes & Signals" section in box detail pages (currently shows "No notes yet")

### 15. Build Status - Automated Screenshot System
- [ ] Run database migration: `alembic upgrade head` (for missing metrics fields)
- [ ] Complete data extraction formatter
- [ ] Complete automated processing pipeline
- [ ] Update historical data manager for price ladder data
- [ ] End-to-end testing of screenshot processing
- [ ] Create usage guide documentation

---

## 📋 Launch Day Checklist (From LAUNCH_DAY_CHECKLIST.md)

### Environment Configuration
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Update `CORS_ORIGINS` to production domain(s)
- [ ] Verify `JWT_SECRET_KEY` is long and random (64+ characters)
- [ ] Set Stripe secrets (live mode):
  - `STRIPE_SECRET_KEY=sk_live_xxx`
  - `STRIPE_PUBLISHABLE_KEY=pk_live_xxx`
  - `STRIPE_WEBHOOK_SECRET=whsec_xxx`
- [ ] Set admin IP allowlist: `ADMIN_ALLOWED_IPS=YOUR_IP,YOUR_OTHER_IP`
- [ ] Set `ADMIN_IP_ALLOWLIST_ENABLED=true`

### Security Verification
- [ ] Verify RLS is enabled on Supabase (all tables show `rowsecurity = true`)
- [ ] Verify database connection uses SSL (`sslmode=require`)
- [ ] Set `ADMIN_API_KEY` (generate random key)

### Frontend Configuration
- [ ] Update `NEXT_PUBLIC_API_URL` to production API URL
- [ ] Build frontend for production: `cd frontend && npm run build`
- [ ] Verify CSP headers after deployment

### Deployment
- [ ] Deploy backend API to production
- [ ] Deploy frontend to production
- [ ] Set up custom domain + HTTPS
- [ ] Configure all production environment variables

### Post-Launch Verification
- [ ] Homepage loads - No console errors
- [ ] Sign up - New user can register
- [ ] Login - User can log in
- [ ] Dashboard - Loads with data (or paywall)
- [ ] Admin access - Your admin account works
- [ ] Logout - Clears session properly
- [ ] API health - Returns `{"status":"healthy"}`

### Monitoring
- [ ] Set up error monitoring (Sentry, LogRocket, or Datadog)
- [ ] Configure error alerts

---

## 🚨 Critical Path Summary

### Must Have (Launch Blockers)
1. **Authentication** - Register, login, JWT (1-2 days)
2. **Stripe Payments** - Subscription, trial, webhooks (1-2 days)
3. **Paywall** - Protect all content (0.5 days)
4. **Production Deployment** - Backend + Frontend + Database (1-2 days)
5. **Data Validation** - Verify all 18 boxes have accurate data (1 day)
6. **Security Hardening** - RLS, CORS, rate limiting (0.5-1 day)

### Should Have (Launch Quality)
7. **UI Cleanup** - Remove redundant metrics, organize display (1-2 days)
8. **Reprint Risk** - Set for all boxes, add to UI (0.5 days)
9. **Frontend-Backend Testing** - End-to-end verification (0.5 days)
10. **Automation Verification** - Ensure cron jobs work (0.5 days)
11. **Mobile Testing** - Responsiveness, UX polish (1 day)

### Nice to Have (Post-Launch)
12. **Chrome Extension** - TCGplayer integration (2-3 days)
13. **Documentation** - User guides, FAQ, legal pages
14. **Advanced Features** - Favorites, alerts, export

---

## 📊 Estimated Timeline

**Minimum Viable Launch (Critical Blockers Only):**
- Authentication: 1-2 days
- Payments: 1-2 days
- Deployment: 1-2 days
- Data Validation: 1 day
- Security: 0.5-1 day
**Total: 4.5-8 days**

**Launch-Ready (Including Should-Haves):**
- Add UI Cleanup: 1-2 days
- Add Testing: 0.5 days
- Add Automation Verification: 0.5 days
- Add Mobile Testing: 1 day
**Total: 7.5-12 days**

---

## ✅ Quick Reference: Priority Order

1. **Day 1-2:** Authentication & User System
2. **Day 2-3:** Stripe Payments Integration
3. **Day 3-4:** Production Deployment
4. **Day 4:** Data Validation & Manual Tasks
5. **Day 5:** Security Hardening & Testing
6. **Day 6+:** UI Cleanup, Chrome Extension, Documentation

---

## 📝 Notes

- Chrome extension can be launched post-MVP if needed
- Manual tasks (reprint risk, UI cleanup) can be done in parallel with other tasks
- Security audit should be completed before public launch
- All critical blockers must be completed before launch
- Should-haves improve launch quality but aren't blockers
- Nice-to-haves can be added incrementally post-launch

---

**Last Updated:** January 2026  
**Next Review:** After completing critical blockers

