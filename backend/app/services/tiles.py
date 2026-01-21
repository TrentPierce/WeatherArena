import io
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cartopy.crs as ccrs
import math
from PIL import Image

class TileService:
    def __init__(self):
        pass

    def generate_tile(self, data: xr.DataArray, z: int, x: int, y: int, vmin: float = None, vmax: float = None) -> bytes:
        """
        Generate a PNG tile for the given Web Mercator tile coordinates.
        Uses matplotlib to render the data.
        """
        # Calculate bounds for the tile (Web Mercator)
        bounds = self.tile_bounds(x, y, z)
        
        # Setup plot
        fig = plt.figure(figsize=(2.56, 2.56), dpi=100)
        ax = plt.axes(projection=ccrs.Mercator())
        
        # Set extent to tile bounds
        ax.set_extent([bounds[0], bounds[2], bounds[1], bounds[3]], crs=ccrs.Mercator())
        
        # Plot data
        # Assuming data has lat/lon coordinates
        # We use pcolormesh for speed, or contourf for smoothness
        # transform=ccrs.PlateCarree() because GRIB data is usually LatLon
        
        # Determine min/max if not provided
        if vmin is None: vmin = float(data.min())
        if vmax is None: vmax = float(data.max())

        # Render
        # Note: Optimization needed here for production (reprojecting per tile is slow)
        # But for prototype, this works.
        im = data.plot.pcolormesh(
            ax=ax, 
            transform=ccrs.PlateCarree(),
            vmin=vmin, 
            vmax=vmax, 
            cmap='turbo',
            add_colorbar=False,
            add_labels=False
        )
        
        ax.axis('off')
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        
        # Resize to exactly 256x256 (bbox_inches='tight' might change size)
        # Using PIL to force 256x256
        image = Image.open(buf)
        image = image.resize((256, 256), Image.Resampling.LANCZOS)
        
        out_buf = io.BytesIO()
        image.save(out_buf, format='PNG')
        out_buf.seek(0)
        
        return out_buf.read()

    def tile_bounds(self, tx, ty, zoom):
        """
        Returns bounds of the given tile in EPSG:3857 coordinates
        Returns (minx, miny, maxx, maxy)
        """
        minx, maxy = self.pixels_to_meters(tx * 256, ty * 256, zoom)
        maxx, miny = self.pixels_to_meters((tx + 1) * 256, (ty + 1) * 256, zoom)
        return (minx, miny, maxx, maxy)

    def pixels_to_meters(self, px, py, zoom):
        """Converts pixel coordinates in given zoom level of pyramid to EPSG:3857"""
        res = (2 * math.pi * 6378137) / (256 * 2**zoom)
        origin_shift = 2 * math.pi * 6378137 / 2.0
        mx = px * res - origin_shift
        my = origin_shift - py * res
        return mx, my

tile_service = TileService()
