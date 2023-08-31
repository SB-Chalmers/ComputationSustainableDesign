import os
import time
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs
from tqdm.notebook import tqdm  # Note the change here for Jupyter

def make_eplaunch_options(idf):

    idfversion = idf.idfobjects['version'][0].Version_Identifier.split('.')
    idfversion.extend([0] * (3 - len(idfversion)))
    idfversionstr = '-'.join([str(item) for item in idfversion])
    fname = idf.idfname
    options = {
        'ep_version': idfversionstr,
        'output_prefix': os.path.basename(fname).split('.')[0],
        'output_suffix': 'C',
        'output_directory': os.path.dirname(fname),
        'readvars': True,
        'expandobjects': True
    }
    return options

def main():
    iddfile = "Energy+_22_2_0.idd"
    IDF.setiddname(iddfile)
    epwfile = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

    idf_dir = 'idf'
    idf_files = [os.path.join(idf_dir, f) for f in os.listdir(idf_dir) if f.endswith('.idf')]
    runs = []

    for idfname in idf_files:
        print(f"Processing {idfname}")
        idf = IDF(idfname, epwfile)
        theoptions = make_eplaunch_options(idf)
        runs.append([idf, theoptions])

    # Use all available CPUs
    num_CPUs = 4

    runIDFs(runs, num_CPUs)

if __name__ == '__main__':
    main()

# This took 7m and 45.2 seconds for 4 idf files on a 4-core machine