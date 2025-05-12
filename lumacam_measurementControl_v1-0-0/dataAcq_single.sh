#!/bin/bash

if [[ "$1" == "" ]]; then
	echo "ERROR: Must specify a measurement time in seconds"
	exit 1
fi
measurement_time_s="$1"

if [[ "$2" == "" ]]; then
	echo "ERROR: Must specify a relative measurement folder path"
	exit 1
fi
measurement_folder_path_rel="$2"

measurement_folder_base_path="/data/XXX/data"
measurement_folder_tmp_base_path="/media/ramdisk_empir/XXX/data"
parameterSettings_file_path="parameterSettings.json"

python ./python/tpxAcq_continuous_2.py $measurement_folder_base_path $measurement_folder_tmp_base_path $parameterSettings_file_path $measurement_time_s $measurement_folder_path_rel