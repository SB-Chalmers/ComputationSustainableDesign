# Projects within the Computation Sustainable Design Group

This folder contains Python scripts developed by the Computation Sustainable Design group at Chalmers University of Technology. The projects here span a diverse range of applications, from energy simulation and IDF file editing to data visualization and geocoding.

## Contents

- **Geocode Addresses to XYZ (IPython Notebook)**
  - A notebook for converting addresses into 3D coordinates.
  
- **Editing IDF Files using Python**
  - Scripts for modifying EnergyPlus IDF files with wind pressure coefficients and other parameters.
  - Includes key scripts such as:
    - [update_cp.py](Editing IDF files using python/update_cp.py)
    - [eppy_parallel_helper.py](Editing IDF files using python/eppy_parallel_helper.py)
    - [runep.py](Editing IDF files using python/runep.py)
    - Additional supporting modules and README files in the subfolder.
  
- **Radial Plot**
  - A script to generate radial calendar plots for time-series data visualization.
  - Refer to the [radial_plot readme](radial_plot/readme.md) for more details and examples.

  ![plot](radial_plot/img/03.png)

## Getting Started

1. **Clone the Repository**  
   ```sh
   git clone https://github.com/your-repo/ComputationSustainableDesign.git
   ```

2. **Install Required Libraries**  
   The projects make use of various Python libraries such as:
   - `pandas`
   - `numpy`
   - `plotly`
   - `eppy`
   - `scipy`
   - `BeautifulSoup`  
   Install them via pip:
   ```sh
   pip install pandas numpy plotly eppy scipy beautifulsoup4
   ```

3. **Explore the Projects**  
   Navigate through each subfolder to explore the individual projects and follow the instructions provided in their respective README files.

## Contributions

Contributions are welcome. If you have suggestions or improvements:
- Open an issue or submit a pull request.
- Follow the code style guidelines and ensure new changes do not break existing functionality.
