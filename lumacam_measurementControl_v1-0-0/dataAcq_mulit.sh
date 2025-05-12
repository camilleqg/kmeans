#!/bin/bash

if [[ "$1" == "" ]]; then
	echo "ERROR: Must specify a measurement time in seconds"
	exit 1
fi
measurement_time_s="$1"

if [[ "$2" == "" ]]; then
	echo "ERROR: Must specify a relative measurement folder path base"
	exit 1
fi
measurement_folder_path_base_rel="$2"

if [[ "$3" == "" ]]; then
	echo "ERROR: Must specify a number of measurements to run"
	exit 1
fi
nMeasurements="$3"

measurement_folder_base_path="/data/XXX/data"
measurement_folder_tmp_base_path="/media/ramdisk_empir/XXX/data"
parameterSettings_file_path="parameterSettings.json"

measurement_folder_paths_rel=""
for measurementNumber in $(seq 0 $((nMeasurements - 1)));
do
	measurement_folder_path_rel=$(printf "%s_%05d" $measurement_folder_path_base_rel $measurementNumber)
	#echo $measurement_foler_path_rel
	measurement_folder_paths_rel="$measurement_folder_paths_rel $measurement_folder_path_rel"
done
#echo $measurement_folder_paths_rel


python ./python/tpxAcq_continuous_2.py $measurement_folder_base_path $measurement_folder_tmp_base_path $parameterSettings_file_path $measurement_time_s $measurement_folder_paths_rel