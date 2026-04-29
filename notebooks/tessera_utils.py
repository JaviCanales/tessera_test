"""
Utility functions for mapping Planet tiles to overlapping Tessera tile centers.

Tessera tile convention:
  - Grid spacing: 0.1° x 0.1°
  - Centers at (n * 0.1 + 0.05, m * 0.1 + 0.05) for integers n, m
  - Name format: grid_{lon:.2f}_{lat:.2f}  (e.g. grid_0.15_52.05)
  - Each tile covers [center - 0.05, center + 0.05] in both lon and lat
"""

import rasterio
from pyproj import Transformer
import math

TESSERA_SIZE = 0.1
def get_tessera_center_from_bbox(lon_min, lat_min, lon_max, lat_max):
    s = TESSERA_SIZE
    eps = 1e-9

    n_min = math.floor(lon_min / s)
    n_max = math.floor((lon_max - eps) / s)

    m_min = math.floor(lat_min / s)
    m_max = math.floor((lat_max - eps) / s)

    centers = []
    for n in range(n_min, n_max + 1):
        for m in range(m_min, m_max + 1):
            lon_c = round(n * s + s / 2, 2)
            lat_c = round(m * s + s / 2, 2)
            centers.append((lon_c, lat_c))

    return centers

def get_tile_bbox(tile_path: str) -> tuple:
    """Get planet bbox."""
    with rasterio.open(tile_path) as src:
        bounds = src.bounds
        crs = src.crs
        if crs is None:
            raise ValueError(f"Planet tile has no CRS: {tile_path}")

        if crs.to_epsg() == 4326:
            return bounds.left, bounds.bottom, bounds.right, bounds.top

        transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        lon_min, lat_min = transformer.transform(bounds.left, bounds.bottom)
        lon_max, lat_max = transformer.transform(bounds.right, bounds.top)
        return lon_min, lat_min, lon_max, lat_max
