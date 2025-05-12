#!/bin/bash

start=`date +%s`
pids=""
RESULT=0
RESULT_ALL=0
verbose=1  # verbose = 0, no comments, verbose=1 all comments

if [[ "$1" == "" ]]; then
	echo "ERROR: Must specify a measurement folder to process, Exiting without doing anything ..."
	exit 1
fi
dest="$1"

if [[ "$2" == "" ]]; then
	nThreads=1
else
	nThreads="$2"
fi


for file in $dest/tpx3Files/*.tpx3 
do
	fileBase=$(basename -s .tpx3 $file)

    fileCnt=$((fileCnt+1))
    if [ $verbose == 1 ]; then
		echo "Processing file: ${fileBase}.tpx3"
		./bin/empir_pixel2photon_tpx3spidr -i $dest/tpx3Files/${fileBase}.tpx3 -o "$dest/photonFiles/${fileBase}.empirphot" --paramsFile "./parameterSettings.json" & #check empir_pixel2photon_tpx3spidr -h for help. Note -T for using TDC1 trigger
	else
		./bin/empir_pixel2photon_tpx3spidr -i $dest/tpx3Files/${fileBase}.tpx3 -o "$dest/photonFiles/${fileBase}.empirphot" --paramsFile "./parameterSettings.json" > /dev/null 2>&1 &   # no verbose (currently not used)
    fi
    pids="$pids $!"
    
    if ! ((fileCnt % $nThreads)); then
	if [ $verbose == 1 ]; then
	    echo "reached $nThreads files! ... waiting for files to be processed..."
	fi
	for pid in $pids; do
	    wait $pid || let "RESULT=1"
	done
	
	if [ "$RESULT" == "1" ]; then
		RESULT_ALL=1
	    echo "Error occured at while processing some files!"
	fi
   	if [ $verbose == 1 ]; then
	    echo "Processed files... continuing!"
	fi
	pids=""
	RESULT=0
    fi
done

for pid in $pids; do
    wait $pid || let "RESULT=1"
done



end=`date +%s`
runtime=$((end-start))
if [ $verbose == 1 ]; then
    echo "Total processing time for $fileCnt files: $runtime seconds"
fi

exit $RESULT_ALL
