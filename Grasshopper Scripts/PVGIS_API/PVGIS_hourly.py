import ghpythonlib.components as ghcomp
import Grasshopper.Kernel as gh
import urllib2
import urllib
import json

# Function to check if a year is a leap year
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def remove_leapday_hours(list_of_8784_numbers):
    """
    Removes the hours corresponding to February 29th for leap years from the list of 8784 hourly data points.
    
    Args:
    - list_of_8784_numbers: List of hourly data points (length 8784).
    
    Returns:
    - List of hourly data points with leap day hours removed (length 8760).
    """
    if len(list_of_8784_numbers) != 8784:
        raise ValueError("The input list must have exactly 8784 elements.")
    
    # Indices of hours corresponding to February 29th in a leap year (for a year starting from January 1st)
    leap_day_indices = [1416 + i for i in range(24)]

    # Remove the leap day hours
    filtered_data = [data for i, data in enumerate(list_of_8784_numbers) if i not in leap_day_indices]
    
    # Handle subsequent years by shifting the indices accordingly
    for year_start in range(8784, len(list_of_8784_numbers), 8784):
        leap_day_indices = [year_start + 1416 + i for i in range(24)]
        filtered_data.extend([data for i, data in enumerate(list_of_8784_numbers[year_start:year_start + 8784]) if i not in leap_day_indices])
    
    return filtered_data

def create_warning(msg):
    """
    Adds a warning message to the Grasshopper component.
    """
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)

def create_output(output):
    """
    Sets the output nickname and description.
    """
    ghenv.Component.Params.Output[0].NickName = "API Output"
    ghenv.Component.Params.Output[0].Description = "API output data"
    return output

def initialize_inputs():
    """
    Initialize component inputs if they do not exist.
    """
    if not ghenv.Component.Params.Input[0].Name == "lat":
        ghenv.Component.Params.Input[0].NickName = "lat"
        ghenv.Component.Params.Input[0].Name = "lat"
        ghenv.Component.Params.Input[0].Description = "Latitude in decimal degrees, south is negative"
        ghenv.Component.Params.Input[0].Optional = False

    if not ghenv.Component.Params.Input[1].Name == "lon":
        ghenv.Component.Params.Input[1].NickName = "lon"
        ghenv.Component.Params.Input[1].Name = "lon"
        ghenv.Component.Params.Input[1].Description = "Longitude in decimal degrees, west is negative"
        ghenv.Component.Params.Input[1].Optional = False

    if not ghenv.Component.Params.Input[2].Name == "usehorizon":
        ghenv.Component.Params.Input[2].NickName = "usehorizon"
        ghenv.Component.Params.Input[2].Name = "usehorizon"
        ghenv.Component.Params.Input[2].Description = "Calculate taking into account shadows from high horizon"
        ghenv.Component.Params.Input[2].Optional = True

    if not ghenv.Component.Params.Input[3].Name == "userhorizon":
        ghenv.Component.Params.Input[3].NickName = "userhorizon"
        ghenv.Component.Params.Input[3].Name = "userhorizon"
        ghenv.Component.Params.Input[3].Description = "Heights of the horizon at equidistant directions"
        ghenv.Component.Params.Input[3].Optional = True

    if not ghenv.Component.Params.Input[4].Name == "raddatabase":
        ghenv.Component.Params.Input[4].NickName = "raddatabase"
        ghenv.Component.Params.Input[4].Name = "raddatabase"
        ghenv.Component.Params.Input[4].Description = "Name of the radiation database"
        ghenv.Component.Params.Input[4].Optional = True

    if not ghenv.Component.Params.Input[5].Name == "startyear":
        ghenv.Component.Params.Input[5].NickName = "startyear"
        ghenv.Component.Params.Input[5].Name = "startyear"
        ghenv.Component.Params.Input[5].Description = "First year of hourly averages"
        ghenv.Component.Params.Input[5].Optional = True

    if not ghenv.Component.Params.Input[6].Name == "endyear":
        ghenv.Component.Params.Input[6].NickName = "endyear"
        ghenv.Component.Params.Input[6].Name = "endyear"
        ghenv.Component.Params.Input[6].Description = "Final year of hourly averages"
        ghenv.Component.Params.Input[6].Optional = True

    if not ghenv.Component.Params.Input[7].Name == "pvcalculation":
        ghenv.Component.Params.Input[7].NickName = "pvcalculation"
        ghenv.Component.Params.Input[7].Name = "pvcalculation"
        ghenv.Component.Params.Input[7].Description = "0 for only solar radiation, 1 for PV production estimation"
        ghenv.Component.Params.Input[7].Optional = True

    if not ghenv.Component.Params.Input[8].Name == "peakpower":
        ghenv.Component.Params.Input[8].NickName = "peakpower"
        ghenv.Component.Params.Input[8].Name = "peakpower"
        ghenv.Component.Params.Input[8].Description = "Nominal power of the PV system in kW"
        ghenv.Component.Params.Input[8].Optional = True

    if not ghenv.Component.Params.Input[9].Name == "pvtechchoice":
        ghenv.Component.Params.Input[9].NickName = "pvtechchoice"
        ghenv.Component.Params.Input[9].Name = "pvtechchoice"
        ghenv.Component.Params.Input[9].Description = "PV technology choice"
        ghenv.Component.Params.Input[9].Optional = True

    if not ghenv.Component.Params.Input[10].Name == "mountingplace":
        ghenv.Component.Params.Input[10].NickName = "mountingplace"
        ghenv.Component.Params.Input[10].Name = "mountingplace"
        ghenv.Component.Params.Input[10].Description = "Type of PV module mounting"
        ghenv.Component.Params.Input[10].Optional = True

    if not ghenv.Component.Params.Input[11].Name == "loss":
        ghenv.Component.Params.Input[11].NickName = "loss"
        ghenv.Component.Params.Input[11].Name = "loss"
        ghenv.Component.Params.Input[11].Description = "System losses in percent"
        ghenv.Component.Params.Input[11].Optional = True

    if not ghenv.Component.Params.Input[12].Name == "trackingtype":
        ghenv.Component.Params.Input[12].NickName = "trackingtype"
        ghenv.Component.Params.Input[12].Name = "trackingtype"
        ghenv.Component.Params.Input[12].Description = "Type of suntracking used"
        ghenv.Component.Params.Input[12].Optional = True

    if not ghenv.Component.Params.Input[13].Name == "angle":
        ghenv.Component.Params.Input[13].NickName = "angle"
        ghenv.Component.Params.Input[13].Name = "angle"
        ghenv.Component.Params.Input[13].Description = "Inclination angle from the horizontal plane"
        ghenv.Component.Params.Input[13].Optional = True

    if not ghenv.Component.Params.Input[14].Name == "aspect":
        ghenv.Component.Params.Input[14].NickName = "aspect"
        ghenv.Component.Params.Input[14].Name = "aspect"
        ghenv.Component.Params.Input[14].Description = "Orientation angle"
        ghenv.Component.Params.Input[14].Optional = True

    if not ghenv.Component.Params.Input[15].Name == "optimalinclination":
        ghenv.Component.Params.Input[15].NickName = "optimalinclination"
        ghenv.Component.Params.Input[15].Name = "optimalinclination"
        ghenv.Component.Params.Input[15].Description = "Calculate the optimum inclination angle"
        ghenv.Component.Params.Input[15].Optional = True

    if not ghenv.Component.Params.Input[16].Name == "optimalangles":
        ghenv.Component.Params.Input[16].NickName = "optimalangles"
        ghenv.Component.Params.Input[16].Name = "optimalangles"
        ghenv.Component.Params.Input[16].Description = "Calculate both optimal inclination and orientation angles"
        ghenv.Component.Params.Input[16].Optional = True

    if not ghenv.Component.Params.Input[17].Name == "components":
        ghenv.Component.Params.Input[17].NickName = "components"
        ghenv.Component.Params.Input[17].Name = "components"
        ghenv.Component.Params.Input[17].Description = "Output beam, diffuse, and reflected radiation components"
        ghenv.Component.Params.Input[17].Optional = True

    if not ghenv.Component.Params.Input[18].Name == "outputformat":
        ghenv.Component.Params.Input[18].NickName = "outputformat"
        ghenv.Component.Params.Input[18].Name = "outputformat"
        ghenv.Component.Params.Input[18].Description = "Output format (csv, basic, json)"
        ghenv.Component.Params.Input[18].Optional = True

    if not ghenv.Component.Params.Input[19].Name == "browser":
        ghenv.Component.Params.Input[19].NickName = "browser"
        ghenv.Component.Params.Input[19].Name = "browser"
        ghenv.Component.Params.Input[19].Description = "Use if accessing from a web browser"
        ghenv.Component.Params.Input[19].Optional = True

# Initialize inputs
initialize_inputs()

# Default values for the optional inputs
lat_default = None
lon_default = None
usehorizon_default = 1
userhorizon_default = []
raddatabase_default = "PVGIS-SARAH"  # Choose a valid default database
startyear_default = None
endyear_default = None
pvcalculation_default = 1
peakpower_default = 1
pvtechchoice_default = "crystSi"
mountingplace_default = "building"
loss_default = 14
trackingtype_default = 0
angle_default = 0
aspect_default = 0
optimalinclination_default = 0
optimalangles_default = 0
components_default = 0
outputformat_default = "json"
browser_default = 0

# Input validation and assignment
lat = lat if lat is not None else lat_default
lon = lon if lon is not None else lon_default
usehorizon = usehorizon if usehorizon is not None else usehorizon_default
userhorizon = userhorizon if userhorizon is not None else userhorizon_default
raddatabase = raddatabase if raddatabase is not None else raddatabase_default
startyear = startyear if startyear is not None else startyear_default
endyear = endyear if endyear is not None else endyear_default
pvcalculation = pvcalculation if pvcalculation is not None else pvcalculation_default
peakpower = peakpower if peakpower is not None else peakpower_default
pvtechchoice = pvtechchoice if pvtechchoice is not None else pvtechchoice_default
mountingplace = mountingplace if mountingplace is not None else mountingplace_default
loss = loss if loss is not None else loss_default
trackingtype = trackingtype if trackingtype is not None else trackingtype_default
angle = angle if angle is not None else angle_default
aspect = aspect if aspect is not None else aspect_default
optimalinclination = optimalinclination if optimalinclination is not None else optimalinclination_default
optimalangles = optimalangles if optimalangles is not None else optimalangles_default
components = components if components is not None else components_default
outputformat = outputformat if outputformat is not None else outputformat_default
browser = browser if browser is not None else browser_default

# Check for minimum obligatory inputs and add warning if missing
mandatory_inputs = {
    "Latitude": lat,
    "Longitude": lon
}

if pvcalculation == 1:
    mandatory_inputs.update({
        "Peak Power": peakpower,
        "Loss": loss,
        "Mounting Place": mountingplace,
        "Angle": angle,
        "Aspect": aspect
    })

missing_inputs = [name for name, value in mandatory_inputs.items() if value is None]

if run:
    # Check for minimum obligatory inputs and add warning if missing
    mandatory_inputs = {
        "Latitude": lat,
        "Longitude": lon
    }

    if pvcalculation == 1:
        mandatory_inputs.update({
            "Peak Power": peakpower,
            "Loss": loss,
            "Mounting Place": mountingplace,
            "Angle": angle,
            "Aspect": aspect
        })

    missing_inputs = [name for name, value in mandatory_inputs.items() if value is None]

    if missing_inputs:
        create_warning("Missing mandatory inputs: {}".format(", ".join(missing_inputs)))
        output = None
    else:
        # Construct the input dictionary
        input_params = {
            "lat": lat,
            "lon": lon,
            "usehorizon": usehorizon,
            "raddatabase": raddatabase,
            "startyear": startyear,
            "endyear": endyear,
            "pvcalculation": pvcalculation,
            "peakpower": peakpower,
            "pvtechchoice": pvtechchoice,
            "mountingplace": mountingplace,
            "loss": loss,
            "trackingtype": trackingtype,
            "angle": angle,
            "aspect": aspect,
            "optimalinclination": optimalinclination,
            "optimalangles": optimalangles,
            "components": components,
            "outputformat": outputformat,
            "browser": browser
        }
        
        # Only add 'userhorizon' if it is not empty
        if userhorizon:
            input_params["userhorizon"] = ",".join(map(str, userhorizon))
        
        # Remove any keys with None values
        input_params = {k: v for k, v in input_params.items() if v is not None}
        
        # Base URL for the API
        base_url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
        
        # Encode parameters into URL
        url_params = urllib.urlencode(input_params)
        full_url = "{}?{}".format(base_url, url_params)
        
        # Parsing and storing each section in different variables
        try:
            # Make the API call
            response = urllib2.urlopen(full_url)
            response_data = response.read()
            
            # Decode the response based on output format
            if outputformat == "json":
                response_json = json.loads(response_data)
                output = response_json
            else:
                output = response_data
            
            # Parse and store each section in different variables
            inputs_data = response_json.get("inputs", {})
            outputs_data = response_json.get("outputs", {})
            meta_data = response_json.get("meta", {})
            
            # Store specific sections in separate variables
            location = inputs_data.get("location", {})
            meteo_data = inputs_data.get("meteo_data", {})
            mounting_system = inputs_data.get("mounting_system", {})
            pv_module = inputs_data.get("pv_module", {})
            
            hourly_data = outputs_data.get("hourly", [])
            
            # Extract the specified hourly outputs
            time_stamps = [hour["time"] for hour in hourly_data]
            P = [hour["P"] for hour in hourly_data]
            G_i = [hour["G(i)"] for hour in hourly_data]
            H_sun = [hour["H_sun"] for hour in hourly_data]
            T2m = [hour["T2m"] for hour in hourly_data]
            WS10m = [hour["WS10m"] for hour in hourly_data]
            Int = [hour["Int"] for hour in hourly_data]
            
        except urllib2.URLError as e:
            create_warning("API call failed: {}".format(e.reason))
            output = None
        except ValueError:
            create_warning("No JSON object could be decoded. Check if outputformat is set correctly.")
            output = response_data
        except Exception as e:
            create_warning("Unexpected error: {}".format(str(e)))
            output = None

    # Print debug information
    print("URL: {}".format(full_url))



    if is_leap_year(startyear):
        time_stamps = remove_leapday_hours(time_stamps)
        P = remove_leapday_hours(P)
        G_i = remove_leapday_hours(G_i)
        H_sun = remove_leapday_hours(H_sun)
        T2m = remove_leapday_hours(T2m)
        WS10m = remove_leapday_hours(WS10m)
        Int = remove_leapday_hours(Int)