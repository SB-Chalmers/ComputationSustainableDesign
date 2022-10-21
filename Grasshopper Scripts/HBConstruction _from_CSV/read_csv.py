"""Provides a scripting component.
    Inputs:
        path: The x script variable
        run: The y script variable
    Output:
        mat_out_: The a output variable"""

__author__ = "fojacob"
__version__ = "2022.10.14"

import rhinoscriptsyntax as rs
import csv

identifier = []

if run == True:
    #Open the file
    data = open(path)

    #CSV reader
    csv_data = csv.reader(data)

    #Reformat it into a python object List of lists
    data_lines = list(csv_data)

#    identifier = []
#    material = []

    for line in data_lines[0:]:
        identifier.append(line[0])
    #    material.append(line[1])
    

mat_out_ = identifier
#b = material