# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 16:07:05 2024

@author: camil
"""

import numpy as np 
import matplotlib.pyplot as plt
import argparse 
import json
import csv
import pandas as pd
import random 
from sklearn.utils import shuffle
import multiprocessing as mp
from multiprocessing import Pool, cpu_count 
import torch

# buncha constants 

events_per_second = 487 # events per square cm per second
def_detector_sidelength = 1e-2 # in metres 


# import json file stuff for num_events 
def load_params(json_filename):
    '''This just loads parameters from the json file'''
    with open(json_filename, 'r') as f: 
        params = json.load(f)
    return params

# picking total number of photons 

def num_events(photons, a0 = 3426.89, b0 = -3476.32, c0 = 0.10182, sigma = 40.296, mu = 24.3823, file = None):
    '''outputs the probability of events for a given number of photons based on the best fit of the histogram'''
    if file:
        params = load_params(file) 
        a0 = params.get('a0', 3426.89)
        b0 = params.get('b0', -3476.32)
        c0 = params.get('c0', 0.10182)
        sigma = params.get('sigma', 40.296)         
        mu = params.get('mu', 24.3823)
    return 1/6*(a0*np.exp(-(photons-mu)**2 / (2*sigma**2)) + b0*np.exp(-c0*photons)) 

def total_photons(scale, file = None):
    '''guesses the total number of photons out of possible values as well as a number of events.
    from there it checks if these points appear together on the histogram. the probability of coincidence
    matches the histogram distribution. once it finds a number it likes it spits it out'''
    photonspace = np.linspace(0,255,500) # this and next two lines samples function and finds an upper limit to number of events
    eventspace = num_events(photonspace) 
    max_events = max(eventspace)
    
    min_photons = 1 # upper and lower limit of number of photons 
    max_photons = 255
    
    # evaluates the num_events function to see if the random numbers match the distribution
    num_photons_final = 0 
    while num_photons_final == 0: 
        # generates a random number of photons and random number of events based on the limits
        guess_photons = random.uniform(min_photons, max_photons)
        guess_events = random.uniform(1, max_events)
        
        if guess_events <= num_events(guess_photons, file = file): 
            num_photons_final = guess_photons
    return round(scale*num_photons_final)

# generate coordinates for one photon 
def generate_coords(mu_x, mu_y, sigma2=0.00021233045007200478): 
    ''' This function will generate a set of coordinates for x and y, based on the centre of the event (input). It will only generate one at a time
    no need for custom functions here because numpy already has a sampler for gaussian distribution'''
    x_coord = random.gauss(mu_x, sigma2)
    y_coord = random.gauss(mu_y, sigma2)
    return x_coord, y_coord

# generate time coordinate for one photon

def decayfit(t, a1 = 57782.4, t1 = 0.000653566, a2 = 7473.2, t2 = 0.016498, a3 = 1.28054e6, t3 = 2.87915e-05, a4 = 455714, t4 = 0.000119424, file = None): 
    ''' This function takes the time input and outputs f(x) of the best fit line of the decay'''
    if file: 
        params = load_params(file)
        a1 = params.get('a0', 57782.4) 
        t1 = params.get('t0', 0.000653566)
        a2 = params.get('a1', 7473.2)
        t2 = params.get('t1', 0.016498)
        a3 = params.get('a2', 1.28054e6)
        t3 = params.get('t2', 2.87915e-05)
        a4 = params.get('a3', 455714)
        t4 = params.get('t3', 0.000119424)
    return a1*np.exp(-t/t1) + a2*np.exp(-t/t2) + a3*np.exp(-t/t3) + a4*np.exp(-t/t4)

def generate_time(file):
    ''' Just like the photon number generator, will guess a time and number of photons, if these points
    coincide on the integral of the best fit then they are accepted and returned '''
    # event box limits 
    time_min = 0
    time_max = 0.1 # max time for a single event 
    
    # max number of photons at a time 
    max_photons = decayfit(t = 0, file = file)
    
    # loop through until we get an accepted value 
    time_final = 0 
    while time_final == 0: 
        time_guess = random.uniform(time_min, time_max)
        photons_guess = random.uniform(0, max_photons)
        if photons_guess <= decayfit(time_guess, file = file):
            time_final = time_guess 
            
    return time_final

def scramble(x, y, state=0):
    new_x, new_y = shuffle(x, y, random_state=state)

    return new_x, new_y  

def labelmaker(events, sp_density, t_density, noise, filename = None, folder = None): 
    '''creates labels based on my naming convention for different files, keeps it consistent and easy'''
    if folder: 
        folder = folder + '/'

    if filename: 
        datafile = str(filename) 
    else: 
        datafile = str(events) + 'ev_' + str(sp_density) + 'spd_' + str(t_density) + 'td_n' + str(noise)
    

    labelfile = 'labels_' + datafile + '.csv'
    sourcefile = 'sources_' + datafile + '.csv'
    ai_labelfile = datafile + '_results' + '.csv'
    centroidfile = datafile + '_centroids' + '.csv'
    datafile = datafile + '.csv'

    if folder: 
        datafile = folder + datafile 
        centroidfile = folder + centroidfile 
        ai_labelfile = folder + ai_labelfile 
        labelfile = folder + labelfile 
        sourcefile = folder + sourcefile 

    
    return datafile, labelfile, sourcefile, ai_labelfile, centroidfile

def sim(events, noise, sp_density= '1', t_density='1', eventscale=1, spacesigma=0.00021233045007200478, x_i=None, y_i=None, t_i=None, file=None, folder = None, dataSaveID = None):
    all_events = []
    all_labels = []
    all_sources = []
    event_density = events_per_second*float(sp_density) # change density value to reflect temporal density 
    detector_sidelength = def_detector_sidelength/np.sqrt(float(t_density)) # change detector "size" to reflect density in space
    n_per_event= noise//events

    # Creating filenames 
    datafile, labelfile, sourcefile, ai_labelfile, clusterfile = labelmaker(events, sp_density, t_density, noise, folder)

    if dataSaveID: 
        datafile = str(dataSaveID) + '.csv'
        labelfile = 'labels_' + datafile
        sourcefile = 'sources_' + datafile
        if folder:
            datafile = str(folder) + '/' + datafile 
            labelfile = str(folder) + '/' + labelfile
            sourcefile = str(folder) + '/' + sourcefile 

    # Generating data 
    time_window = events/event_density # in seconds
    if file: 
        params = load_params(file)
        verbose = params.get('verbose', False)
        eventscale = params.get('eventscale', 1) 
        spacesigma = params.get('spacesigma', 0.00021233045007200478)
        start_time = params.get('start_time', -1)
        start_x = params.get('start_x', -1)
        start_y = params.get('start_y', -1)

    
    for i in range(events):
        label = i + 1 #random.randint(1, 10000)
        num_photons = total_photons(eventscale, file=file)
        all_labels.append([label])
        start_time = random.uniform(0, time_window)/time_window
        start_x = random.uniform(0, detector_sidelength)/detector_sidelength
        start_y = random.uniform(0, detector_sidelength)/detector_sidelength
        if x_i is not None: 
            start_x = x_i
        if y_i is not None: 
            start_y = y_i 
        if t_i is not None: 
            start_time = t_i

        
        all_sources.append([start_time, start_x, start_y])

        event = []
        for j in range(num_photons): 
            coords = [0]*3
            gen = generate_coords(start_x, start_y, sigma2=spacesigma)
            coords[0] = gen[0]/detector_sidelength
            coords[1] = gen[1]/detector_sidelength
            coords[2] = (generate_time(file = file) + start_time)/time_window
            event.append(coords)

        for i in range(n_per_event): 
            coords = [0]*3
            coords[0] = random.uniform(0,detector_sidelength)/detector_sidelength
            coords[1] = random.uniform(0,detector_sidelength)/detector_sidelength
            coords[2] = random.uniform(0,time_window)/time_window
            event.append(coords)

        event = sorted(event, key=lambda coord: coord[2])
        all_events.append(event)
    
    # Writing the data to datafiles 
    # columns = ['x[px]', 'y[px]', 't[s]']
    # with open(datafile, mode = 'w', newline='') as wfile: 
    #     writer = csv.writer(wfile)
    #     for event in all_events:
    #         row = [coord for point in event for coord in point]  # Flatten to 1D list
    #         writer.writerow(row)
    # with open(labelfile, mode = 'w', newline = '') as wfile: 
    #     writer = csv.writer(wfile)
    #     writer.writerow(['labels'])
    #     for label in all_labels: 
    #         writer.writerow(label)
    # with open(sourcefile, mode = 'w', newline = '') as wfile: 
    #     writer = csv.writer(wfile)
    #     writer.writerow(columns)
    #     writer.writerows(all_sources)

    return torch.tensor(all_sources)

# sim(100, 0, dataSaveID='100ev_n0')

## Finding a typical value for the variance 

vars = []
for i in range(100):
    sources = sim(100, 0)
    var = torch.mean(torch.var(sources, dim=0))
    vars.append(var)

print(np.mean(np.array(vars)))


