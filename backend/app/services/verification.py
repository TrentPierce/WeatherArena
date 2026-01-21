import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..database import get_supabase_client
from .weather import weather_service

logger = logging.getLogger(__name__)

class VerificationService:
    def __init__(self):
        pass

    async def verify_location(self, location_code: str, lat: float, lon: float, model: str = "openmeteo") -> bool:
        logger.info(f"Starting verification for {location_code} ({lat}, {lon})")
        
        # Fetch Data
        # In a real app, these would be separate calls for Forecast (History) vs Observation (Current)
        fcst_data = await weather_service.get_forecast(lat, lon, model)
        obs_data = await weather_service.get_current_observation(lat, lon) # Need to implement this in WeatherService

        if not fcst_data or not obs_data:
            logger.error(f"Data fetch failed for {location_code}")
            return False

        # Calculate Errors
        # Temp
        t_err = abs(fcst_data.get('temp', 0) - obs_data.get('temp', 0))
        # Wind
        w_err = abs(fcst_data.get('wind', 0) - obs_data.get('wind', 0))
        # Dewpoint
        d_err = abs(fcst_data.get('dewpoint', 0) - obs_data.get('dewpoint', 0))
        
        # Record
        return self._record_result(
            location_code, lat, lon, 
            fcst_data, obs_data, 
            {'temp': t_err, 'wind': w_err, 'dewpoint': d_err}, 
            model
        )

    def _record_result(self, location_code: str, lat: float, lon: float, fcst: dict, obs: dict, errors: dict, model: str) -> bool:
        supabase = get_supabase_client()
        now = datetime.utcnow().isoformat()
        
        data = {
            'model_name': model,
            'location_code': location_code,
            'latitude': lat,
            'longitude': lon,
            'forecast_temp': fcst.get('temp'),
            'actual_temp': obs.get('temp'),
            'error_value': errors.get('temp'), # Legacy column
            'forecast_wind_speed': fcst.get('wind'),
            'actual_wind_speed': obs.get('wind'),
            'error_wind_speed': errors.get('wind'),
            'forecast_dewpoint': fcst.get('dewpoint'),
            'actual_dewpoint': obs.get('dewpoint'),
            'error_dewpoint': errors.get('dewpoint'),
            'forecast_timestamp': now,
            'observation_timestamp': now
        }
        
        try:
            supabase.table('model_verification_logs').insert(data).execute()
            self._update_ranking(model, errors)
            return True
        except Exception as e:
            logger.error(f"DB Error: {e}")
            return False

    def _update_ranking(self, model: str, errors: Dict[str, float]):
        supabase = get_supabase_client()
        try:
            # Fetch existing
            res = supabase.table('model_rankings').select("*").eq('model_name', model).execute()
            existing = res.data
            
            if existing:
                current = existing[0]
                new_total = current['total_verifications'] + 1
                
                # Update Elos independently
                updates = {
                    'total_verifications': new_total,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                for metric in ['temp', 'wind', 'dewpoint']:
                    col_name = f"elo_{metric}"
                    # Use 1200 as default if column is new/null
                    current_elo = current.get(col_name) or 1200.0
                    
                    # Performance logic:
                    # Temp: Target error 1.0C
                    # Wind: Target error 2.0 km/h
                    # Dewpoint: Target error 1.5C
                    targets = {'temp': 1.0, 'wind': 2.0, 'dewpoint': 1.5}
                    perf = targets[metric] - errors[metric]
                    new_elo = current_elo + (perf * 2)
                    updates[col_name] = new_elo
                
                supabase.table('model_rankings').update(updates).eq('id', current['id']).execute()
            else:
                # Initialize
                data = {
                    'model_name': model,
                    'total_verifications': 1,
                    'last_updated': datetime.utcnow().isoformat()
                }
                for metric in ['temp', 'wind', 'dewpoint']:
                     data[f'elo_{metric}'] = 1200.0
                     
                supabase.table('model_rankings').insert(data).execute()
                
        except Exception as e:
            logger.error(f"Ranking Update Error: {e}")

verification_service = VerificationService()
