#!/usr/bin/env python3
"""
Test script for WeatherArena verification pipeline.
Validates API connectivity and database operations without storing data.
"""

import os
import logging
from typing import Optional
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


def test_openmeteo_api(lat: float = 40.6413, lon: float = -73.7781) -> bool:
    """
    Test Open-Meteo API connectivity.

    Returns:
        True if API is accessible, False otherwise
    """
    logger.info(f"Testing Open-Meteo API for lat={lat}, lon={lon}")

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m",
            "timezone": "auto"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "current" not in data:
            logger.error("API response missing 'current' field")
            return False

        temp = data["current"]["temperature_2m"]
        logger.info(f"✓ Open-Meteo API working: {temp}°C")
        return True

    except requests.RequestException as e:
        logger.error(f"✗ Open-Meteo API failed: {e}")
        return False


def test_supabase_connection() -> bool:
    """
    Test Supabase database connection.

    Returns:
        True if connection successful, False otherwise
    """
    logger.info("Testing Supabase connection")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        logger.error("✗ Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        logger.info("  Set these in .env file or GitHub Secrets")
        return False

    try:
        from supabase import create_client

        client = create_client(supabase_url, supabase_key)

        # Test connection by querying the rankings table
        result = client.table('model_rankings').select('*').limit(1).execute()

        logger.info(f"✓ Supabase connection successful")
        logger.info(f"  Found {len(result.data)} existing rankings")
        return True

    except ImportError:
        logger.error("✗ Supabase client not installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"✗ Supabase connection failed: {e}")
        return False


def test_error_calculation() -> bool:
    """
    Test error calculation logic.

    Returns:
        True if logic is correct, False otherwise
    """
    logger.info("Testing error calculation")

    # Test cases
    test_cases = [
        (20.0, 18.0, 2.0),    # Forecast higher
        (15.0, 20.0, 5.0),    # Actual higher
        (10.0, 10.0, 0.0),    # Perfect match
    ]

    for forecast, actual, expected in test_cases:
        error = abs(forecast - actual)
        if error != expected:
            logger.error(f"✗ Error calculation failed: {forecast} - {actual} = {error}, expected {expected}")
            return False
        logger.info(f"  ✓ |{forecast} - {actual}| = {error}")

    logger.info("✓ Error calculation logic correct")
    return True


def run_all_tests() -> bool:
    """
    Run all validation tests.

    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("=" * 60)
    logger.info("WeatherArena Validation Tests")
    logger.info("=" * 60)

    tests = [
        ("Open-Meteo API", test_openmeteo_api),
        ("Error Calculation", test_error_calculation),
        ("Supabase Connection", test_supabase_connection),
    ]

    results = {}
    for name, test_func in tests:
        logger.info(f"\n--- Testing {name} ---")
        results[name] = test_func()

    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{name:25} {status}")
        if not passed:
            all_passed = False

    logger.info("=" * 60)

    if all_passed:
        logger.info("All tests passed! Ready to deploy.")
    else:
        logger.error("Some tests failed. Please fix issues before deploying.")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
