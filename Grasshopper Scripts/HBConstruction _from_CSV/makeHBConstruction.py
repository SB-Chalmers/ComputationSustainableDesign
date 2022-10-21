"""Provides a scripting component.
    Inputs:
        _solutions: The x script variable
    Output:
        HB_Constructions: The a output variable"""

__author__ = "ssanjay"
__version__ = "2022.10.21"
try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.materials import opaque_material_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
import rhinoscriptsyntax as rs
import ghpythonlib.treehelpers as th
_solution = th.tree_to_list(_solution)



HB_Constructions = []

for sol in _solution:
    _materials = []
    _name_ = []
    for layer in sol:
        prop = layer.split(';')
        identifier = prop[0]
        _name = clean_ep_string(prop[1])
        _thickness = prop[2]
        _conductivity = prop[3]
        cost = prop[4]
        embodied_Carbon = prop[5]
        _density = prop[6]
        u_value = prop[7]
        # Adding default assumptions
        _roughness_ = 'MediumRough'
        _therm_absp_ = 0.9
        _sol_absp_ = 0.7
        _vis_absp_ = 0.9
        # https://www.mrsphysics.co.uk/bge/wp-content/uploads/2016/07/thermal-properties-of-building-materials.pdf
        _spec_heat = 950
        # Creating the EnergyMaterial
        mat = EnergyMaterial(
        _name,
        _thickness,
        _conductivity,
        _density,
        _spec_heat,
        _roughness_,
        _therm_absp_,
        _sol_absp_,
        _vis_absp_)
        # Add EnergyMaterial to _materials
        _materials.append(mat)
        _name_.append(_name[0:3])
    # create the construction
    material_objs = []
    for material in _materials:
        if isinstance(material, str):
            material = opaque_material_by_identifier(material)
        material_objs.append(material)
    name = '_'.join(_name_)
    constr = OpaqueConstruction(name, material_objs)
    HB_Constructions.append(constr)