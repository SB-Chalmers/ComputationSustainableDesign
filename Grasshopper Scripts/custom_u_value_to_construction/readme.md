# Custom U-Value to Construction Script

This Grasshopper script is designed to create a simple wall construction with a specified U-value (thermal transmittance) for use in Honeybee energy simulations. The construction is composed of three layers: cladding (exterior), insulation (middle), and concrete (interior). The script calculates the required insulation thickness to achieve the desired U-value.

## Features
- Automatically calculates the required insulation thickness based on the desired U-value.
- Generates a Honeybee-compatible opaque construction object.
- Provides a detailed step-by-step explanation of the U-value calculation.

## Inputs
- **_u_value**: The desired overall U-value of the wall construction in W/m²K.
- **_name**: A custom name for the construction (optional).

## Outputs
- **constr**: A Honeybee opaque construction object that can be used in energy simulations.
- **calculation**: A text string detailing the step-by-step U-value calculation.

## How It Works
1. The script defines fixed properties for the cladding and concrete layers.
2. It calculates the thermal resistance of these fixed layers.
3. Based on the desired U-value, it determines the required total thermal resistance.
4. The script calculates the insulation resistance and thickness needed to meet the total resistance.
5. It creates Honeybee `EnergyMaterial` objects for each layer and assembles them into an `OpaqueConstruction`.

## Example
If you specify a U-value of 0.25 W/m²K and name the construction "MyWall", the script will:
- Calculate the required insulation thickness.
- Create a construction named "WallConstruction_MyWall".
- Output a detailed calculation showing how the U-value was achieved.

## Requirements
- Honeybee and Ladybug libraries must be installed.
- Grasshopper environment for running the script.

