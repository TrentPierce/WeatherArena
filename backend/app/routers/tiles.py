from fastapi import APIRouter, HTTPException, Response
from ..services.weather import weather_service
from ..services.tiles import tile_service

router = APIRouter(prefix="/tiles", tags=["tiles"])

@router.get("/{model}/{z}/{x}/{y}.png")
async def get_tile(model: str, z: int, x: int, y: int):
    """
    Get a PNG tile for a specific model layer (Temperature 2m).
    """
    # 1. Get the dataset
    ds = await weather_service.get_model_grid(model)
    if ds is None:
        # Return transparent tile or 404
        raise HTTPException(status_code=404, detail="Model data not found")

    # 2. Extract variable (assuming 't2m' or 't')
    # This logic needs to be robust to different variable names from GRIB
    var = None
    for v in ['t2m', 't', 'tmp', '2t']:
        if v in ds:
            var = ds[v]
            break
            
    if var is None:
         # Fallback to first variable
        var = ds[list(ds.data_vars)[0]]

    # 3. Generate Tile
    try:
        # Convert Kelvin to Celsius for visualization if mean is high
        if var.mean() > 200:
            var = var - 273.15
            
        img_bytes = tile_service.generate_tile(var, z, x, y, vmin=-10, vmax=40)
        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        print(f"Tile Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Tile generation failed")
