
import requests
import time
import os
import json
import subprocess
import logging

# Manage Serval
def thread_Serval(measurements_base_path, pathServalApp):

	serval_command = [
		"java",
		"-jar",
		pathServalApp
	]

	with open(measurements_base_path + "/Servarlog.txt", 'a') as log_output:
		subprocess.run(serval_command, stdout=log_output, stderr=subprocess.STDOUT) 

def setup_tpx3spidr(baseurl, config_pixel_path, config_dacs_path, sysConfig, folder_tpx3Files_path):

	while True:
		sucess = True

		# load a pixelconfig exported by SoPhy, the file should exist on the server
		resp = requests.get(url=baseurl+'/config/load?format=pixelconfig&file='+config_pixel_path)
		data = resp.text
		print('Response: ' + data)
		sucess = sucess and (resp.status_code == 200)

		#  .... and the corresponding DACS file
		resp = requests.get(url=baseurl+'/config/load?format=dacs&file='+config_dacs_path)
		data = resp.text
		print('Response: ' + data)
		sucess = sucess and (resp.status_code == 200)

		# set the sysConfig
		resp = requests.put(url=baseurl+'/detector/config', data=json.dumps(sysConfig))
		data = resp.text
		print('Response: ' + data)
		sucess = sucess and (resp.status_code == 200)

		# set the destination settings
		print(folder_tpx3Files_path)
		os.makedirs(folder_tpx3Files_path , exist_ok=True)
		baseSavePath = "file:" + folder_tpx3Files_path
		destination = {
			"Raw" : [ {
				"Base" : baseSavePath ,
				"FilePattern" : "%yyyy-MM-dd'T'HHmmss_",
				"SplitStrategy" : "FRAME"
				} ],
			"Image" : [ ]
		}
		resp = requests.put(url=baseurl+'/server/destination', data=json.dumps(destination))
		data = resp.text
		print('Response: ' + data)
		sucess = sucess and (resp.status_code == 200)

		if sucess:
			break
		else:
			print("Detector Configuration Failed! Trying again in 5 seconds...")
			time.sleep(5)


	# we could ask the complete chip config, and print/save them
	#resp = requests.get(url=baseurl+'/chipConfig');
			
# processing of a single .tpx3 file
def thread_processing_singleFrame(file_log_path, tpx3File_path, photonFile_path, eventFile_path, processingParameters_file_path, tpx3Files_keep = True, photonFiles_keep = True):
	logging.info("Processing %s: starting", tpx3File_path)


	pixel2photon_command = [
		"nice", "-n", "19",
		"./bin/empir_pixel2photon_tpx3spidr",
		"--paramsFile", processingParameters_file_path,
		"-i", tpx3File_path,
		"-o", photonFile_path
	]

	#logging.info("Thread operation: %s", ' '.join(map(str, pixels_to_photons_command)))

	with open(file_log_path, 'a') as log_output:
		subprocess.run(pixel2photon_command, stdout=log_output, stderr=subprocess.STDOUT)

	if (not tpx3Files_keep) & os.path.isfile(tpx3File_path):
		os.remove(tpx3File_path)

	photon2event_command = [
		"nice", "-n", "19",
		"./bin/empir_photon2event",
		"--paramsFile", processingParameters_file_path,
		"-i", photonFile_path,
		"-o", eventFile_path
	]

	#logging.info("Thread operation: %s", ' '.join(map(str, photon_to_event_command)))

	with open(file_log_path, 'a') as log_output:
		subprocess.run(photon2event_command, stdout=log_output, stderr=subprocess.STDOUT)

	if (not photonFiles_keep) & os.path.isfile(photonFile_path):
		os.remove(photonFile_path)

	#time.sleep(1)
	logging.info("Processing %s: finishing", tpx3File_path)

			
# processing of a single .tpx3 file
def thread_processing_events2image(file_log_path, folder_eventFiles_path, file_image_path, processingParameters_file_path, eventFiles_keep = True):
	logging.info("Binning %s: starting", folder_eventFiles_path)

	event2image_command = [
		"nice", "-n", "19",
		"./bin/empir_event2image",
		"--paramsFile", processingParameters_file_path,
		"--parallel", "false",
		"-I", folder_eventFiles_path,
		"-o", file_image_path
	]

	#logging.info("Thread operation: %s", ' '.join(map(str, pixels_to_photons_command)))

	with open(file_log_path, 'a') as log_output:
		subprocess.run(event2image_command, stdout=log_output, stderr=subprocess.STDOUT)

	if (not eventFiles_keep):
		filesList=os.listdir(folder_eventFiles_path)
		for file_name in filesList:
			if file_name.endswith(".empirevent"):
				os.remove(folder_eventFiles_path + "/" + file_name)
			else:
				print("ERROR: Non .empirevent file in directory: " + file_name + "!")

		os.rmdir(folder_eventFiles_path)

	#time.sleep(1)
	logging.info("Binning %s: finished", file_image_path)