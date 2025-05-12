#!/bin/bash

nThreads=20 #Modify number of number of paralell processes used for data reduction according to PC specs, here set to 20.

start=`date +%s`

if [[ "$1" == "" ]]; then
	echo "ERROR: Must specify a name, exiting without doing anything ..."
	exit 1
fi
dest="$1"

rm -rf $dest/final
rm -rf $dest/eventFiles
rm -rf $dest/photonFiles

./process_pixel2photon.sh $dest $nThreads
./process_photon2event.sh $dest $nThreads
./process_event2image.sh $dest


#Keep only final images and raw data
rm -rf $dest/eventFiles
rm -rf $dest/photonFiles
#rm -rf $dest/tpx3Files

end=`date +%s`
runtime=$((end-start))
echo "Total processing time: $runtime seconds"

