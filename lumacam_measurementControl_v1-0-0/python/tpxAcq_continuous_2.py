#!/usr/bin/python

import signal
import sys
import logging
import threading
import time
import requests
import os
import subprocess
import concurrent.futures
import shutil

import tpx3Spider_parameters
import tpx3Spider_lumacam
import settings_installation

#
# Settings
#

baseurl = 'http://localhost:8080'

folder_tpx3Files_tmp_name = "tpx3Files_tmp"
folder_tpx3Files_final_name = "tpx3Files"
folder_photonFiles_name = "photonFiles"
folder_eventFiles_name = "eventFiles"
folder_images_name = "final"

file_image_name = "image"

fileExtension_tpx3 = ".tpx3"
fileExtension_empirphot = ".empirphot"
fileExtension_empirevent = ".empirevent"

tpx3Files_keep = True
photonFiles_keep = False
eventFiles_keep = False

#
# Global variables
#

shutdown = False

measurementFolder_base_path = ""
measurementFolder_tmp_base_path = ""

measurementFolder_currentProcessing_path_rel = ""
measurementFolder_currentMeasuring_path_rel = ""


pool_evenReconstruction = concurrent.futures.ThreadPoolExecutor(max_workers=settings_installation.nWorkers)


#
# Signal Handling
#

def signal_handler_sigint(sig, frame):
	global shutdown

	if shutdown:
		sys.exit(1)
	else:
		print('Cleaning up and quitting afterwards')
		print('To quit immediately press Ctrl+C (again)')
		shutdown = True

signal.signal(signal.SIGINT, signal_handler_sigint)

#
# Functions
#

# Process all files of the different measurements
def thread_processing(dummy, processingParameters_file_path):
	global measurementFolder_currentProcessing_path_rel

	future_image = None

	while not shutdown:
		#print("Shutdown " + str(shutdown))

		measurementFolder_currentProcessing_path_rel = measurementFolder_currentMeasuring_path_rel

		if measurementFolder_currentProcessing_path_rel == "":
			print("No directory set. Processing idle...")
			time.sleep(0.1)#Nothing to do
		else :
			#Schedule all files in a single measurement for processing
			print("Start scheduling processing in folder: " + measurementFolder_currentProcessing_path_rel)

			if tpx3Files_keep:
				folder_tpx3Files_tmp_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_tpx3Files_tmp_name
				folder_tpx3Files_final_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_tpx3Files_final_name
			else:
				folder_tpx3Files_tmp_path = measurementFolder_tmp_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_tpx3Files_tmp_name
				folder_tpx3Files_final_path = measurementFolder_tmp_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_tpx3Files_final_name

			if photonFiles_keep:
				folder_photonFiles_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_photonFiles_name
			else:
				folder_photonFiles_path = measurementFolder_tmp_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_photonFiles_name

			if eventFiles_keep:
				folder_eventFiles_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_eventFiles_name
			else:
				folder_eventFiles_path = measurementFolder_tmp_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_eventFiles_name
			
			folder_images_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/" + folder_images_name

			file_image_path = folder_images_path + "/" + file_image_name

			file_log_path = measurementFolder_base_path + "/" + measurementFolder_currentProcessing_path_rel + "/log.txt"

			os.makedirs(folder_tpx3Files_final_path, exist_ok=True)
			
			futures = []

			while True:
				if os.path.isdir(folder_tpx3Files_tmp_path):
					filesList=os.listdir(folder_tpx3Files_tmp_path)

					#print("Found " + str(len(filesList)) + " files")

					if len(filesList) > 1:
						#print("Found files to process")
						time.sleep(2)#Wait for files to be finished written

						filesList.sort()
						filesList.pop()

						for file in filesList:
							if file.endswith(".tpx3"):
								print("Scheduling " + file)

								#threadWaitCnt=0
								#while threading.active_count() > settings_installation.nWorkers + 2:
								#	#print (threadWaitCnt)
								#	if threadWaitCnt % 50 == 0:
								#		logging.info("Main    : active processing threads: %d", threading.active_count()-3)
								#	
								#	time.sleep(0.1)
								#	threadWaitCnt = threadWaitCnt + 1

								tpx3File_temp_path = folder_tpx3Files_tmp_path + "/" + file
								tpx3File_final_path = folder_tpx3Files_final_path + "/" + file
								photonFile_path = folder_photonFiles_path + "/" + file.replace(fileExtension_tpx3, fileExtension_empirphot)
								eventFile_path = folder_eventFiles_path + "/" + file.replace(fileExtension_tpx3, fileExtension_empirevent)

								mv_tpx3_command = [
									"mv",
									tpx3File_temp_path,
									folder_tpx3Files_final_path
								]
								#print (' '.join(map(str, mv_tpx3_command)))

								with open(file_log_path, 'a') as log_output:
									subprocess.run(mv_tpx3_command, stdout=log_output, stderr=subprocess.STDOUT)                

								#x = threading.Thread(target=tpx3Spider_lumacam.thread_processing_singleFrame, args=(measurementFolder_currentProcessing, tpx3File_final_path, photonFile_path, eventFile_path, processingParameters_file_path, tpx3Files_keep, photonFiles_keep), name=file)
								#threads.append(x)
								#x.start()

								future = pool_evenReconstruction.submit(tpx3Spider_lumacam.thread_processing_singleFrame, file_log_path, tpx3File_final_path, photonFile_path, eventFile_path, processingParameters_file_path, tpx3Files_keep, photonFiles_keep)
								futures.append(future)
								#print(f'Futures: {futures}')
								
								time.sleep(1)
							else:
								print("ERROR: Non .tpx3 file in directory: " + file + "!")
								print("PLEASE REMOVE THIS FILE!")


					else:
						#print("Found no files to process")
						if measurementFolder_currentProcessing_path_rel != measurementFolder_currentMeasuring_path_rel:
							#No files left to process and corresponding measurement is done
							#print("Measurement done")
							shutil.rmtree(folder_tpx3Files_tmp_path)
							break
						else :
							time.sleep(0.1)#Nothing to do

					
					
			


			#threadWaitCnt=0
			#while threading.active_count() > 3:
			#	if threadWaitCnt % 50 == 0:
			#		logging.info("Main    : active threads: %d", threading.active_count()-1)
			#		for thread in threading.enumerate()[1:]: 
			#			logging.info("Main    : thread name %s.", thread.name)
			#	time.sleep(0.1)
			#	threadWaitCnt = threadWaitCnt + 1

			os.makedirs(folder_images_path, exist_ok=True)

			if not (future_image is None):
				future_image.result()

			for future in futures:
				future.result()

			#logging.info("Binning %s: starting", folder_eventFiles_path)

			#event2image_command = [
			#	"./bin/empir_event2image",
			#	"--paramsFile", processingParameters_file_path,
			#	"-I", folder_eventFiles_path,
			#	"-o", file_image_path
			#]

			#with open(measurementFolder_currentProcessing + "/log.txt", 'a') as log_output:
			#	subprocess.run(event2image_command, stdout=log_output, stderr=subprocess.STDOUT)

			#if (not eventFiles_keep):
			#	filesList=os.listdir(folder_eventFiles_path)
			#	for file_name in filesList:
			#		if file_name.endswith(".empirevent"):
			#			os.remove(folder_eventFiles_path + "/" + file_name)
			#		else:
			#			print("ERROR: Non .empirevent file in directory: " + file_name + "!")
			#
			#	os.rmdir(folder_eventFiles_path)
   
			future_image = pool_evenReconstruction.submit(tpx3Spider_lumacam.thread_processing_events2image, file_log_path, folder_eventFiles_path, file_image_path, processingParameters_file_path, eventFiles_keep)

	future_image.result()
	pool_evenReconstruction.shutdown()

#
# Main Program
#

if __name__ == "__main__":
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
	
	if len(sys.argv) < 6:
		print("Usage: python script.py <measurementFolder_base_path> <measurementFolder_tmp_base_path> <processingSettingsFile> <measurementTime_s> <measurementFolder(s)_path_rel>")
		sys.exit(1)

	measurementFolders_path_rel = list()

	measurementFolder_base_path = sys.argv[1]
	measurementFolder_tmp_base_path = sys.argv[2]
	processingParameters_file_path = str(sys.argv[3])
	measurementTime_s = int(sys.argv[4])
	for measurement_index in range(5, len(sys.argv)):
		measurementFolders_path_rel.append(str(sys.argv[measurement_index]))
	

	os.makedirs(measurementFolder_base_path , exist_ok=True)
	os.makedirs(measurementFolder_tmp_base_path , exist_ok=True)

	threads = list()


	#
	# Set up
	#

	#Serval
	logging.info("Main    : create Serval thread")
	servalThread = threading.Thread(target=tpx3Spider_lumacam.thread_Serval, args=(measurementFolder_base_path, settings_installation.pathServalApp), name="Serval" )
	threads.append(servalThread)
	servalThread.start()

	time.sleep(5)

	#Processing
	logging.info("Main    : create Master Processing thread")
	masterProcessingThread = threading.Thread(target=thread_processing, args=(0,processingParameters_file_path), name="Processing_Master" )
	threads.append(masterProcessingThread)
	masterProcessingThread.start()

	#
	# Measurement
	#

	for measurementFolder_path_rel in measurementFolders_path_rel:

		logging.info("Starting measurement in: " + measurementFolder_path_rel)

		# Upload TPX3 SPIDR Settings
		os.makedirs(measurementFolder_base_path + "/" + measurementFolder_path_rel , exist_ok=True)
		measurementFolder_currentMeasuring_path_rel = measurementFolder_path_rel
		tpx3Spider_lumacam.setup_tpx3spidr(baseurl, settings_installation.config_pixel_path, settings_installation.config_dacs_path, tpx3Spider_parameters.sysConfig, measurementFolder_base_path + "/" + measurementFolder_currentMeasuring_path_rel + "/" + folder_tpx3Files_tmp_name)

		resp = requests.get(url=baseurl+'/measurement/start')

		##check if we should stop acquisition
		measurement_counter = 0
		while (not shutdown) and (measurement_counter < measurementTime_s):
			time.sleep(1)
			measurement_counter = measurement_counter + 1

		try:
			resp = requests.get(url=baseurl+'/measurement/stop')
		except:
			print("Server seems to be down.")

		#Only continue if the processings cheduling is at least at the just finished measurement to prevent processing being skipped
		keepUp_counter = 0
		while measurementFolder_currentProcessing_path_rel != measurementFolder_currentMeasuring_path_rel:
			if keepUp_counter % 50 == 0:
				logging.warning("Cant keep up! Waiting for analysis before continuing...")
			time.sleep(0.1)
			keepUp_counter = keepUp_counter + 1


	
	measurementFolder_currentMeasuring_path_rel = ""
	
	shutdown = True

	logging.info("thread_tpx3Acq: finishing")


	#
	# Cleanup
	#


	try:
		resp = requests.get(url=baseurl+'/server/shutdown')
	except:
		print("Server seems to be down.")

	threadWaitCnt=0
	while threading.active_count() > 1:
		if threadWaitCnt % 50 == 0:
			#logging.info("Main    : active threads: %d", threading.active_count()-1)
			#for thread in threading.enumerate()[1:]: 
			#	logging.info("Main    : thread name %s.", thread.name)
			logging.info("Waiting for tasks to finish...")

		time.sleep(0.1)
		threadWaitCnt = threadWaitCnt + 1






