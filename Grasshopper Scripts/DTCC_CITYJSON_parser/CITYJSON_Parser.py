"""Provides a scripting component.
    Inputs:
        CityModel: The x script variable
        run: The y script variable
    Output:
        buildings: The a output variable"""

__author__ = "ssanjay"
__version__ = "2022.10.21"

import rhinoscriptsyntax as rs
import ghpythonlib.treehelpers as th
import json
import Rhino as rh
if _run:
    with open(CityModel) as file:
        data = json.load(file)
    buildings = []
    for building in data['Buildings']:
        points = []
        z = building['GroundHeight']
        height = building['Height']
        for point in building['Footprint']:
            x = point['x']
            y = point['y']
            points.append(rs.AddPoint(x,y,z))
    
        polyline = rs.AddPolyline(points+[points[0]])
        path = rs.AddLine([0,0,0], [0,0,height])
        extrusion = rs.ExtrudeCurve(polyline,path)
        brep = rs.CapPlanarHoles(extrusion)
        buildings.append(extrusion)


buildings = th.list_to_tree(buildings)