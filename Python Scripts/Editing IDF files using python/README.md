# A python notebook to add wind pressure coefficients to surfaces in an E+ IDF file 
The script uses the following libraries

- EPPY

Date : 23-08-23  
Author : Sanjay Somanath
Contact : ssanjay@chalmers.se   

EnergyPlus Wind Pressure Coefficient Updater
============================================

This Python notebook provides a user-friendly approach to integrate wind pressure coefficients to EnergyPlus IDF files. By leveraging the EPPY library, this tool simplifies the process of annotating IDF files with wind-related data, which is essential for advanced airflow and energy simulations.

Table of Contents
-----------------

1.  Introduction
2.  Prerequisites
3.  Script Structure
    -   Importing Libraries
    -   Setting Paths
    -   Defining Wind Pressure Coefficient Array
    -   Adding Cp Values to Building Surfaces
    -   Saving the Modified IDF
4.  Conclusion
6.  Contact

Introduction
------------

This notebook is designed for EnergyPlus users, both novice and experienced, who want to incorporate the influence of wind on building surfaces into their simulations. Understanding the interaction of wind with building surfaces is crucial for realistic and accurate airflow simulations.

Prerequisites
-------------

-   Basic Python knowledge.
-   Installed version of EnergyPlus.
-   `eppy` Python library. Installation: `pip install eppy`.

Script Structure
----------------

-   Importing Libraries: Necessary modules are imported for script functionality.
-   Setting Paths: Paths for the EnergyPlus IDF and IDD files are defined.
-   Defining Wind Pressure Coefficient Array: Wind direction and associated coefficients are set.
-   Adding Cp Values to Building Surfaces: For each building surface in the IDF, wind pressure coefficients are added if the surface is exposed to outdoors.
-   Saving the Modified IDF: The IDF, now enriched with wind pressure data, is saved for further simulations.

Conclusion
----------

With this notebook, you can seamlessly add wind pressure coefficients to any EnergyPlus IDF file, enhancing the realism of your simulations.

Getting Started
---------------

1.  Clone this repository or download the notebook.
2.  Ensure you have the required prerequisites.
3.  Open the notebook using Jupyter and follow the step-by-step guide.

Contact
-------

-   Author: Sanjay Somanath
-   Email: <ssanjay@chalmers.se>