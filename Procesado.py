
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
from mne.channels import read_layout
from mne.time_frequency import psd_array_welch
from mne.time_frequency import tfr_multitaper
from mne.stats import permutation_cluster_1samp_test as pcluster_test
from brainflow.board_shim import BoardShim, BrainFlowInputParams

def get_args():
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file_path', help = 'Path to the file to process', type = str)

    parser.add_argument('format_type', help = 'Path to the file to process', type = str, default= False)

    #parser.add_argument('output_path', help = 'Path to save the processed file', type = str)

    return parser.parse_args()


def only_eeg(file_path, format):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    if format:
        #Change 'Time' to datetime type and then calculate the difference
        df['Time'] = pd.to_datetime(df['Time'])
        df['Time'] = ((df['Time'] - df['Time'].min()) / np.timedelta64(1,'D'))*1e7
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
    df_channels.to_csv(output_file_path_channels, index=False)

    return df_channels

def raw_mne(df_channels, file_path):

    ch_types=["eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "stim"]

    ch_names = ['FC1', 'FC2', 'C3', 'C1', 'C2', 'C4', 'CP1', 'CP2', 'STI']

    sfreq = 250

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    montage = mne.channels.make_standard_montage("standard_1020")
    info.set_montage(montage = montage)
    array = df_channels.iloc[:,1:10].to_numpy()
    data = np.transpose(array)
    raw = mne.io.RawArray(data, info)
    
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

def main():

    args = get_args()

    file_path = args.file_path
    format = args.format_type

    raw_mne(only_eeg(file_path,format), file_path)

if __name__ == '__main__':
    main()