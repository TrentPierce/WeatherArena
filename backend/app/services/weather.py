import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import requests
import xarray as xr
from herbie import Herbie
import threading
from functools import lru_cache

logger = logging.getLogger(__name__)

# Global cache for the latest grid
# In a real app, use a proper cache (Redis or disk)
GRID_CACHE = {}

class WeatherService:
    def __init__(self):
        pass

    async def get_forecast(self, lat: float, lon: float, model: str = "openmeteo") -> Dict[str, Any]:
        """
        Fetch point forecast (Temp, Wind, Dewpoint).
        """
        if model == "openmeteo":
            return self._get_openmeteo_forecast(lat, lon)
        elif model in ["hrrr", "gfs", "nam"]:
            return await self._get_herbie_point(lat, lon, model)
        else:
            raise ValueError(f"Unknown model: {model}")

    async def get_current_observation(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current conditions (Temp, Wind, Dewpoint).
        """
        # Using OpenMeteo Current Weather for now
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,dew_point_2m",
            "timezone": "auto"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("current", {})
            return {
                "temp": data.get("temperature_2m"),
                "wind": data.get("wind_speed_10m"),
                "dewpoint": data.get("dew_point_2m")
            }
        except Exception as e:
            logger.error(f"Observation Error: {e}")
            return {}

    def _get_openmeteo_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,dew_point_2m",
            "timezone": "auto"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("current", {})
            return {
                "temp": data.get("temperature_2m"),
                "wind": data.get("wind_speed_10m"),
                "dewpoint": data.get("dew_point_2m")
            }
        except Exception as e:
            logger.error(f"OpenMeteo Error: {e}")
            return {}

    async def _get_herbie_point(self, lat: float, lon: float, model: str) -> Dict[str, Any]:
        """
        Extract point value from GRIB2 via Herbie.
        """
        try:
            ds = await self.get_model_grid(model)
            if ds is None:
                return {}
            
            # Extract multiple variables if available
            # Note: This requires the cached DS to contain all vars, which means get_model_grid needs update
            # For prototype, we'll just support Temp for Herbie path until 'get_model_grid' is multi-var
            
            result = {}
            if 't2m' in ds:
                 val = ds.t2m.sel(latitude=lat, longitude=lon, method="nearest").values
                 result['temp'] = float(val - 273.15) if val > 200 else float(val)
            
            # Add wind/dewpoint logic here if GRIB has them
                 
            return result
        except Exception as e:
            logger.error(f"Herbie Point Error: {e}")
            return {}

    async def get_model_grid(self, model: str) -> Optional[xr.Dataset]:
        """
        Get the latest model grid. Uses in-memory cache.
        """
        key = f"{model}_latest"
        
        if key in GRID_CACHE:
            return GRID_CACHE[key]
            
        # If not cached, fetch it
        # This is a blocking operation, should be run in threadpool in real app
        try:
            # Look for recent run
            # Herbie defaults to latest available
            H = Herbie(datetime.utcnow(), model=model, save_dir='./data')
            
            # Download/Open GRIB2 for Temperature (2m)
            # searchString filters the GRIB messages.
            ds = H.xarray("TMP:2 m", remove_grib=False)
            
            # Rename to standard 't2m' if needed or keep as is
            # GRIB variable names vary. Herbie usually maps them well.
            
            GRID_CACHE[key] = ds
            return ds
        except Exception as e:
            logger.error(f"Herbie Grid fetch error: {e}")
            return None
            
weather_service = WeatherService()
