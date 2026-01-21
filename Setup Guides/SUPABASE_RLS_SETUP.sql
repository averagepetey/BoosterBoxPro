-- ============================================================================
-- SUPABASE ROW LEVEL SECURITY (RLS) SETUP
-- ============================================================================
-- 
-- IMPORTANT: Since all access goes through FastAPI (not direct client access),
-- RLS is configured as a DEFENSE-IN-DEPTH measure, not primary access control.
--
-- The service_role key (used by FastAPI) automatically bypasses RLS.
-- These policies protect against accidental exposure or misconfiguration.
--
-- Run these commands in your Supabase SQL Editor:
-- Dashboard -> SQL Editor -> New Query -> Paste and Run
-- ============================================================================

-- ============================================================================
-- STEP 1: Enable RLS on all tables
-- ============================================================================

-- Users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Booster boxes table
ALTER TABLE booster_boxes ENABLE ROW LEVEL SECURITY;

-- Unified box metrics table
ALTER TABLE unified_box_metrics ENABLE ROW LEVEL SECURITY;

-- Add any other tables you have:
-- ALTER TABLE tcg_listings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tcg_sales ENABLE ROW LEVEL SECURITY;


-- ============================================================================
-- STEP 2: Create restrictive policies (deny by default)
-- ============================================================================
-- These policies deny direct access via anon/public key.
-- The service_role key (used by your backend) bypasses these.

-- Users table: Only backend can access
CREATE POLICY "Backend only - users" ON users
    FOR ALL
    USING (false);

-- Booster boxes table: Only backend can access
CREATE POLICY "Backend only - booster_boxes" ON booster_boxes
    FOR ALL
    USING (false);

-- Unified box metrics: Only backend can access
CREATE POLICY "Backend only - unified_box_metrics" ON unified_box_metrics
    FOR ALL
    USING (false);


-- ============================================================================
-- ALTERNATIVE: If you want authenticated users to read (future Supabase Auth)
-- ============================================================================
-- Uncomment these if you later use Supabase Auth directly from the frontend:

-- -- Users can read their own data only
-- CREATE POLICY "Users read own data" ON users
--     FOR SELECT
--     USING (auth.uid() = id);

-- -- Authenticated users can read all booster boxes
-- CREATE POLICY "Authenticated read booster_boxes" ON booster_boxes
--     FOR SELECT
--     USING (auth.role() = 'authenticated');

-- -- Authenticated users can read all metrics
-- CREATE POLICY "Authenticated read metrics" ON unified_box_metrics
--     FOR SELECT
--     USING (auth.role() = 'authenticated');


-- ============================================================================
-- STEP 3: Verify RLS is enabled
-- ============================================================================
-- Run this query to check RLS status:

SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- All tables should show rowsecurity = true


-- ============================================================================
-- STEP 4: Test that anon key is blocked
-- ============================================================================
-- From your frontend or Postman, try to access Supabase directly with anon key.
-- It should return empty results or an error.
--
-- Test query (should fail or return empty):
-- SELECT * FROM booster_boxes LIMIT 1;


-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- 1. service_role key: NEVER expose to frontend. Backend only.
-- 2. anon key: Safe to expose, but RLS blocks access anyway.
-- 3. If you add new tables, remember to enable RLS on them.
-- 4. Review policies periodically as your access patterns change.
--
-- ============================================================================

