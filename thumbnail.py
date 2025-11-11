import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os
import numpy as np
from PIL import Image

def create_tiles(input_tiff, output_dir, zoom_levels=(8, 12)):
    """
    Convert a TIFF file to web tiles for use with Leaflet
    
    Args:
        input_tiff (str): Path to input TIFF file
        output_dir (str): Directory to save tiles
        zoom_levels (tuple): Min and max zoom levels to generate
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    with rasterio.open(input_tiff) as src:
        # Reproject to Web Mercator (EPSG:3857)
        transform, width, height = calculate_default_transform(
            src.crs, 'EPSG:3857', src.width, src.height, *src.bounds)
        
        # Read and reproject the data
        data = src.read()
        data = np.moveaxis(data, 0, -1)  # Change from (bands, height, width) to (height, width, bands)
        
        # Convert to 8-bit RGB if necessary
        if data.dtype != np.uint8:
            data = ((data - data.min()) * (255 / (data.max() - data.min()))).astype(np.uint8)
        
        img = Image.fromarray(data)
        
        # Generate tiles for each zoom level
        for z in range(zoom_levels[0], zoom_levels[1] + 1):
            # Calculate tile coordinates
            n_tiles = 2 ** z
            tile_size = 256
            
            for x in range(n_tiles):
                for y in range(n_tiles):
                    # Create directories for this zoom level and x coordinate
                    tile_dir = os.path.join(output_dir, str(z), str(x))
                    os.makedirs(tile_dir, exist_ok=True)
                    
                    # Calculate pixel coordinates for this tile
                    x_pixel = x * tile_size
                    y_pixel = y * tile_size
                    
                    # Extract and save tile
                    tile = img.crop((x_pixel, y_pixel, 
                                   x_pixel + tile_size, 
                                   y_pixel + tile_size))
                    
                    tile.save(os.path.join(tile_dir, f"{y}.png"))

if __name__ == "__main__":
    # Example usage
    create_tiles("data/thumbnail.tif", "data/tiles", zoom_levels=(8, 12))
