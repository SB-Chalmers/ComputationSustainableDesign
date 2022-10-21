"""Provides a scripting component.
    Inputs:
        _insulation: The x script variable
        _board: The y script variable
    Output:
        sol_combined: The a output variable"""

__author__ = "ssanjay"
__version__ = "2022.10.21"

import rhinoscriptsyntax as rs
import itertools
import ghpythonlib.treehelpers as th

solution_3 = [[i, j, k] for i in _board 
                 for j in _insulation
                 for k in _board]


solution_5 = [[i, j, k,l,m] for i in _board 
                 for j in _insulation
                 for k in _board
                 for l in _insulation
                 for m in _board]

sol_combined = solution_3+solution_5
solution_3 = th.list_to_tree(solution_3)
solution_5 = th.list_to_tree(solution_5)
sol_combined = th.list_to_tree(sol_combined)