# Author: Sanjay Somanath
# Date created: 2023-09-01

# -------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------

import os                                           # For file and directory operations
import glob                                         # For file and directory operations
import pandas as pd                                 # For data manipulation  and analysis
from bs4 import BeautifulSoup                       # For parsing HTML files
from eppy.modeleditor import IDF                    # For working with IDF files
from eppy.runner.run_functions import runIDFs       # For running IDFs in parallel

# -------------------------------------------------------------------------------
# IDF Configuration and Running
# -------------------------------------------------------------------------------

def make_eplaunch_options(idf, output_dir):
    """
    Create the necessary options for the runIDFs function to make it behave like EPLaunch.
    
    Parameters:
    - idf: The IDF object to extract version details from.
    - output_dir: The desired directory for the simulation results.
    
    Returns:
    - Dictionary with options for runIDFs function.
    """
    # Extract version details from the IDF
    idfversion = idf.idfobjects['version'][0].Version_Identifier.split('.')
    idfversion.extend([0] * (3 - len(idfversion)))
    idfversionstr = '-'.join([str(item) for item in idfversion])
    fname = idf.idfname
    options = {
        'ep_version': idfversionstr,
        'output_prefix': os.path.basename(fname).split('.')[0],
        'output_suffix': 'C',
        'output_directory': output_dir,
        'readvars': True,
        'expandobjects': True
    }
    return options

def idf_file_generator(idf_dir):
    """
    A generator yielding paths to IDF files located in the specified directory.
    
    Parameters:
    - idf_dir: The directory containing the IDF files.
    
    Yields:
    - Full path to an IDF file.
    """
    for idf_file in os.listdir(idf_dir):
        if idf_file.endswith('.idf'):
            yield os.path.join(idf_dir, idf_file)

def modified_idf_run_generator(epwfile, idf_dir):
    """
    A generator yielding modified IDF objects and their respective run options.
    
    Parameters:
    - epwfile: The weather file for the simulation.
    - idf_dir: The directory containing the IDF files.
    
    Yields:
    - Tuple containing an IDF object and its associated run options.
    """
    for idf_file in idf_file_generator(idf_dir):
        idf = IDF(idf_file, epwfile)
        # Modify the IDF properties
        idf.idfobjects['TIMESTEP'][0].Number_of_Timesteps_per_Hour = 1
        idf.idfobjects['OUTPUTCONTROL:TABLE:STYLE'][0].Unit_Conversion = 'JtoKWH'
        idf_name = os.path.basename(idf_file).split('.')[0]
        
        yield (idf, make_eplaunch_options(idf, 'results/results_' + idf_name))

def lazy_run_IDF(num_CPUs=6, iddfile="Energy+_22_2_0.idd", 
                 epwfile='USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw', 
                 idf_dir='idf', results_dir='results', simulation_timestep=1):
    """
    Set up and run the IDFs in parallel based on the provided parameters.
    """
    # Set the IDD file
    IDF.setiddname(iddfile)
    
    # Generator for modified IDFs and their run options
    runs = list(modified_idf_run_generator(epwfile, idf_dir))  # Convert generator to list
    
    for i in range(len(runs)):
        idf, options = runs[i]
        
        # Modify the IDF properties for timestep
        idf.idfobjects['TIMESTEP'][0].Number_of_Timesteps_per_Hour = simulation_timestep
        
        # Modify the output directory based on provided results_dir
        options['output_directory'] = os.path.join(results_dir, f'results_{os.path.basename(idf.idfname).split(".")[0]}')
        
        runs[i] = (idf, options)  # Update the list item
    
    # if num_CPUs is "all", use all available CPUs
    if num_CPUs == "all":
        num_CPUs = os.cpu_count()

    # Run the simulations in parallel using the provided number of CPUs
    runIDFs(runs, num_CPUs)



# -------------------------------------------------------------------------------
# Result Parsing and Extraction
# -------------------------------------------------------------------------------

def extract_heating_value(htm_file, num_lines=200):
    """
    Extracts the heating value from the given HTML file.
    
    Parameters:
    - htm_file: Path to the HTML file.
    - num_lines: Number of lines to read from the file for performance reasons. Default is 200.
    
    Returns:
    - Tuple with the district heating demand and the total building area.
    """
    with open(htm_file, "r", encoding="utf-8") as file:
        content = ''.join([file.readline() for _ in range(num_lines)])

    soup = BeautifulSoup(content, "lxml")
    tables = soup.find_all("table")

    if len(tables) >= 4:
        end_uses_table = tables[3]
        building_area_table = tables[2]

        rows = building_area_table.find_all("tr")
        total_building_area = rows[1].find_all("td")[1].get_text().strip()

        rows = end_uses_table.find_all("tr")
        if len(rows) >= 2:
            district_heating_demand = rows[1].find_all("td")[12].get_text().strip()
            return district_heating_demand, total_building_area

    return None, None

def get_htm_files(results_dir):
    """
    Recursively find all .htm files within a directory.
    
    Parameters:
    - results_dir: The root directory to start the search.
    
    Returns:
    - List of paths to found .htm files.
    """
    return [os.path.join(root, file) for root, dirs, files in os.walk(results_dir) for file in files if file.endswith(".htm")]

def get_values(htm_files, verbose=False):
    """
    Extract district heating demand, total building area, and normalized heating demand from given htm files.
    
    Parameters:
    - htm_files: List of paths to .htm files.
    - verbose: Flag to print status messages. Default is False.
    
    Returns:
    - Dictionary with extracted values.
    """
    result_values = {}
    for htm_file in htm_files:
        path_parts = htm_file.split(os.path.sep)
        idf_name = path_parts[1].split("_")[1] if path_parts else ""
        if verbose:
            print(f"Processing {idf_name}")
        heating_value, building_area = extract_heating_value(htm_file)
        result_values[idf_name] = {
            'district_heating_demand_kwh': heating_value,
            'total_building_area_m2': building_area,
            'normalised_district_heating_demand_kwh_m2': float(heating_value) / float(building_area)
        }
    return result_values

def parse_results(results_dir):
    """
    Parse simulation results from a directory, convert to DataFrame, and save to a CSV file.
    
    Parameters:
    - results_dir: The directory containing the .htm result files.
    
    Returns:
    - DataFrame containing parsed results.
    """
    # Check if results directory exists
    if not os.path.isdir(results_dir):
        print(f"Directory {results_dir} does not exist!")
        return None
    htm_files = get_htm_files(results_dir)

    result_values = get_values(htm_files)
    df = pd.DataFrame.from_dict(result_values, orient='index').reset_index().rename(columns={'index':'idf_name'})
    df.to_csv('results.csv', index=False)
    print("Results saved to results.csv")
    return df

# -------------------------------------------------------------------------------
# Additional functions or modifications can be added below this line
# -------------------------------------------------------------------------------
