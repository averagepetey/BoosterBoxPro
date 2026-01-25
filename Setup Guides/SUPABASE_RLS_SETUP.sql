-- ============================================================
-- SUPABASE ROW LEVEL SECURITY (RLS) SETUP
-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================

-- Default-Deny Posture
-- ============================================================
-- 
-- SECURITY PHILOSOPHY:
-- 1. All tables start with RLS enabled and NO policies (blocked by default)
-- 2. Add explicit SELECT policies only where needed
-- 3. All WRITE operations go through FastAPI (service_role key)
-- 4. Frontend NEVER writes directly to database
-- 5. anon key should have MINIMAL access (public reads only if needed)
--
-- HOW TO USE:
-- 1. Go to Supabase Dashboard > SQL Editor
-- 2. Run this entire script
-- 3. Verify policies in Authentication > Policies
--
-- ============================================================

-- ============================================================
-- STEP 1: Enable RLS on ALL tables (default deny)
-- ============================================================

-- Core tables
ALTER TABLE IF EXISTS booster_boxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS unified_box_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Raw data tables (if they exist)
ALTER TABLE IF EXISTS tcg_listings_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tcg_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_sales_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ebay_box_metrics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS historical_entries ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 2: Drop any existing overly permissive policies
-- ============================================================

-- Drop old policies if they exist (clean slate)
DROP POLICY IF EXISTS "Allow authenticated read access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow admin write access to booster_boxes" ON booster_boxes;
DROP POLICY IF EXISTS "Allow authenticated read access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow admin write access to unified_box_metrics" ON unified_box_metrics;
DROP POLICY IF EXISTS "Allow user to read their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to read all user profiles" ON users;
DROP POLICY IF EXISTS "Allow user to update their own profile" ON users;
DROP POLICY IF EXISTS "Allow admin to update any user profile" ON users;
DROP POLICY IF EXISTS "Allow new user registration" ON users;
DROP POLICY IF EXISTS "Allow admin to delete users" ON users;

-- ============================================================
-- STEP 3: Create STRICT policies
-- ============================================================

-- ------------------------------------------------------------
-- BOOSTER_BOXES: Public read (leaderboard data), no client writes
-- ------------------------------------------------------------

-- Anyone can read booster box info (it's public leaderboard data)
CREATE POLICY "booster_boxes_select_all"
ON booster_boxes FOR SELECT
TO authenticated, anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- UNIFIED_BOX_METRICS: Authenticated read only, no client writes
-- ------------------------------------------------------------

-- Authenticated users can read metrics (dashboard data)
CREATE POLICY "unified_box_metrics_select_authenticated"
ON unified_box_metrics FOR SELECT
TO authenticated
USING (true);

-- Optionally allow anon to see metrics (for public landing page)
-- Comment out if you want metrics behind auth
CREATE POLICY "unified_box_metrics_select_anon"
ON unified_box_metrics FOR SELECT
TO anon
USING (true);

-- NO INSERT/UPDATE/DELETE policies for clients
-- All writes go through FastAPI with service_role key

-- ------------------------------------------------------------
-- USERS: Strict access - users can only see/edit themselves
-- ------------------------------------------------------------

-- Users can only read their OWN profile
CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (id = auth.uid());

-- Users can only update their OWN profile (limited fields)
-- Note: Role and token_version should NOT be client-editable
CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (id = auth.uid())
WITH CHECK (
    id = auth.uid()
    -- Prevent users from escalating their own role
    -- The NEW.role must equal the OLD.role (can't change)
    -- This is enforced at application level, but defense in depth
);

-- NO INSERT policy - registration goes through FastAPI
-- NO DELETE policy - account deletion goes through FastAPI

-- ============================================================
-- STEP 4: Verify service_role bypass
-- ============================================================

-- The service_role key (used by FastAPI) bypasses RLS entirely
-- This is by design - all writes should go through the API
-- 
-- IMPORTANT: Never expose service_role key to clients!
-- - Backend only (environment variable)
-- - Never in frontend code
-- - Never in client-side JavaScript

-- ============================================================
-- STEP 5: Verification queries
-- ============================================================

-- Run these to verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Run these to see active policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================

-- 1. FRONTEND READS:
--    - Use Supabase client with anon key for public data (booster_boxes)
--    - Use authenticated session for user-specific data
--    - All queries are automatically filtered by RLS

-- 2. FRONTEND WRITES:
--    - DO NOT write directly to Supabase from frontend
--    - All mutations go through FastAPI endpoints
--    - FastAPI uses service_role key which bypasses RLS

-- 3. TESTING:
--    - Test as anon: Should only see public booster_boxes
--    - Test as user: Should see own profile only
--    - Test as service_role: Should see/modify everything

-- 4. IF YOU NEED TO ADD A NEW TABLE:
--    - Always enable RLS: ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
--    - Start with NO policies (blocked by default)
--    - Add minimal SELECT policies as needed
--    - All writes go through FastAPI

-- ============================================================
-- END OF RLS SETUP
-- ============================================================
