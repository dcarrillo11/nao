import os
import sys
import time
import asyncio
import random
from datetime import date, datetime
import json
import threading
import argparse

import shutil
import pandas as pd
import matplotlib.pyplot as plt 
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
#import cv2 as cv
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.playback import play
from pylsl import StreamInlet, resolve_stream

import mini.mini_sdk as MiniSdk
from mini.apis import *
from mini.dns.dns_browser import WiFiDevice

from utils import *
from protocolos import *
from test_connect import test_connect, test_get_device_by_name, test_play_action
from android_vr import android_connect, start_vr, stop_vr

def get_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('user', help='User ID to remove')
    args = parser.parse_args()

    return args.user

def main():

    user_id = get_args()

    with open('participants.json', 'r') as file:
        participants = json.load(file)

    path = './Results/{p}/'.format(p = user_id)

    if user_id in participants.keys() and os.path.exists(path):
        shutil.rmtree(path)
        removed_key = participants.pop(user_id)
        with open('participants.json', 'w') as file:
            json.dump(participants, file)
    else:
        print("No existe un usuario con ese id, esta es la lista de usuarios:")
        [print("-",x) for x in participants.keys()]


if __name__ == '__main__':
    main()
