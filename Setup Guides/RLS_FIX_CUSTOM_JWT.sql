-- ============================================================
-- RLS FIX: Custom JWT (Not Using Supabase Auth)
-- ============================================================
--
-- PROBLEM: We used auth.uid() in our RLS policies, but we're using
-- custom FastAPI JWT, not Supabase Auth. auth.uid() returns NULL
-- for our users, so the policies don't work as expected.
--
-- SOLUTION: Since frontend ONLY calls FastAPI (never Supabase directly),
-- we should block ALL direct client access to sensitive tables.
-- FastAPI uses service_role key which bypasses RLS anyway.
--
-- ============================================================

-- Drop the broken policies that use auth.uid()
DROP POLICY IF EXISTS "users_select_own" ON users;
DROP POLICY IF EXISTS "users_update_own" ON users;

-- USERS TABLE: No direct client access at all
-- All user operations go through FastAPI (which uses service_role)
-- This is the safest approach when using custom JWT

-- If you ever need client reads (e.g., public profiles), create specific policies:
-- CREATE POLICY "users_public_profile_read"
-- ON users FOR SELECT
-- TO anon, authenticated
-- USING (is_public = true);  -- Only if you add a public profile feature

-- ============================================================
-- VERIFICATION: Run this to confirm no dangerous policies exist
-- ============================================================

-- SELECT tablename, policyname, cmd, qual 
-- FROM pg_policies 
-- WHERE schemaname = 'public' AND tablename = 'users';

-- Expected result: No rows (users table has no client-accessible policies)
-- All user access goes through FastAPI with service_role key

-- ============================================================
-- SUMMARY OF SAFE RLS POSTURE
-- ============================================================
-- 
-- booster_boxes: Public SELECT (intentional - leaderboard data)
-- unified_box_metrics: Public SELECT (intentional - metrics data)  
-- users: NO client policies (all access via FastAPI)
--
-- ============================================================

