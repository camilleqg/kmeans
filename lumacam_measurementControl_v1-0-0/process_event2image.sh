#!/bin/bash

if [[ "$#" -ne 1 ]]; then
	echo "ERROR: Must specify a measurement folder. Exiting without doing anything ..."
	exit 1
fi
dest="$1"

fileName="image"
echo $fileName
mkdir "$dest/final" 2> /dev/null
echo "Creating final images..."


./bin/empir_event2image -I $dest/eventFiles -o $dest/final/$fileName --paramsFile "./parameterSettings.json" #> /dev/null 2>&1

