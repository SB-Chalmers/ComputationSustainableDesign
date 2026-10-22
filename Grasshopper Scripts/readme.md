# Grasshopper examples

Four small analysis examples remain in this collection. Open their individual READMEs for the original workflow and dependencies; the migration has not revalidated the binary definitions or their results.

| Example | Purpose | Grasshopper entry file |
| --- | --- | --- |
| [HB / Dragonfly Energy Variations](HB_DF_EnergyVariations/readme.md) | Compare energy use in existing buildings when new buildings are added as context. | [DF_HB_Energy_Variations.gh](HB_DF_EnergyVariations/DF_HB_Energy_Variations.gh) |
| [LB MRT / UTCI](LB_MRT_UTCI/readme.md) | Compare outdoor thermal comfort between baseline and added-building scenarios on the coldest and warmest days. | [LB_MRT_UTCI.gh](LB_MRT_UTCI/LB_MRT_UTCI.gh) |
| [LB Radiation](LB_Radiation/readme.md) | Compare incident radiation in the surroundings of proposed buildings. | [LB_radiation.gh](LB_Radiation/LB_radiation.gh) |
| [Outdoor Thermal Comfort](Outdoor_thermal_comfort/README.md) | Calculate MRT and UTCI for a single point from a context mesh and EPW file. | [MRT-UTCI.gh](Outdoor_thermal_comfort/MRT-UTCI.gh) |

The first three examples document Ladybug Tools **1.5.0** and a location-specific EPW input. They also require an appropriate Rhino context model. The single-point example does not record exact software versions. TODO: supply verified minimal examples, complete input provenance and compatible environments before treating these workflows as independently reproduced.

## Projects moved to their own repositories

| Former collection folder | Current repository |
| --- | --- |
| `PVGIS_API/` | [PVGIS for Grasshopper](https://github.com/SB-Chalmers/grasshopper-pvgis) |
| `DecarbonAIte_LCA_LCC_Optimizer/` | [DecarbonAIte](https://github.com/SB-Chalmers/decarbonaite) |
| `ACE405_bps_lca_script/` | [ACE405 Building Analysis](https://github.com/SB-Chalmers/ace405-building-analysis) |
| `HBConstruction _from_CSV/` and `custom_u_value_to_construction/` | [Honeybee Construction Tools](https://github.com/SB-Chalmers/honeybee-construction-tools), grouped as `csv-constructions/` and `target-u-value/` |
| `DTCC_CITYJSON_parser/` and `DTCC_WindComfort_Parser/` | [DTCC Grasshopper Tools](https://github.com/SB-Chalmers/dtcc-grasshopper), grouped as `citymodel/` and `wind-comfort/` |

The DTCC geometry parser specifically targets its documented DTCC CityModel schema; general CityJSON support has not been established. The original source folders and author metadata remain in Git history.

See the [collection catalogue](../) for all eight extracted projects, including the Python tools and multidomain viewer. Report example-specific issues in this collection, and standalone project issues in their current repositories.
