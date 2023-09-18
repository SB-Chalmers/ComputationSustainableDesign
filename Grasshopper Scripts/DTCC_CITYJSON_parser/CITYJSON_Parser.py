import Rhino
import Rhino.Geometry as rg
import json
import ghpythonlib.treehelpers as th
def should_cull(value, criterion):
    """
    Determine if a value should be culled based on the criterion.
    criterion: string in format '>100' or '<100'
    """
    if not criterion:
        return False
    operation = criterion[0]
    threshold = float(criterion[1:])
    if operation == '>':
        return value > threshold
    elif operation == '<':
        return value < threshold
    return False
if _run:
    with open(CityModel, 'r') as file:
        data = json.load(file)

    # Extract bounds
    xmin = data['bounds']['xmin']
    ymin = data['bounds']['ymin']

    footprints = []
    heights = []
    buildings = []
    culled_buildings = []
    # Loop through buildings in the data
    for building in data['buildings']:
        points = []

        z = building['groundHeight']
        
        height = building['height']

        # Extract footprint points and subtract xmin and ymin from x and y respectively
        for vertex in building['footprint']['shell']['vertices']:
            x = vertex['x'] - xmin
            y = vertex['y'] - ymin
            points.append(rg.Point3d(x, y, z))


        # Create the building in Rhino
        polyline = rg.PolylineCurve(points)

        # Ensure the polyline is closed
        if not polyline.IsClosed:
            polyline.MakeClosed(0.01)  # 0.01 is a small tolerance value
        footprints.append(polyline)
        vector = rg.Vector3d(0, 0, height)
        extrusion = rg.Extrusion.Create(polyline, height, True)

        if extrusion:
            brep = extrusion.ToBrep()
            area = rg.AreaMassProperties.Compute(brep).Area
            volume = rg.VolumeMassProperties.Compute(brep).Volume
            # Append the building and its details to their respective lists
            footprints.append(polyline)
            heights.append(height)
        if (should_cull(area, cull_area) or 
            should_cull(volume, cull_volume) or 
            should_cull(height, cull_height)):
            culled_buildings.append(brep)
        else:
            buildings.append(brep)
    origin = rg.Point3d(xmin, ymin, 0)
