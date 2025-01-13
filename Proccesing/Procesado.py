
import os
import sys
import argparse
import psutil
import time
import asyncio
import logging
import random
from datetime import date, datetime
from pathlib import Path

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 

from scipy import signal, stats
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch, freqz, filtfilt

import mne
from autoreject import AutoReject

from mne.channels import read_layout
from mne.time_frequency import psd_array_welch
from mne.time_frequency import tfr_multitaper
from mne.stats import permutation_cluster_1samp_test as pcluster_test
from brainflow.board_shim import BoardShim, BrainFlowInputParams

""" def get_args():
    #Get command-line arguments

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file_path', help = 'Path to the file to process', type = str)

    parser.add_argument('format_type', nargs='?', help = 'Path to the file to process', type = str, default= False)

    #parser.add_argument('output_path', help = 'Path to save the processed file', type = str)

    return parser.parse_args()
 """


def only_eeg(file_path, old_format = False):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    if old_format:
        #Change 'Time' to datetime type and then calculate the difference
        df['Time'] = pd.to_datetime(df['Time'])
        df['Time'] = ((df['Time'] - df['Time'].min()) / np.timedelta64(1,'D'))*1e7

        df['STI'] = df['STI'] - 1

    else:
        # Subtract the first time value from all the time values
        df['Time'] = df['Time'] - df['Time'].iloc[0]
    
    df['Time'] = df['Time'].round(5)
    
    # Create new DataFrame with the first 9 columns (time,channels and events)
    columns_to_select = df.columns[0:9].tolist() + [df.columns[-1]]
    df_channels = df[columns_to_select]
     
    # Extract the filename from the complete path and create output path
    filename = os.path.basename(file_path)
    output_file_path_channels = os.path.join(os.path.dirname(file_path), filename.replace('.csv', '_channels.csv'))
    
    # Save the modified DataFrame to the new CSV file
    #df_channels.to_csv(output_file_path_channels, index=False)

    return df_channels

def raw_mne(df_channels):

    ch_types=["eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "stim"]

    ch_names = ['FC1', 'FCz', 'FC2', 'C3', 'C4', 'CP1', 'CPz', 'CP2', 'STI']

    sfreq = 250

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    montage = mne.channels.make_standard_montage("standard_1020")
    info.set_montage(montage = montage)
    array = df_channels.iloc[:,1:10].to_numpy()
    data = np.transpose(array)
    raw = mne.io.RawArray(data, info)

    #Scale correction
    raw.apply_function(lambda x: x*1e-7, picks="eeg")

    #CAR
    #raw.set_eeg_reference("average")
    
    #Info
    n_time_samps = raw.n_times
    time_secs = raw.times
    ch_names = raw.ch_names
    n_chan = len(ch_names)  # note: there is no raw.n_channels attribute
    print(
        f"the (cropped) sample data object has {n_time_samps} time samples and "
        f"{n_chan} channels."
    )
    print(f"The last time sample is at {time_secs[-1]} seconds.")
    print("The first few channel names are {}.".format(", ".join(ch_names[:3])))
    print()  # insert a blank line in the output

    # some examples of raw.info:
    print("bad channels:", raw.info["bads"])  # chs marked "bad" during acquisition
    print(raw.info["sfreq"], "Hz")  # sampling frequency
    print(raw.info["description"], "\n")  # miscellaneous acquisition info

    print(raw.info)

    return raw


def filtering(raw, alpha = False, plots = False):

    #bandpass
    if alpha:
        low_cut = 8
        hi_cut  = 13
    else:
        low_cut = 0.1
        hi_cut  = 30

    raw_filt = raw.copy().filter(low_cut, hi_cut)

    #notch
    eeg_picks = mne.pick_types(raw_filt.info, eeg=True)
    raw_notch = raw_filt.copy().notch_filter(freqs = (50,100), picks = eeg_picks)

    #CAR
    raw_car = raw_notch.copy().set_eeg_reference("average")

    #Visualization
    if plots:
        raw.compute_psd().plot()
        #raw_filt.compute_psd().plot()
        #raw_notch.compute_psd().plot()
        raw_car.compute_psd().plot()

        raw.plot(start=15, duration=5)
        #raw_filt.plot(start=15, duration=5)
        #raw_notch.plot(start=15, duration=5, picks = ['eeg'])
        raw_car.plot(start=15, duration=5, picks = ['eeg'])

        plt.show()

    return raw_notch

def clean_artifacts(epochs, plots = False):


    # ICA parameters
    random_state = 42   # ensures ICA is reproducible each time it's run
    ica_n_components = .99     # Specify n_components as a decimal to set % explained variance

    # Fit ICA
    ica = mne.preprocessing.ICA(n_components=ica_n_components,
                                random_state=random_state,
                                )
    ica.fit(epochs)

    ica.exclude = []
    num_excl = 0
    max_ic = 2
    z_thresh = 3.5
    z_step = .05

    while num_excl < max_ic:
        eog_indices, eog_scores = ica.find_bads_eog(epochs,
                                                    ch_name=['FC1', 'FC2', 'FCz'], 
                                                    threshold=z_thresh
                                                    )
        num_excl = len(eog_indices)
        z_thresh -= z_step # won't impact things if num_excl is ≥ n_max_eog 

    # assign the bad EOG components to the ICA.exclude attribute so they can be removed later
    ica.exclude = eog_indices

    epochs_ica = ica.apply(epochs.copy())

    ar = AutoReject(n_interpolate=[1, 2, 4],
                random_state=42,
                picks=mne.pick_types(epochs_ica.info, 
                                     eeg=True,
                                     eog=False
                                    ),
                n_jobs=-1, 
                verbose=False
                )

    epochs_clean, reject_log_clean = ar.fit_transform(epochs_ica, return_log=True)

    if plots:
        #fig, ax = plt.subplots(figsize=[10, 4])
        #reject_log_clean.plot('horizontal', aspect='auto', ax=ax)

        #ica.plot_components()

        #ica.plot_properties(epochs, picks=range(0, ica.n_components_), psd_args={'fmax': 30})

        #ica.plot_scores(eog_scores)

        fig, ax = plt.subplots(1, 2, figsize=[12, 3])
        epochs['both'].average().plot(axes=ax[0], ylim=[-11, 10], show=False)
        epochs_ica['both'].average().plot(axes=ax[1], ylim=[-11, 10])

        fig, ax = plt.subplots(1, 2, figsize=[12, 3])
        epochs['both'].average().plot(axes=ax[0], show=False) # remember the semicolon prevents a duplicated plot
        epochs_clean['both'].average().plot(axes=ax[1])

        plt.show()

def map_event(data, plots = False):

    events = mne.find_events(data, stim_channel="STI")

    event_dict = {
    "right": 1,
    "left": 2,
    "both": 3}

    if plots:
        data.plot(
        events=events,
        start=5,
        duration=10,
        color="gray",
        event_color={1: "r", 2: "g", 3: "b"})

        mne.viz.plot_events(events, sfreq=data.info["sfreq"], first_samp=data.first_samp, event_id=event_dict)

    return events,event_dict

def make_epochs(data, events, events_dict):

    epochs = mne.Epochs(
    data,
    events,
    event_id=events_dict,
    tmin=-0.5,
    tmax=5,
    baseline=(None, 0),
    preload=True)

    conditions = list(events_dict.keys())

    return epochs,conditions


def avg_epochs(epochs, conditions):

    evokeds = {c:epochs[c].average() for c in conditions}

    evokeds

    #for c in evokeds.keys():
        #evokeds[c].plot_joint(title=c)

    mne.viz.plot_compare_evokeds(evokeds, picks='CPz', show_sensors='lower center',
                                    legend='lower right')

    # define the channels we want plots for
    #channels = ['FC1', 'FCz', 'FC2', 'C3', 'C4', 'CP1', 'CPz', 'CP2']
    channels = ['FC1', 'FCz', 'FC2', 'C3']

    # create a figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))

    # plot each channel in a separate subplot
    for idx, chan in enumerate(channels):
        mne.viz.plot_compare_evokeds(evokeds, 
                                    picks=chan,
                                    ylim={'eeg':(-150, 150)},
                                    show_sensors='lower right',
                                    legend='upper right',
                                    axes=axes.reshape(-1)[idx],
                                    show=False
                                    )
        
    channels = ['C4', 'CP1', 'CPz', 'CP2']

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))

    for idx, chan in enumerate(channels):
        mne.viz.plot_compare_evokeds(evokeds, 
                                    picks=chan,
                                    ylim={'eeg':(-150, 150)},
                                    show_sensors='lower right',
                                    legend='upper right',
                                    axes=axes.reshape(-1)[idx],
                                    show=False
                                    )


    plt.show()    

    return evokeds


def export_matlab(raw_data):

    mne.export.export_raw("./test.set", raw_data, fmt='eeglab')


def psd(raw_data):

    raw_data.compute_psd().plot()

    plt.show()

    return


def main():

    plots = True

    file_path = sys.argv[1]
    if len(sys.argv) > 2: #For old format 
        old_format = sys.argv[2]
        raw_data = raw_mne(only_eeg(file_path,old_format))
    else:
        raw_data = raw_mne(only_eeg(file_path))

    filtered_data = filtering(raw_data, plots = True)
    events, events_dict = map_event(filtered_data)
    epochs, conditions = make_epochs(filtered_data, events, events_dict)
    #clean_artifacts(epochs, plots = plots)
    #evoked = avg_epochs(epochs, conditions)

if __name__ == '__main__':
    main()