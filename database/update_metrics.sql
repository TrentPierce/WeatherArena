-- Add new columns to verification logs
ALTER TABLE model_verification_logs 
ADD COLUMN IF NOT EXISTS forecast_wind_speed DECIMAL(5, 2),
ADD COLUMN IF NOT EXISTS actual_wind_speed DECIMAL(5, 2),
ADD COLUMN IF NOT EXISTS error_wind_speed DECIMAL(5, 2),
ADD COLUMN IF NOT EXISTS forecast_dewpoint DECIMAL(5, 2),
ADD COLUMN IF NOT EXISTS actual_dewpoint DECIMAL(5, 2),
ADD COLUMN IF NOT EXISTS error_dewpoint DECIMAL(5, 2);

-- Update rankings table to support categories
-- For simplicity in this iteration, we will add specific columns
ALTER TABLE model_rankings
ADD COLUMN IF NOT EXISTS elo_temp DECIMAL(10, 2) DEFAULT 1200.00,
ADD COLUMN IF NOT EXISTS elo_wind DECIMAL(10, 2) DEFAULT 1200.00,
ADD COLUMN IF NOT EXISTS elo_dewpoint DECIMAL(10, 2) DEFAULT 1200.00;

-- Optional: Create a view for a composite score
CREATE OR REPLACE VIEW model_leaderboard AS
SELECT 
    model_name,
    elo_temp,
    elo_wind,
    elo_dewpoint,
    (elo_temp + elo_wind + elo_dewpoint) / 3 as composite_score,
    total_verifications
FROM model_rankings;
