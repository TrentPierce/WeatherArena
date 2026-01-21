#!/usr/bin/env python3
"""
WeatherArena Verification Pipeline
Zero-storage architecture: Calculate errors immediately, discard raw data.

Usage:
    python weather_verification.py

Environment Variables:
    SUPABASE_URL - Supabase project URL
    SUPABASE_KEY - Supabase service role key
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_supabase_http_client() -> Optional[Dict[str, Any]]:
    """
    Create and return a Supabase HTTP client configuration.

    Returns:
        Dictionary with base_url and headers for making HTTP requests
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials: SUPABASE_URL and SUPABASE_KEY required")
        return None

    try:
        # For Supabase, we need to use the /rest/v1 endpoint
        base_url = supabase_url.rstrip('/') + '/rest/v1'
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info("Successfully configured Supabase HTTP client")
        return {
            'base_url': base_url,
            'headers': headers
        }
    except Exception as e:
        logger.error(f"Failed to configure Supabase HTTP client: {e}")
        return None


def fetch_openmeteo_forecast(lat: float, lon: float) -> Optional[float]:
    """
    Fetch forecast temperature from Open-Meteo API.

    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        Forecast temperature in Celsius or None on error
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current" not in data:
            logger.error(f"Forecast API response missing 'current' field")
            return None

        temp = data["current"]["temperature_2m"]
        logger.info(f"Fetched forecast temperature: {temp}°C")
        return temp

    except requests.RequestException as e:
        logger.error(f"Failed to fetch forecast from Open-Meteo: {e}")
        return None


def fetch_openmeteo_current(lat: float, lon: float) -> Optional[float]:
    """
    Fetch current observation temperature from Open-Meteo API.

    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        Current temperature in Celsius or None on error
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "hourly": "temperature_2m"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current" not in data:
            logger.error(f"Current weather API response missing 'current' field")
            return None

        temp = data["current"]["temperature_2m"]
        logger.info(f"Fetched current temperature: {temp}°C")
        return temp

    except requests.RequestException as e:
        logger.error(f"Failed to fetch current weather from Open-Meteo: {e}")
        return None


def calculate_error(forecast_temp: float, actual_temp: float) -> float:
    """
    Calculate absolute error between forecast and actual temperature.

    Args:
        forecast_temp: Forecast temperature
        actual_temp: Actual observed temperature

    Returns:
        Absolute difference in Celsius
    """
    return abs(forecast_temp - actual_temp)


def insert_verification_result(
    db: SyncPostgrestClient,
    location_code: str,
    lat: float,
    lon: float,
    forecast_temp: float,
    actual_temp: float,
    error_value: float,
    model_name: str = "openmeteo_default"
) -> bool:
    """
    Insert verification result into model_verification_logs table.

    Args:
        db: Postgrest client
        location_code: Location identifier (e.g., 'JFK')
        lat: Latitude
        lon: Longitude
        forecast_temp: Forecast temperature
        actual_temp: Actual temperature
        error_value: Calculated error
        model_name: Name of the weather model

    Returns:
        True if successful, False otherwise
    """
    try:
        now = datetime.utcnow().isoformat()

        db.table('model_verification_logs').insert({
            'model_name': model_name,
            'location_code': location_code,
            'latitude': lat,
            'longitude': lon,
            'forecast_temp': forecast_temp,
            'actual_temp': actual_temp,
            'error_value': error_value,
            'forecast_timestamp': now,
            'observation_timestamp': now
        }).execute()

        logger.info(f"Inserted verification result for {location_code}: error={error_value}°C")
        return True

    except Exception as e:
        logger.error(f"Failed to insert verification result: {e}")
        return False


def cleanup_old_records(db: SyncPostgrestClient, days: int = 7) -> Optional[int]:
    """
    Delete verification records older than specified days.

    Args:
        db: Postgrest client
        days: Number of days to retain records

    Returns:
        Number of deleted records or None on error
    """
    try:
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        result = db.rpc('cleanup_old_verification_logs', {
            'days_old': days
        }).execute()

        deleted_count = result.data
        logger.info(f"Cleaned up {deleted_count} old records (older than {days} days)")
        return deleted_count

    except Exception as e:
        logger.error(f"Failed to cleanup old records: {e}")
        return None


def update_model_ranking(db: SyncPostgrestClient, model_name: str, error_value: float) -> bool:
    """
    Update model rankings with new verification data.

    Args:
        db: Supabase client
        model_name: Name of the weather model
        error_value: Error value from verification

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if model exists
        existing = db.table('model_rankings').select(
            'id', 'elo_score', 'total_verifications', 'average_error'
        ).eq('model_name', model_name).execute()

        if existing.data:
            # Update existing model
            current = existing.data[0]
            new_total = current['total_verifications'] + 1
            current_avg = current['average_error'] or 0
            new_avg = ((current_avg * current['total_verifications']) + error_value) / new_total

            # Simple ELO adjustment (could be more sophisticated)
            elo_adjustment = 10 - error_value  # Lower error = higher ELO gain
            new_elo = current['elo_score'] + elo_adjustment

            db.table('model_rankings').update({
                'elo_score': new_elo,
                'total_verifications': new_total,
                'average_error': new_avg,
                'last_updated': datetime.utcnow().isoformat()
            }).eq('model_name', model_name).execute()
        else:
            # Create new model entry
            new_elo = 1000 + (10 - error_value)
            db.table('model_rankings').insert({
                'model_name': model_name,
                'elo_score': new_elo,
                'total_verifications': 1,
                'average_error': error_value,
                'last_updated': datetime.utcnow().isoformat()
            }).execute()

        logger.info(f"Updated ranking for {model_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to update model ranking: {e}")
        return False


def verify_location(
    db: SyncPostgrestClient,
    location_code: str,
    lat: float,
    lon: float,
    model_name: str = "openmeteo_default"
) -> bool:
    """
    Run full verification for a single location.

    Args:
        db: Postgrest client
        location_code: Location identifier
        lat: Latitude
        lon: Longitude
        model_name: Name of the weather model

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Starting verification for {location_code} ({lat}, {lon})")

    # Fetch forecast and current temperatures
    forecast_temp = fetch_openmeteo_forecast(lat, lon)
    actual_temp = fetch_openmeteo_current(lat, lon)

    if forecast_temp is None or actual_temp is None:
        logger.error(f"Failed to fetch temperatures for {location_code}")
        return False

    # Calculate error
    error_value = calculate_error(forecast_temp, actual_temp)
    logger.info(f"Calculated error: {error_value}°C")

    # Store in database
    success = insert_verification_result(
        db, location_code, lat, lon,
        forecast_temp, actual_temp, error_value, model_name
    )

    if success:
        # Update rankings
        update_model_ranking(db, model_name, error_value)

    return success


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("WeatherArena Verification Pipeline - Starting")
    logger.info("=" * 60)

    # Get database client
    db = get_postgrest_client()
    if not db:
        logger.error("Failed to initialize database connection. Exiting.")
        return

    # Define verification points (starting with JFK)
    verification_points = [
        {
            "code": "JFK",
            "name": "John F. Kennedy International Airport",
            "lat": 40.6413,
            "lon": -73.7781
        }
        # Add more airports here as needed
    ]

    # Run verification for each point
    success_count = 0
    for point in verification_points:
        if verify_location(
            db,
            point["code"],
            point["lat"],
            point["lon"]
        ):
            success_count += 1

    logger.info(f"Verification complete: {success_count}/{len(verification_points)} locations successful")

    # Cleanup old records
    cleanup_old_records(db, days=7)

    logger.info("=" * 60)
    logger.info("WeatherArena Verification Pipeline - Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
