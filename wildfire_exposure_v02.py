#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wildfire Exposure Analysis for Alberta Pipeline Infrastructure
Version 0.2 – Chunked Zonal Stats for Performance (10k per batch)
Created on Jul 18, 2025
Author: Greg Williams
"""

from pathlib import Path
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches

# =============================================================================
# 0. PATHS
# =============================================================================

ROOT_DIR = Path("/home/gwilly/Documents/Data")
BASE_DIR = Path("/home/gwilly/Documents/LinkedIn/Wildfire Exposure")
OUTPUT_DIR = BASE_DIR / "Outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

pipeline_file = ROOT_DIR / "Alberta/AER/Pipelines_SHP/Pipelines_NAD83_10TM_AEPForest.shp"
prov_file     = ROOT_DIR / "Geo/Statistics Canada/Boundary/Prov/lpr_000b21a_e.shp"
fire_file     = ROOT_DIR / "NRCan/NBAC/NBAC_MRB_1972to2024_30m.tif"

# =============================================================================
# 1. LOAD AND PREPARE PIPELINE DATA
# =============================================================================

print("📦 Loading pipeline data...")
pipe = gpd.read_file(pipeline_file)

with rasterio.open(fire_file) as src:
    fire_crs = src.crs
    fire_bounds = src.bounds

pipe = pipe.to_crs(fire_crs)

# Clip to raster bounds (optional)
pipe = pipe.cx[fire_bounds.left:fire_bounds.right, fire_bounds.bottom:fire_bounds.top]
print(f"✅ Loaded and projected {len(pipe)} pipeline segments.")

# Buffer pipeline by 500m
print("🛡️ Buffering pipeline geometries by 500 meters...")
pipe["buffer_500m"] = pipe.geometry.buffer(500)
buffered = gpd.GeoDataFrame(pipe[["buffer_500m"]], geometry="buffer_500m", crs=pipe.crs)

# =============================================================================
# 2. CHUNKED ZONAL STATS
# =============================================================================

def run_chunked_zonal_stats(gdf, raster_path, chunk_size=10000, nodata=65535):
    all_stats = []
    total = len(gdf)

    print(f"🚀 Starting chunked zonal stats: {total} buffers in chunks of {chunk_size}")
    for start in range(0, total, chunk_size):
        end = min(start + chunk_size, total)
        chunk = gdf.iloc[start:end]
        print(f"🧩 Processing rows {start:,} to {end-1:,}...")

        stats = zonal_stats(
            vectors=chunk.geometry,
            raster=raster_path,
            stats=["mean", "min", "count", "nodata"],
            nodata=nodata,
            geojson_out=False
        )

        all_stats.extend(stats)

    return all_stats

print("🔥 Calculating wildfire exposure using zonal stats in 10k chunks...")
burn_stats = run_chunked_zonal_stats(buffered, fire_file)

buffered["burn_mean"] = [s["mean"] if s else None for s in burn_stats]
buffered["burn_exposed"] = [
    1 if s and s["min"] != 65535 and s["count"] > s.get("nodata", 0) else 0 for s in burn_stats
]

# =============================================================================
# 3. COMBINE WITH PIPE DATA AND NORMALIZE
# =============================================================================

pipe["burn_mean"] = buffered["burn_mean"]
pipe["burn_exposed"] = buffered["burn_exposed"]

pipe["burn_norm"] = (pipe["burn_mean"] - pipe["burn_mean"].min()) / \
                    (pipe["burn_mean"].max() - pipe["burn_mean"].min())

# =============================================================================
# 4. EXPORT GEOJSON
# =============================================================================

geojson_out = OUTPUT_DIR / "pipeline_wildfire_exposure_v02.geojson"
# Drop the buffer geometry column before saving
pipe = pipe.drop(columns="buffer_500m")
pipe.to_file(geojson_out, driver="GeoJSON")
print(f"✅ GeoJSON saved to: {geojson_out}")

# =============================================================================
# 5. PLOT FINAL MAP
# =============================================================================


print("🗺️ Creating exposure map...")

# Load and reproject Alberta boundary
prov = gpd.read_file(prov_file).to_crs(pipe.crs)
alberta = prov[prov["PRUID"] == "48"]

# Lambert Conformal Conic projection for Canada (EPSG:3347)
lcc_crs = "EPSG:3347"

# Reproject to LCC
pipe_lcc = pipe.to_crs(lcc_crs)
alberta_lcc = alberta.to_crs(lcc_crs)


fig, ax = plt.subplots(figsize=(14, 10))
alberta_lcc.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
pipe_lcc.plot(column="burn_norm", ax=ax, cmap="OrRd", linewidth=0.75, legend=False)

# Colorbar
sm = plt.cm.ScalarMappable(cmap="OrRd", norm=plt.Normalize(vmin=0, vmax=1))
cbar = fig.colorbar(sm, ax=ax, shrink=0.7)
cbar.set_label("Normalized Burn Exposure", fontsize=12)

# Title and styling
ax.set_title("Alberta Pipelines by Wildfire Exposure (2001–2023, LCC Projection)", fontsize=16)
ax.axis("off")

# Add scale bar (you can tweak the values slightly depending on the new units)
scalebar = AnchoredSizeBar(ax.transData,
                           100_000, '100 km', 'lower right',
                           pad=0.5, color='black', frameon=False,
                           size_vertical=1_000,
                           fontproperties=fm.FontProperties(size=10))
ax.add_artist(scalebar)

# North arrow
ax.text(0.97, 0.97, 'N', transform=ax.transAxes, fontsize=14, ha='center', va='center')
ax.annotate('', xy=(0.97, 0.93), xytext=(0.97, 0.87),
            arrowprops=dict(facecolor='black', width=2, headwidth=8),
            xycoords='axes fraction')

plt.tight_layout()

# Save
map_out = OUTPUT_DIR / "wildfire_pipeline_map_lcc.png"
plt.savefig(map_out, dpi=300)
print(f"🖼️ Map saved to: {map_out}")
plt.show()
