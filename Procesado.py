
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

    parser.add_argument('protocol', help = 'Choose the protocol to be analysed: control,robot,video,VR', type = str)

    parser.add_argument('id', help = 'Choose the id to be analysed', type = str)

    return parser.parse_args()

def main():

    args = get_args()
    
    dataframe = pd.read_csv()

    pass

if __name__ == '__main__':
    main()