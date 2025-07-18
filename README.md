# 🔥 Wildfire Exposure for Alberta Pipeline Infrastructure

This project maps wildfire exposure along Alberta's pipeline infrastructure using 500m buffer zones and zonal statistics. It calculates the average historical wildfire frequency (1972–2024) for each pipeline segment, normalizes this value from 0 to 1, and produces a map for visualization.

---

## 📍 Key Features

- Buffers pipeline geometries by 500 meters
- Computes mean wildfire burn frequency per buffer zone
- Flags segments with any wildfire history (`burn_exposed = 1`)
- Normalizes burn values to allow gradient-based visualization
- Outputs:
  - GeoJSON with wildfire metrics
  - High-resolution PNG map for use in reports or posts

---
