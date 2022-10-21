"""Provides a scripting component.
    Inputs:
        mat_in: The x script variable

    Output:
        insulation: The a output variable
        Board: The a output variable
        window: The a output variable"""

__author__ = "ssanjay"
__version__ = "2022.10.20"

import rhinoscriptsyntax as rs
# Make output list containers
mat,thk,cond,cost,embodied,density,u_value = [],[],[],[],[],[],[]
# Remove the header
mat_in = mat_in[1:]

insulation = []
board = []
window = []


# Searching through all the materials in DB
for mat in mat_in:
    if 'insulation' in mat:
        insulation.append(mat)
    elif 'Board' in mat:
        board.append(mat)
    elif 'window' in mat:
        window.append(mat)