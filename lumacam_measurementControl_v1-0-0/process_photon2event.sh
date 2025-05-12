#!/bin/bash

start=`date +%s`
pids=""
RESULT=0
RESULT_ALL=0

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



for file in $dest/photonFiles/*.empirphot
do
	fileBase=$(basename -s .empirphot $file)

    fileCnt=$((fileCnt+1))
    echo "Processing file: $fileBase.empirphot"
    ./bin/empir_photon2event -i "$dest/photonFiles/$fileBase.empirphot" -o "$dest/eventFiles/${fileBase}.empirevent" --paramsFile "./parameterSettings.json" &
    pids="$pids $!"
    if ! ((fileCnt % $nThreads)); then
    	echo "reached $nThreads files! ... waiting for files to be processed..."
	for pid in $pids; do
	    wait $pid || let "RESULT=1"
	done
	
	if [ "$RESULT" == "1" ]; then
		RESULT_ALL=1
	    echo "Error occured at while processing some files!"
	fi
   	echo "Processed files... continuing!"
	pids=""
	RESULT=0
    fi
done

for pid in $pids; do
    wait $pid || let "RESULT=1"
done


end=`date +%s`
runtime=$((end-start))
echo "Total processing time for $fileCnt files: $runtime seconds"

exit $RESULT_ALL
