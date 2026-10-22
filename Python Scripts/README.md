# Geospatial Python notebooks

Two small notebooks remain in this collection. Their code and original explanatory notes are preserved; their external services, dependencies and results were not revalidated during migration.

| Notebook | Purpose and required inputs |
| --- | --- |
| [Geocode Addresses to XYZ.ipynb](Geocode%20Addresses%20to%20XYZ.ipynb) | Geocode address rows with geocode.xyz, record latitude/longitude/confidence and create maps and geospatial exports. The example uses region `SE` and an API-key placeholder. Supply your own service credentials and review the input/output filenames before running. |
| [GeoJSON_to_xy.ipynb](GeoJSON_to_xy.ipynb) | Read polygon GeoJSON, reproject to EPSG:3006 and subtract a configured origin to print local XY coordinates for modelling. Supply the referenced `option_3.geojson` or update the input path and origin for your data. |

Both notebooks identify **Sanjay Somanath** in their original notes. Open them in a suitable Jupyter environment and review cells before execution. Package versions are not pinned: the geocoding notebook uses `requests`, `pandas`, `geopandas`, `matplotlib`, `contextily`, `folium` and `mapclassify`; the coordinate notebook uses `geopandas`, `pyproj` and `pandas`. Follow each notebook's imports and installation cells. TODO: document verified environments, external-service/data terms and a reproducible small input for each notebook.

The geocoding notebook's historical filename includes “XYZ”, but its documented geocoding outputs are latitude, longitude and confidence; an elevation output is not established. The GeoJSON example expects polygon exteriors and contains case-specific coordinate settings.

## Projects moved to their own repositories

| Former collection folder | Current repository |
| --- | --- |
| `radial_plot/` | [Radial Calendar Plot](https://github.com/SB-Chalmers/radial-calendar-plot): create radial calendar plots from time-series data with Python. |
| `Editing IDF files using python/` | [EnergyPlus Pressure Coefficient Tools](https://github.com/SB-Chalmers/energyplus-cp-tools): map CFD wind pressure coefficients to EnergyPlus AirflowNetwork models and run simulation workflows. |

Use each project's current README for installation, entry points and input provenance. Original source files and contributor metadata remain in this collection's Git history.

See the [collection catalogue](../) for all eight extracted repositories. Keep notebook issues in this collection and standalone project issues in their current repositories.
