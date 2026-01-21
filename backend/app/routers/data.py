from fastapi import APIRouter, HTTPException
from ..services.weather import weather_service

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/forecast")
async def get_forecast(lat: float, lon: float, model: str = "openmeteo"):
    data = await weather_service.get_forecast(lat, lon, model)
    if data is None:
        raise HTTPException(status_code=504, detail="Upstream service failed")
    return {"temperature": data, "unit": "C"}
