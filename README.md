# WeatherArena

A zero-storage weather model ranking platform built entirely on free-tier infrastructure.

## Architecture

**Zero-Storage Pipeline**: Calculate errors immediately, discard raw forecasts. Store only metrics.

### Components

1. **Verification Pipeline** (Python)
   - Fetches forecasts from Open-Meteo API (free)
   - Fetches current observations for comparison
   - Calculates error immediately
   - Stores only: model_name, location, error_value, timestamps
   - Auto-cleanup: Hard DELETE records older than 7 days

2. **Database** (Supabase/PostgreSQL - Free Tier)
   - `model_verification_logs`: Hourly error calculations (auto-cleanup)
   - `model_rankings`: Long-term Elo-style scores (permanent)

3. **Scheduler** (GitHub Actions - Free)
   - Runs every hour via cron: `0 * * * *`
   - Python execution in serverless environment

4. **Frontend** (Vercel - Free, Optional)
   - Map visualization using Leaflet + Open-Meteo WMS
   - Leaderboard from Supabase rankings table

## Quick Start

### 1. Set Up Supabase

```bash
# Create a free account at supabase.com
# Create a new project

# Apply the database schema
psql -h db.your-project.supabase.co -U postgres -d postgres -f database/schema.sql

# Get your credentials:
# - Project URL: https://your-project.supabase.co
# - Service Role Key: Settings > API > service_role (secret!)
```

### 2. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_service_role_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Locally

```bash
python scripts/weather_verification.py
```

### 5. Deploy to GitHub Actions

```bash
# Add repository secrets
# Settings > Secrets and variables > Actions > New repository secret
# - SUPABASE_URL (your project URL)
# - SUPABASE_KEY (service role key - NOT anon key!)

# Push to GitHub
git add .
git commit -m "Add WeatherArena verification pipeline"
git push origin main
```

The workflow will now run automatically every hour!

## Database Schema

### `model_verification_logs`

Stores hourly error calculations. Auto-cleanup removes records older than 7 days.

```sql
- id: BIGSERIAL PRIMARY KEY
- model_name: VARCHAR(100) -- Model identifier
- location_code: VARCHAR(10) -- e.g., 'JFK'
- latitude: DECIMAL(10, 6)
- longitude: DECIMAL(10, 6)
- forecast_temp: DECIMAL(5, 2)
- actual_temp: DECIMAL(5, 2)
- error_value: DECIMAL(5, 2) -- Absolute difference
- forecast_timestamp: TIMESTAMP WITH TIME ZONE
- observation_timestamp: TIMESTAMP WITH TIME ZONE
- created_at: TIMESTAMP WITH TIME ZONE
```

### `model_rankings`

Long-term Elo-style scores (permanent, no cleanup needed).

```sql
- id: SERIAL PRIMARY KEY
- model_name: VARCHAR(100) UNIQUE
- elo_score: DECIMAL(10, 2) -- Starts at 1000
- total_verifications: INTEGER
- average_error: DECIMAL(5, 2)
- last_updated: TIMESTAMP WITH TIME ZONE
```

## Adding More Verification Points

Edit `scripts/weather_verification.py` and add to the `verification_points` list:

```python
verification_points = [
    {
        "code": "JFK",
        "name": "John F. Kennedy International Airport",
        "lat": 40.6413,
        "lon": -73.7781
    },
    {
        "code": "LAX",
        "name": "Los Angeles International Airport",
        "lat": 33.9425,
        "lon": -118.4081
    },
    # Add more...
]
```

## API Sources

- **Open-Meteo Forecast API**: `https://api.open-meteo.com/v1/forecast`
  - Free, no authentication required
  - Current weather + hourly forecasts

- **Open-Meteo Current API**: Same endpoint, different parameters
  - Real-time observations from ground stations

## Cost Optimization

### Storage
- Only store error metrics, not raw forecasts
- Auto-cleanup deletes records after 7 days
- Rankings table remains small (one row per model)

### Compute
- GitHub Actions: 2000 free minutes/month
  - ~44 hours = enough for hourly runs
- Supabase: 500MB database storage (free tier)
  - Should handle years of rankings data

### Network
- Open-Meteo: Free, unlimited API calls
- Supabase: Free tier includes 50GB bandwidth/month

## Monitoring

Check logs in GitHub Actions:
```bash
# Go to your repository > Actions tab > Select workflow run > View logs
```

Query Supabase directly:
```sql
-- View recent errors
SELECT
    location_code,
    model_name,
    error_value,
    created_at
FROM model_verification_logs
ORDER BY created_at DESC
LIMIT 10;

-- View rankings
SELECT * FROM model_rankings ORDER BY elo_score DESC;
```

## Security Notes

⚠️ **Important**:
- Use **Service Role Key** (not anon key) for backend operations
- Never commit `.env` to version control
- GitHub Secrets encrypt your credentials at rest
- Supabase RLS policies should restrict public access

## License

MIT
