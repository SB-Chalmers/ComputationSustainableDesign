# Imports
from eppy import modeleditor
from eppy.modeleditor import IDF
import plotly.graph_objects as go
import pandas as pd
from scipy.spatial import cKDTree
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('Adding CP Values to IDF')

# Constants
IDF_PATH = 'data/in.idf'
IDD_PATH = 'idd/Energy+_22_2_0.idd'
CP_PATH = 'data/Cp.csv'

def path_checker(IDF_PATH, IDD_PATH, CP_PATH):
    """Checks if the paths are valid"""
    logger.info('Checking paths')
    # If any of the paths are invalid, raise an error and exit the program
    if not os.path.exists(IDF_PATH):
        raise FileNotFoundError(f'IDF file not found at {IDF_PATH}')
    if not os.path.exists(IDD_PATH):
        raise FileNotFoundError(f'IDD file not found at {IDD_PATH}')
    if not os.path.exists(CP_PATH):
        raise FileNotFoundError(f'Cp file not found at {CP_PATH}')
    logger.info('All paths are valid')

def update_idf_params(idf1):
    """Updates the IDF file to use JtoKWH and HTML as the column separator"""
    logger.info('Updating IDF to use JtoKWH')
    idf1.idfobjects["OUTPUT:SQLITE"][0].Unit_Conversion_for_Tabular_Data = "JtoKWH"
    idf1.idfobjects["OUTPUTCONTROL:TABLE:STYLE"][0].Column_Separator = "HTML"
    idf1.idfobjects["OUTPUTCONTROL:TABLE:STYLE"][0].Unit_Conversion = "JtoKWH"
    # Set Plant Sizing calculation to No
    idf1.idfobjects['SimulationControl'][0].Do_Plant_Sizing_Calculation = 'No'
    # Save the IDF file
    logger.info('Saving original IDF file')
    idf1.save()

def add_wind_pressure_coefficients_array(idf1):
    """Adds the wind pressure coefficients array to the IDF file"""
    logger.info('Adding wind pressure coefficients array')
    # Define wind pressure coefficients array
    wind_pressure_coefficient_array = idf1.newidfobject("AirflowNetwork:MultiZone:WindPressureCoefficientArray",
                                Name="Cp Data",
                                Wind_Direction_1 = 0,
                                Wind_Direction_2 = 45,
                                Wind_Direction_3 = 90,
                                Wind_Direction_4 = 135,
                                Wind_Direction_5 = 180,
                                Wind_Direction_6 = 225,
                                Wind_Direction_7 = 270,
                                Wind_Direction_8 = 315)
    return wind_pressure_coefficient_array
    
def vectorize_points(cp_path = CP_PATH, x_trans = None, y_trans = None, z_trans = None):
    """Vectorizes the points from the Cp.csv file"""
    logger.info(f'Vectorizing points from {cp_path}')
    cp_data = pd.read_csv(cp_path)
    cp_data.head()

    # Fix cp csv
    coords_df = cp_data[cp_data['angle'] == 0][['u_ref', 'x', 'y', 'z']]
    cp_list = []
    for angles in cp_data['angle'].unique():
        cp_list.append(cp_data[cp_data['angle'] == angles]['c_p'].tolist())

    # add the cp_list to the coords_df with the column name 'c_p_<angle>'
    for i, angles in enumerate(cp_data['angle'].unique()):
        coords_df['c_p_{}'.format(angles)] = cp_list[i]
    # Extract just the xyz for cp0
    xyz_df = coords_df[['x', 'y', 'z','c_p_0']]
    sampled_df = coords_df[['x', 'y', 'z','c_p_0']].copy()

    logger.info('Translating points')
    # Define translation values to align the two dataframes
    x_trans = 851.9646-101.854
    y_trans = 883.6051+16.43799
    z_trans = 69.24877-72.39

    # Fine tuning
    point_A = (920.479730342372, 936.878514625527, 58.3200021362305)
    point_B = (920.59058, 936.92212, 58.17876999999999)

    # Add translate values to the sampled_df
    sampled_df['x'] += x_trans + point_B[0] - point_A[0]
    sampled_df['y'] += y_trans + point_B[1] - point_A[1]
    sampled_df['z'] += z_trans + point_B[2] - point_A[2]

    # Convert DataFrame to a NumPy array
    coords_array = coords_df[['x', 'y', 'z']].to_numpy()
    logger.info('Building KDTree')
    # Build a KDTree for faster nearest-neighbor search
    kdtree = cKDTree(coords_array)
    return kdtree, coords_df

def get_cp(surface, kdtree, coords_df, threshold=None):   
    vertices = surface.coords    
    # Find closest points in the KDTree
    distances, indices = kdtree.query(vertices, k=1)
    # Check if any distance exceeds the threshold
    if threshold and np.any(distances > threshold):
        return [-9999] * 8
    # Use the indices to fetch the required rows from the original DataFrame
    closest_rows = coords_df.iloc[indices]
    cp_columns = ['c_p_0', 'c_p_45', 'c_p_90', 'c_p_135', 'c_p_180', 'c_p_225', 'c_p_270', 'c_p_315']
    avg_cp = closest_rows[cp_columns].mean().tolist()
    return avg_cp

def fetch_surfaces(idf1):# Sample cp values
    logger.info('Fetching surfaces')
    building_objects = idf1.idfobjects['BUILDINGSURFACE:DETAILED']
    fenestration_objects = idf1.idfobjects['FENESTRATIONSURFACE:DETAILED']
    return building_objects, fenestration_objects



def plot_fenestration(fenestration_objects):
    # Extract coordinates using the surface.coords() method
    points = [coord for surface in fenestration_objects for coord in surface.coords]
    points_array = np.array(points)

    fig = go.Figure()

    # Scatter3D from sampled_df
    fig.add_trace(go.Scatter3d(
        x=sampled_df['x'], y=sampled_df['y'], z=sampled_df['z'],
        mode='markers',
        marker=dict(size=2, color='red')
    ))

    # Scatter3D from points_array
    fig.add_trace(go.Scatter3d(
        x=points_array[:,0], y=points_array[:,1], z=points_array[:,2],
        mode='markers',
        marker=dict(size=2, color='blue')
    ))

    fig.update_layout(scene=dict(
        xaxis_title="X", 
        yaxis_title="Y", 
        zaxis_title="Z", zaxis_range=[-50,250])
    )

    fig.show()


def add_cp_fenestration(idf1, fenestration_objects,wind_pressure_coefficient_array, kdtree, coords_df):
    node_height = 6.5 # Placeholder
    opening_array = []
    null_cp_counter = 0
    logger.info('Adding CP for fenestration')
    for i, surface in enumerate(fenestration_objects):
        if surface.View_Factor_to_Ground!=0:
            #print(f'Adding wind pressure coefficients for {surface.Name}')
            CP_values = get_cp(surface,kdtree=kdtree, coords_df=coords_df)
            
            # Count the number of times the CP_values is -9999
            if CP_values == [-9999] * 8:
                null_cp_counter += 1

            print(f'Number of fenestrations processed: {i+1}/{len(fenestration_objects)}, Number of null CP values: {null_cp_counter}', end='\r')
            #print(f'Adding wind pressure coefficients for {surface.Name}')
            idf1.newidfobject("AirflowNetwork:MultiZone:WindPressureCoefficientValues",
                            Name=surface.Name,
                            AirflowNetworkMultiZoneWindPressureCoefficientArray_Name = wind_pressure_coefficient_array.Name,
                            Wind_Pressure_Coefficient_Value_1 = CP_values[0],
                            Wind_Pressure_Coefficient_Value_2 = CP_values[1],
                            Wind_Pressure_Coefficient_Value_3 = CP_values[2],
                            Wind_Pressure_Coefficient_Value_4 = CP_values[3],
                            Wind_Pressure_Coefficient_Value_5 = CP_values[4],
                            Wind_Pressure_Coefficient_Value_6 = CP_values[5],
                            Wind_Pressure_Coefficient_Value_7 = CP_values[6],
                            Wind_Pressure_Coefficient_Value_8 = CP_values[7])
            #print(f'Adding external node for {surface.Name}')
            idf1.newidfobject("AirflowNetwork:MultiZone:ExternalNode",
                                Name=surface.Name, #+ '.EN', # Don't know why this is .EN
                                External_Node_Height = node_height,
                                Wind_Pressure_Coefficient_Curve_Name = surface.Name,
                                Symmetric_Wind_Pressure_Coefficient_Curve = 'No',
                                Wind_Angle_Type = 'Absolute')
            
            # Assign name to multizone surface node
            idf1.getobject('AirflowNetwork:MultiZone:Surface', surface.Name).External_Node_Name = surface.Name
            
            #print(f'Adding detailed opening settings for {surface.Name}')
            new_detailed_opening = idf1.newidfobject("AirflowNetwork:MultiZone:Component:DetailedOpening")
            
            # Set properties for the DetailedOpening object:
            new_detailed_opening.Name = surface.Name
            new_detailed_opening.Air_Mass_Flow_Coefficient_When_Opening_is_Closed = 0.00014
            new_detailed_opening.Air_Mass_Flow_Exponent_When_Opening_is_Closed = 0.65
            new_detailed_opening.Type_of_Rectangular_Large_Vertical_Opening_LVO = "NonPivoted"
            new_detailed_opening.Extra_Crack_Length_or_Height_of_Pivoting_Axis = 0
            new_detailed_opening.Number_of_Sets_of_Opening_Factor_Data = 2

            # Opening Factor 1 properties
            new_detailed_opening.Opening_Factor_1 = 0
            new_detailed_opening.Discharge_Coefficient_for_Opening_Factor_1 = 0.65
            new_detailed_opening.Width_Factor_for_Opening_Factor_1 = 0
            new_detailed_opening.Height_Factor_for_Opening_Factor_1 = 0
            new_detailed_opening.Start_Height_Factor_for_Opening_Factor_1 = 0

            # Opening Factor 2 properties
            new_detailed_opening.Opening_Factor_2 = 1
            new_detailed_opening.Discharge_Coefficient_for_Opening_Factor_2 = 0.65
            new_detailed_opening.Width_Factor_for_Opening_Factor_2 = 1e-08
            new_detailed_opening.Height_Factor_for_Opening_Factor_2 = 1
            new_detailed_opening.Start_Height_Factor_for_Opening_Factor_2 = 0

            # Opening Factor 3 properties
            new_detailed_opening.Opening_Factor_3 = 0
            new_detailed_opening.Discharge_Coefficient_for_Opening_Factor_3 = 0
            new_detailed_opening.Width_Factor_for_Opening_Factor_3 = 0
            new_detailed_opening.Height_Factor_for_Opening_Factor_3 = 0
            new_detailed_opening.Start_Height_Factor_for_Opening_Factor_3 = 0

            # Opening Factor 4 properties
            new_detailed_opening.Opening_Factor_4 = 0
            new_detailed_opening.Discharge_Coefficient_for_Opening_Factor_4 = 0
            new_detailed_opening.Width_Factor_for_Opening_Factor_4 = 0
            new_detailed_opening.Height_Factor_for_Opening_Factor_4 = 0
            new_detailed_opening.Start_Height_Factor_for_Opening_Factor_4 = 0

            opening_array.append(new_detailed_opening)

    idf1.idfobjects["AirflowNetwork:MultiZone:Component:DetailedOpening"] = opening_array
                                
def get_surface_no_node(idf1,building_objects):
    logger.info('Getting surfaces with no node setup')
    
    # List of all AIRFLOWNETWORK:MULTIZONE:SURFACE objects with no External_Node_Name
    airflownetwork_multizone_surface_objects = idf1.idfobjects['AIRFLOWNETWORK:MULTIZONE:SURFACE']
    airflownetwork_multizone_surface_objects_no_external_node_name = [obj for obj in airflownetwork_multizone_surface_objects if not obj.External_Node_Name]
    # List of all airflownetwork_multizone_surface_objects_no_external_node_name .Surface_Name
    airflownetwork_multizone_surface_objects_no_external_node_name_surface_names = [obj.Surface_Name for obj in airflownetwork_multizone_surface_objects_no_external_node_name]
    airflownetwork_multizone_surface_objects_no_external_node_name_surface_names
    # Get list of these surfaces from the building_objects
    building_objects_no_external_node_name = [obj for obj in building_objects if obj.Name in airflownetwork_multizone_surface_objects_no_external_node_name_surface_names]
    return building_objects_no_external_node_name



def add_cp_surfaces(idf1, building_objects_no_external_node_name, wind_pressure_coefficient_array, kdtree, coords_df):
    logger.info('Adding CP for surfaces')
    node_height = 6.5 # Placeholder
    null_cp_counter = 0
    for i, surface in enumerate(building_objects_no_external_node_name):
        #print(f'Adding wind pressure coefficients for {surface.Name}')
        CP_values = get_cp(surface, kdtree=kdtree, coords_df=coords_df)

        # Count the number of times the CP_values is -9999
        if CP_values == [-9999] * 8:
            null_cp_counter += 1

        print(f'Number of surfaces processed: {i+1}/{len(building_objects_no_external_node_name)}, Number of null CP values: {null_cp_counter}', end='\r')
        #print(f'Adding wind pressure coefficients for {surface.Name}')
        idf1.newidfobject("AirflowNetwork:MultiZone:WindPressureCoefficientValues",
                            Name=surface.Name,
                            AirflowNetworkMultiZoneWindPressureCoefficientArray_Name = wind_pressure_coefficient_array.Name,
                            Wind_Pressure_Coefficient_Value_1 = CP_values[0],
                            Wind_Pressure_Coefficient_Value_2 = CP_values[1],
                            Wind_Pressure_Coefficient_Value_3 = CP_values[2],
                            Wind_Pressure_Coefficient_Value_4 = CP_values[3],
                            Wind_Pressure_Coefficient_Value_5 = CP_values[4],
                            Wind_Pressure_Coefficient_Value_6 = CP_values[5],
                            Wind_Pressure_Coefficient_Value_7 = CP_values[6],
                            Wind_Pressure_Coefficient_Value_8 = CP_values[7])
        #print(f'Adding external node for {surface.Name}')
        idf1.newidfobject("AirflowNetwork:MultiZone:ExternalNode",
                            Name=surface.Name, #+ '.EN', # Don't know why this is .EN
                            External_Node_Height = node_height,
                            Wind_Pressure_Coefficient_Curve_Name = surface.Name,
                            Symmetric_Wind_Pressure_Coefficient_Curve = 'No',
                            Wind_Angle_Type = 'Absolute')
        
        # Assign name to multizone surface node
        idf1.getobject('AirflowNetwork:MultiZone:Surface', surface.Name).External_Node_Name = surface.Name

def main():
    path_checker(IDF_PATH, IDD_PATH, CP_PATH)
    logger.info(f'Setting IDD file to {IDD_PATH}')
    IDF.setiddname(IDD_PATH)    # Setting the IDD file so EPPY knows how to read the IDF file.
    logger.info(f'Loading IDF file from {IDF_PATH}')
    idf1 = IDF(IDF_PATH)
    update_idf_params(idf1)
    wind_pressure_coefficient_array = add_wind_pressure_coefficients_array(idf1)
    kdtree, coords_df = vectorize_points()
    building_objects, fenestration_objects = fetch_surfaces(idf1)
    add_cp_fenestration(idf1, fenestration_objects, wind_pressure_coefficient_array, kdtree=kdtree, coords_df=coords_df)
    building_objects_no_external_node_name = get_surface_no_node(idf1,building_objects)
    add_cp_surfaces(idf1, building_objects_no_external_node_name, wind_pressure_coefficient_array, kdtree=kdtree, coords_df=coords_df)
    # Set AirflowNetwork:SimulationControl object
    logger.info('Setting AirflowNetwork:SimulationControl object to use input wind pressure coefficients')
    idf1.idfobjects['AirflowNetwork:SimulationControl'][0].Wind_Pressure_Coefficient_Type = 'Input'
    logger.info('Saving IDF file with CP')
    idf1.saveas('in_with_cp.idf')
    logger.info('Done!')

if __name__ == "__main__":
    main()
