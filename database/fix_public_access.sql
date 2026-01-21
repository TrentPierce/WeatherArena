-- ============================================================================
-- WEATHERARENA - FIX PUBLIC ACCESS FOR WEBSITE
-- Run this in your Supabase SQL Editor to enable anonymous read access
-- ============================================================================

-- Step 1: Enable Row Level Security (RLS) on both tables
ALTER TABLE model_rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_verification_logs ENABLE ROW LEVEL SECURITY;

-- Step 2: Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Allow public read access to model_rankings" ON model_rankings;
DROP POLICY IF EXISTS "Allow public read access to model_verification_logs" ON model_verification_logs;
DROP POLICY IF EXISTS "Allow service_role full access to model_rankings" ON model_rankings;
DROP POLICY IF EXISTS "Allow service_role full access to model_verification_logs" ON model_verification_logs;

-- Step 3: Create RLS policies for public read access (required for website)
-- Allow anonymous users (website visitors) to read model_rankings
CREATE POLICY "Allow public read access to model_rankings" 
ON model_rankings FOR SELECT 
TO anon, authenticated
USING (true);

-- Allow anonymous users (website visitors) to read model_verification_logs
CREATE POLICY "Allow public read access to model_verification_logs" 
ON model_verification_logs FOR SELECT 
TO anon, authenticated
USING (true);

-- Step 4: Allow service_role (GitHub Action) to have full access for writes
CREATE POLICY "Allow service_role full access to model_rankings" 
ON model_rankings FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow service_role full access to model_verification_logs" 
ON model_verification_logs FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Step 5: Grant SELECT permissions to anon role
GRANT SELECT ON model_rankings TO anon;
GRANT SELECT ON model_verification_logs TO anon;

-- Step 6: Verify policies were created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies 
WHERE tablename IN ('model_rankings', 'model_verification_logs')
ORDER BY tablename, policyname;

-- ============================================================================
-- After running this, the website should be able to fetch data!
-- ============================================================================
