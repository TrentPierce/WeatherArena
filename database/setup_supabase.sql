-- ============================================================================
-- WEATHERARENA DATABASE SETUP - RUN THIS IN SUPABASE SQL EDITOR
-- ============================================================================

-- Step 1: Create model_verification_logs table
CREATE TABLE IF NOT EXISTS model_verification_logs (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    location_code VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    forecast_temp DECIMAL(5, 2) NOT NULL,
    actual_temp DECIMAL(5, 2) NOT NULL,
    error_value DECIMAL(5, 2) NOT NULL,
    forecast_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    observation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create index for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_verification_logs_created_at
ON model_verification_logs(created_at);

-- Step 3: Create model_rankings table
CREATE TABLE IF NOT EXISTS model_rankings (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    elo_score DECIMAL(10, 2) DEFAULT 1000.00,
    total_verifications INTEGER DEFAULT 0,
    average_error DECIMAL(5, 2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create cleanup function (deletes records older than 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_verification_logs(days_old INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM model_verification_logs
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Step 5: Enable Row Level Security (RLS)
ALTER TABLE model_rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_verification_logs ENABLE ROW LEVEL SECURITY;

-- Step 6: Create RLS policies for public read access (required for website)
-- Allow anyone to read model_rankings
CREATE POLICY "Allow public read access to model_rankings" 
ON model_rankings FOR SELECT 
TO anon, authenticated
USING (true);

-- Allow anyone to read model_verification_logs
CREATE POLICY "Allow public read access to model_verification_logs" 
ON model_verification_logs FOR SELECT 
TO anon, authenticated
USING (true);

-- Allow service_role to insert/update/delete (for the GitHub Action)
CREATE POLICY "Allow service_role full access to model_rankings" 
ON model_rankings FOR ALL 
TO service_role
USING (true);

CREATE POLICY "Allow service_role full access to model_verification_logs" 
ON model_verification_logs FOR ALL 
TO service_role
USING (true);

-- Step 7: Grant permissions
-- Grant read access to anon (anonymous/public) and authenticated users
GRANT SELECT ON model_rankings TO anon;
GRANT SELECT ON model_verification_logs TO anon;
GRANT SELECT ON model_rankings TO authenticated;
GRANT SELECT ON model_verification_logs TO authenticated;

-- Grant all permissions to service_role (for GitHub Action writes)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Step 8: Verify tables were created
SELECT
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('model_verification_logs', 'model_rankings')
ORDER BY tablename;

-- ============================================================================

