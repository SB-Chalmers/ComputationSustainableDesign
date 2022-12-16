# HB_DF_EnergyVariations
## A grasshopper script to conduct energy analysis of the existing context due to the new buildings

This script is based on the Rhino model which is later translated to the Dragonfly one. New buildings are treated as the context in order to understand their impact on energy usage within the existing buildings. Schematic parameters of openings within facades are additionally added and the model is further exported to Honeybee with the implementation of  HB IdealAir system. Prepared model is then exported to OpenStudioModel and based on the .sql file results of energy consumption are received and visualised through HB Color Rooms component.  

Date: 2022 December 12  
Author:   Dominika Komisarczyk
Contact:  domkom@chalmers.se

### Dependancies
this script makes use of  
* Ladybug tools version 1.5.0 (OpenStudio, DragonFly, HoneyBee)
* epw file for the location


![picture of the script](media/DF_HB_Energy_Variations.png)

![example of the obtained results](media/media.jpg)

the following parameters have been adopted:   
_floor_to_floor: @3
perim_offset: 0  
HB Building Programs: MediumOffice  
for constr_set: HB Climate Zones: 5-Cool    
DF Model to HB: 
_obj_per_model: deistrict
Use_multiplier: true (in order to simplify calculations)
