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


def get_supabase_http_config() -> Optional[Dict[str, Any]]:
    """
    Get Supabase HTTP configuration.

    Returns:
        Dictionary with base_url and headers or None if credentials missing
    """
    supabase_url = os.getenv('SUPABASE_URL', '').strip()
    supabase_key = os.getenv('SUPABASE_KEY', '').strip()

    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials: SUPABASE_URL and SUPABASE_KEY required")
        return None

    try:
        base_url = supabase_url.rstrip('/') + '/rest/v1'
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        logger.info("Successfully configured Supabase HTTP client")
        return {
            'base_url': base_url,
            'headers': headers
        }
    except Exception as e:
        logger.error(f"Failed to configure Supabase HTTP client: {e}")
        return None


def supabase_request(config: Dict[str, Any], method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
    """
    Make a request to Supabase REST API.

    Args:
        config: Supabase configuration
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint (e.g., 'model_verification_logs')
        data: Request data for POST/PUT requests

    Returns:
        Response data or None on error
    """
    try:
        url = f"{config['base_url']}/{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=config['headers'], timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=config['headers'], json=data, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=config['headers'], json=data, timeout=30)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=config['headers'], json=data, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=config['headers'], timeout=30)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()
        
        if response.text.strip():
            return response.json()
        else:
            return []

    except requests.RequestException as e:
        logger.error(f"Supabase request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Supabase request failed with unexpected error: {e}")
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
    config: Dict[str, Any],
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
        config: Supabase configuration
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

        data = {
            'model_name': model_name,
            'location_code': location_code,
            'latitude': lat,
            'longitude': lon,
            'forecast_temp': forecast_temp,
            'actual_temp': actual_temp,
            'error_value': error_value,
            'forecast_timestamp': now,
            'observation_timestamp': now
        }

        result = supabase_request(config, 'POST', 'model_verification_logs', data)

        if result is not None:
            logger.info(f"Inserted verification result for {location_code}: error={error_value}°C")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Failed to insert verification result: {e}")
        return False


def cleanup_old_records(config: Dict[str, Any], days: int = 7) -> Optional[int]:
    """
    Delete verification records older than specified days.

    Args:
        config: Supabase configuration
        days: Number of days to retain records

    Returns:
        Number of deleted records or None on error
    """
    try:
        result = supabase_request(config, 'POST', 'rpc/cleanup_old_verification_logs', {'days_old': days})

        if result is not None:
            deleted_count = result if isinstance(result, int) else 0
            logger.info(f"Cleaned up {deleted_count} old records (older than {days} days)")
            return deleted_count
        else:
            return None

    except Exception as e:
        logger.error(f"Failed to cleanup old records: {e}")
        return None


def update_model_ranking(config: Dict[str, Any], model_name: str, error_value: float) -> bool:
    """
    Update model rankings with new verification data.

    Args:
        config: Supabase configuration
        model_name: Name of the weather model
        error_value: Error value from verification

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if model exists
        existing = supabase_request(config, 'GET', f"model_rankings?model_name=eq.{model_name}")

        if existing and len(existing) > 0:
            # Update existing model
            current = existing[0]
            new_total = current['total_verifications'] + 1
            current_avg = current['average_error'] or 0
            new_avg = ((current_avg * current['total_verifications']) + error_value) / new_total

            # Simple ELO adjustment (could be more sophisticated)
            elo_adjustment = 10 - error_value  # Lower error = higher ELO gain
            new_elo = current['elo_score'] + elo_adjustment

            update_data = {
                'elo_score': new_elo,
                'total_verifications': new_total,
                'average_error': new_avg,
                'last_updated': datetime.utcnow().isoformat()
            }

            result = supabase_request(config, 'PATCH', f"model_rankings?id=eq.{current['id']}", update_data)

            if result is not None:
                logger.info(f"Updated ranking for {model_name}")
                return True
            else:
                return False
        else:
            # Create new model entry
            new_elo = 1000 + (10 - error_value)
            new_data = {
                'model_name': model_name,
                'elo_score': new_elo,
                'total_verifications': 1,
                'average_error': error_value,
                'last_updated': datetime.utcnow().isoformat()
            }

            result = supabase_request(config, 'POST', 'model_rankings', new_data)

            if result is not None:
                logger.info(f"Created new ranking for {model_name}")
                return True
            else:
                return False

    except Exception as e:
        logger.error(f"Failed to update model ranking: {e}")
        return False


def verify_location(
    config: Dict[str, Any],
    location_code: str,
    lat: float,
    lon: float,
    model_name: str = "openmeteo_default"
) -> bool:
    """
    Run full verification for a single location.

    Args:
        config: Supabase configuration
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
        config, location_code, lat, lon,
        forecast_temp, actual_temp, error_value, model_name
    )

    if success:
        # Update rankings
        update_model_ranking(config, model_name, error_value)

    return success


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("WeatherArena Verification Pipeline - Starting")
    logger.info("=" * 60)

    # Get database configuration
    config = get_supabase_http_config()
    if not config:
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
            config,
            point["code"],
            point["lat"],
            point["lon"]
        ):
            success_count += 1

    logger.info(f"Verification complete: {success_count}/{len(verification_points)} locations successful")

    # Cleanup old records
    cleanup_old_records(config, days=7)

    logger.info("=" * 60)
    logger.info("WeatherArena Verification Pipeline - Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
