"""
Create a simple wall construction with a given U-value (W/m²K) and name.
The construction is composed of three layers:
    - Cladding (exterior)
    - Insulation (middle, e.g., rockwool; thickness is calculated)
    - Concrete (interior)
The script calculates the required insulation thickness such that:
    U = 1 / (R_cladding + R_insulation + R_concrete)
It also outputs a step-by-step explanation of the U-value calculation.

Inputs:
    _u_value: Desired overall U-value [W/m²K].
    _name: Name for the construction.

Outputs:
    constr: An opaque construction for Honeybee.
    calculation: A text string showing the step-by-step U-value calculation.
"""

ghenv.Component.Name = "HB Simple Wall U-value Construction"
ghenv.Component.NickName = "SimpleWallU"
ghenv.Component.Message = "v1.1"
ghenv.Component.Category = "HB-Energy"
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

# Import required modules from Honeybee and Ladybug
try:
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component):
    # ----- Fixed material properties -----
    # Concrete (interior layer)
    thickness_conc = 0.2  # [m]
    conductivity_conc = 1.95  # [W/m-K]
    density_conc = 2300  # [kg/m³]
    spec_heat_conc = 900  # [J/kg-K]

    # Cladding (exterior layer)
    thickness_clad = 0.02  # [m]
    conductivity_clad = 1.0  # [W/m-K]
    density_clad = 1800  # [kg/m³]
    spec_heat_clad = 1000  # [J/kg-K]

    # Insulation (middle layer, e.g., rockwool)
    conductivity_insul = 0.04  # [W/m-K]
    density_insul = 100  # [kg/m³]
    spec_heat_insul = 1000  # [J/kg-K]

    # Default surface properties (applied uniformly)
    roughness = 'MediumRough'
    therm_absp = 0.9
    sol_absp = 0.7
    vis_absp = sol_absp

    # ----- Calculate fixed layer resistances -----
    R_conc = thickness_conc / conductivity_conc  # Concrete resistance [m²K/W]
    R_clad = thickness_clad / conductivity_clad  # Cladding resistance [m²K/W]
    R_fixed = R_conc + R_clad

    # ----- Desired total resistance from U-value -----
    R_total_desired = 1.0 / _u_value  # [m²K/W]

    if R_total_desired <= R_fixed:
        raise ValueError("Desired U-value is too high for the fixed layers. "
                         "Please specify a lower U-value (i.e., higher insulation performance).")

    # ----- Calculate required insulation layer -----
    R_insul = R_total_desired - R_fixed
    thickness_insul = R_insul * conductivity_insul

    # ----- Create material names -----
    conc_name = clean_and_id_ep_string("Concrete_" + _name_) if _name_ is not None else clean_and_id_ep_string(
        "Concrete")
    insul_name = clean_and_id_ep_string("Insulation_" + _name_) if _name_ is not None else clean_and_id_ep_string(
        "Insulation")
    clad_name = clean_and_id_ep_string("Cladding_" + _name_) if _name_ is not None else clean_and_id_ep_string(
        "Cladding")
    constr_name = clean_and_id_ep_string(
        "WallConstruction_" + _name_) if _name_ is not None else clean_and_id_ep_string("WallConstruction")

    # ----- Create materials using EnergyMaterial -----
    concrete_mat = EnergyMaterial(conc_name, thickness_conc, conductivity_conc, density_conc, spec_heat_conc,
                                  roughness, therm_absp, sol_absp, vis_absp)
    insulation_mat = EnergyMaterial(insul_name, thickness_insul, conductivity_insul, density_insul, spec_heat_insul,
                                    roughness, therm_absp, sol_absp, vis_absp)
    cladding_mat = EnergyMaterial(clad_name, thickness_clad, conductivity_clad, density_clad, spec_heat_clad,
                                  roughness, therm_absp, sol_absp, vis_absp)

    # ----- Assemble the construction (exterior to interior) -----
    materials_list = [cladding_mat, insulation_mat, concrete_mat]
    constr = OpaqueConstruction(constr_name, materials_list)
    constr.display_name = _name_ if _name_ is not None else constr_name

    # ----- Build the step-by-step calculation explanation -----
    calculation = ""
    calculation += "Step-by-step U-value Calculation:\n"
    calculation += "1. Provided U-value: {0:.3f} W/m²K\n".format(_u_value)
    calculation += "2. Concrete layer: thickness = {0:.3f} m, conductivity = {1:.3f} W/m-K, so R_concrete = {0:.3f} / {1:.3f} = {2:.3f} m²K/W\n".format(
        thickness_conc, conductivity_conc, R_conc)
    calculation += "3. Cladding layer: thickness = {0:.3f} m, conductivity = {1:.3f} W/m-K, so R_cladding = {0:.3f} / {1:.3f} = {2:.3f} m²K/W\n".format(
        thickness_clad, conductivity_clad, R_clad)
    calculation += "4. Fixed resistance: R_fixed = R_concrete + R_cladding = {0:.3f} + {1:.3f} = {2:.3f} m²K/W\n".format(
        R_conc, R_clad, R_fixed)
    calculation += "5. Desired total resistance: R_total = 1 / U = 1 / {0:.3f} = {1:.3f} m²K/W\n".format(_u_value,
                                                                                                         R_total_desired)
    calculation += "6. Required insulation resistance: R_insulation = R_total - R_fixed = {0:.3f} - {1:.3f} = {2:.3f} m²K/W\n".format(
        R_total_desired, R_fixed, R_insul)
    calculation += "7. Insulation layer: conductivity = {0:.3f} W/m-K, so thickness = R_insulation * conductivity = {1:.3f} * {0:.3f} = {2:.3f} m\n".format(
        conductivity_insul, R_insul, thickness_insul)
