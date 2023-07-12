import csv
import json
from honeybee_energy.material.opaque import EnergyMaterial
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee_energy.lib.materials import opaque_material_by_identifier
from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.lib.materials import window_material_by_identifier
from honeybee.typing import clean_and_id_ep_string, clean_ep_string

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.materials import opaque_material_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def read_csv_file(file_path):
    with open(file_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile.read().decode('utf-8-sig').splitlines())
        data = [row for row in reader]
    return data

def process_mat_data(mat_data):
    result = {row['UUID']: row for row in mat_data}
    return result

def process_cons_data(cons_data):
    result = {}
    for row in cons_data:
        element = row['Element']
        identifier = row['Identifier']
        layer_id = row['Layer']
        uuid = row['UUID']
        cons = element + '_' + identifier

        if cons not in result:
            result[cons] = {
                'Element': element,
                'Identifier': identifier,
                'Layer': []
            }

        result[cons]['Layer'].append({
            'layer_id': layer_id,
            'UUID': uuid
        })

    return result

mat_data = read_csv_file(mat_DB)
cons_data = read_csv_file(cons_DB)

mat_data = process_mat_data(mat_data)
cons_data = process_cons_data(cons_data)
cons_data = {k.replace('_', ' '): v for k, v in cons_data.items()}

#from honeybee_energy.lib.constructions import opaque_construction_by_identifier
#base_Wall = opaque_construction_by_identifier(base_Wall)
#base_Floor = opaque_construction_by_identifier(base_Floor)
#base_Roof = opaque_construction_by_identifier(base_Roof)
#from honeybee_energy.lib.constructions import window_construction_by_identifier
#base_Window = window_construction_by_identifier(base_Window)

HB_Walls = [base_Wall]
HB_Floors = [base_Floor]
HB_Roofs = [base_Roof]
HB_Windows = [base_Window]


for construction in cons_data:
    if 'Wall' in construction:
        _materials = list(base_Wall.materials)
        for layer_info in cons_data[construction]['Layer']:
            layer = mat_data[layer_info['UUID']]
            _name_ = layer['Material']
            name = clean_and_id_ep_string('OpaqueMaterial') if _name_ is None else \
                clean_ep_string(_name_)
            mat = EnergyMaterial(
                name,
                float(layer['Thickness']),
                float(layer['Conductivity']),
                float(layer['Density']),
                950,  # _spec_heat
                'MediumRough',  # _roughness_
                0.9,  # _therm_absp_
                0.7,  # _sol_absp_
                0.9  # _vis_absp_
            )
            _materials.append(mat)
        material_objs = [opaque_material_by_identifier(mat) if isinstance(mat, str) else mat for mat in _materials]
        print construction
        name = clean_and_id_ep_string('OpaqueConstruction') if construction is None else \
            clean_ep_string(construction)
        print name
        constr = OpaqueConstruction(name, material_objs)
        constr.display_name = construction
        HB_Walls.append(constr)


    if 'Floor' in construction:
        _materials = list(base_Floor.materials)
        for layer_info in cons_data[construction]['Layer']:
            layer = mat_data[layer_info['UUID']]
            mat = EnergyMaterial(
                layer['Material'],
                float(layer['Thickness']),
                float(layer['Conductivity']),
                float(layer['Density']),
                950,  # _spec_heat
                'MediumRough',  # _roughness_
                0.9,  # _therm_absp_
                0.7,  # _sol_absp_
                0.9  # _vis_absp_
            )
            _materials.append(mat)
        material_objs = [opaque_material_by_identifier(mat) if isinstance(mat, str) else mat for mat in _materials]
        constr = OpaqueConstruction(construction, material_objs)
        HB_Floors.append(constr)

    if 'Roof' in construction:
        _materials = list(base_Roof.materials)
        for layer_info in cons_data[construction]['Layer']:
            layer = mat_data[layer_info['UUID']]
            mat = EnergyMaterial(
                layer['Material'],
                float(layer['Thickness']),
                float(layer['Conductivity']),
                float(layer['Density']),
                950,  # _spec_heat
                'MediumRough',  # _roughness_
                0.9,  # _therm_absp_
                0.7,  # _sol_absp_
                0.9  # _vis_absp_
            )
            _materials.append(mat)
        material_objs = [opaque_material_by_identifier(mat) if isinstance(mat, str) else mat for mat in _materials]
        constr = OpaqueConstruction(construction, material_objs)
        HB_Roofs.append(constr)


    if 'Window' in construction:
        _materials = []
        for layer_info in cons_data[construction]['Layer']:
            layer = mat_data[layer_info['UUID']]
            mat = EnergyWindowMaterialSimpleGlazSys(
                layer['Material'],
                float(layer['U-value']),
                0.3,    #shgc
                0.6     #t_vis
            )
            _materials.append(mat)
        material_objs = [window_material_by_identifier(mat) if isinstance(mat, str) else mat for mat in _materials]
        constr = WindowConstruction(construction, material_objs)
        HB_Windows.append(constr)