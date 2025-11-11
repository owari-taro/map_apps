import rasterio
from pyproj import Transformer

# GeoTIFFを開く
path = "thumbnail.tif"
with rasterio.open(path) as src:
    bounds = src.bounds
    src_crs = src.crs

print("元のCRS:", src_crs)
print("元の範囲:", bounds)

# EPSG:4326（緯度経度）へ変換
transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)

xmin, ymin = transformer.transform(bounds.left, bounds.bottom)
xmax, ymax = transformer.transform(bounds.right, bounds.top)

print("EPSG:4326 の範囲:")
print(f"  xmin (lon): {xmin}")
print(f"  ymin (lat): {ymin}")
print(f"  xmax (lon): {xmax}")
print(f"  ymax (lat): {ymax}")