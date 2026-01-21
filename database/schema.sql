-- WeatherArena Database Schema
-- Zero-storage design: Only store error metrics, discard raw forecasts

-- Model verification logs (hourly error calculations)
CREATE TABLE IF NOT EXISTS model_verification_logs (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    location_code VARCHAR(10) NOT NULL, -- e.g., 'JFK'
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    forecast_temp DECIMAL(5, 2) NOT NULL, -- Temperature forecast
    actual_temp DECIMAL(5, 2) NOT NULL, -- Actual observation
    error_value DECIMAL(5, 2) NOT NULL, -- Absolute difference
    forecast_timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- When forecast was made
    observation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- When observation was taken
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_verification_logs_created_at
ON model_verification_logs(created_at);

-- Model rankings (long-term Elo-style scores)
CREATE TABLE IF NOT EXISTS model_rankings (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    elo_score DECIMAL(10, 2) DEFAULT 1000.00, -- Starting score
    total_verifications INTEGER DEFAULT 0,
    average_error DECIMAL(5, 2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Auto-cleanup function: Delete records older than specified days
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

-- Trigger to automatically run cleanup after new inserts (optional)
-- Uncomment if you want automatic cleanup after each batch
-- CREATE OR REPLACE FUNCTION trigger_cleanup_verification_logs()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     PERFORM cleanup_old_verification_logs(7);
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER auto_cleanup_verification_logs
-- AFTER INSERT ON model_verification_logs
-- FOR EACH STATEMENT
-- EXECUTE FUNCTION trigger_cleanup_verification_logs();
