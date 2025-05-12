# LumaCam MeasurementControl

## Description
This repository contains scripts and compiled programs to run a measurement using a LumaCam, including online data processing. Scripts for post-processing are included as well.

## Structure
 - top level shell scripts are at the project root
 - program binaries are in the "bin" folder
 - python scripts are in the "python" folder
 - a detailed documentation is in the "documentation" folder

## Setup
Required libraries:
 - libtiff --> for creating tiff images.
 - python --> python3 is required to be python (only for data acquisition, not required for processing)

Create a "settings_installation.py" file (only for data acquisition, not required for processing):
 - create a copy of "./python/settings_installation_example.py" under "./python/settings_installation.py"
 - modify the entries in the file to the correct paths for the system

## Usage

### Data Acquisition with Online Processing (Example)
Use the "dataAcq_single.sh" (for a single measurement) or the "dataAcq_mulit.sh" (for multiple measurements directly after each other) script:
 - Adjust the parameters in "parameterSettings.json" to the desired values
 - Adjust the variable "measurement_foler_base_bath" in the "dataAcq_single.sh" or the "dataAcq_mulit.sh" to where you want all your measurements to be saved
 - Adjust the variable "measurement_folder_tmp_base_path" in the "dataAcq_single.sh" or the "dataAcq_mulit.sh" to where you want temporary data needed for processing to be saved
 - Call the "dataAcq_single.sh" or the "dataAcq_mulit.sh" script with the desired measurement runtime in seconds, measurement folder path relative to the path set in the "measurement_foler_base_bath" variable, and number of measurements (only for "dataAcq_mulit.sh"), e.g.:
   	```console
    $ ./dataAcq_single.sh 60 XXX
    ```
	for a single measurement of 60 seconds saved at "measurement_foler_base_bath"/XXX
    
	or
    ```console
    $ ./dataAcq_mulit.sh 60 XXX 10
    ```
	for ten measurements of 60 seconds each, saved at "measurement_foler_base_bath"/XXX_00000, "measurement_foler_base_bath"/XXX_00001, ... , and "measurement_foler_base_bath"/XXX_00009.

### Post Processing (Example)
For post processing, use the "dataReduct.sh" script in the EMPIR base directory:
 - Adjust the parameters in "parameterSettings.json" to the desired values
 - Get the path of the folder of the measurement to process (here called "/XXX"). This is the folder that contains the "tpx3Files" folder (e.g. "/XXX/tpx3Files/singleTpxFile.tpx3").
 - call "dataReduct.sh" with the measurement folder path as an argument:
	```console
    $ ./dataReduct.sh /XXX
	```
 - The created image is saved under "/XXX/final/image"
