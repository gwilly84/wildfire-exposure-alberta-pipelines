# 🔥 Wildfire Exposure for Alberta Pipeline Infrastructure

This project maps wildfire exposure along Alberta's pipeline network using buffer zones and historical wildfire burn frequency data. Each pipeline segment is evaluated based on fire activity from 1972 to 2024, then visualized using a normalized color gradient.

---

## 📦 Data Sources

This project uses publicly available geospatial data from Canadian government sources:

- **Pipelines**  
  Source: Alberta Energy Regulator (AER)  
  File: `Pipelines_NAD83_10TM_AEPForest.shp`  
  [https://www.aer.ca/data-and-performance-reports/activity-and-data/spatial-data](https://www.aer.ca/data-and-performance-reports/activity-and-data/spatial-data)

- **Wildfire Burn Frequency Raster (1972–2024)**  
  Source: Natural Resources Canada (NRCan)  
  File: `NBAC_MRB_1972to2024_30m.tif`  
  [https://cwfis.cfs.nrcan.gc.ca/datamart](https://cwfis.cfs.nrcan.gc.ca/datamart)

- **Alberta Boundary Shapefile**  
  Source: Statistics Canada – Boundary Files  
  File: `lpr_000b21a_e.shp`  
  [https://www150.statcan.gc.ca/n1/en/catalogue/92-160-X](https://www150.statcan.gc.ca/n1/en/catalogue/92-160-X)

---

## 🚀 What This Script Does (v0.2)

- Buffers pipeline geometries by 500 meters
- Uses **chunked zonal statistics** (10,000 rows per batch) for wildfire raster overlay
- Calculates:
  - `burn_mean`: average wildfire frequency per segment
  - `burn_exposed`: binary flag if ever burned
  - `burn_norm`: normalized 0–1 wildfire exposure
- Outputs:
  - A `.geojson` file with attributes
  - A `.png` map for visualization

*Note: this version processes large datasets in ~8 hours depending on your machine.*

---

## ⚙️ How to Recreate This

### 1. Install dependencies

```bash
pip install geopandas rasterio rasterstats matplotlib
```

### 2. Prepare your files

Organize the files using this structure:

```
/your/project/
├── wildfire_exposure_v01.py
├── Outputs/
├── Data/
│ ├── Alberta/AER/Pipelines_SHP/
│ ├── NRCan/NBAC/
│ └── Geo/Statistics Canada/Boundary/Prov/
│ └── lpr_000b21a_e.shp
```

Ensure the following files are present:

- `Pipelines_NAD83_10TM_AEPForest.shp`
- `NBAC_MRB_1972to2024_30m.tif`
- `lpr_000b21a_e.shp`


### 3. Set paths in the script

At the top of wildfire_exposure_v01.py, point to your directories:
```
ROOT_DIR = Path("/your/project/Data")
BASE_DIR = Path("/your/project")
OUTPUT_DIR = BASE_DIR / "Outputs"
```
### 4. Run the script

python wildfire_exposure_v02.py

This generates

- `pipeline_wildfire_exposure.geojson`
- `wildfire_pipeline_map.png`

🧠 Want to Help?

If you're a GIS or Python performance nerd, I'd love to hear your tips for optimizing large-scale zonal stats workflows. This script averages ~15 minutes per chunk. Suggestions welcome!


📄 License

MIT License — see LICENSE for details.


