# A script to create HB materials and Component solutions from a CSV for parametric sensitivity analysis
![Script](media/script.png)

The script makes use of a helper csv file with the material properties and LCA/LCC Parameters.

The solutions are created using the Honeybee library.

Some assumtions are made within the script for all materials. 6,479 Solutions are created from the example CSV.

Sample HB material
```
Construction,
 Min_Pla,                  !- name
 Mineral_wool,             !- layer 1
 Plasterboard;             !- layer 2

```

```
Mineral_wool
MediumRough
0.1
0.038
300.0
950.0
0.9
0.7
0.9
Plasterboard
MediumRough
0.02
0.4
760.0
950.0
0.9
0.7
0.9

```

```
name
roughness
thickness {m}
conductivity {W/m-K}
density {kg/m3}
specific heat {J/kg-K}
thermal absorptance
solar absorptance
visible absorptance
name
roughness
thickness {m}
conductivity {W/m-K}
density {kg/m3}
specific heat {J/kg-K}
thermal absorptance
solar absorptance
visible absorptance

```