
import os
import sys
import time
import asyncio
import random
from datetime import date, datetime
import json
import threading

import shutil
import pandas as pd
import matplotlib.pyplot as plt 
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
#import cv2 as cv
import pygame
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.playback import play
from pylsl import StreamInlet, resolve_stream

import mini.mini_sdk as MiniSdk
from mini.apis import *
from mini.dns.dns_browser import WiFiDevice

from test_connect import test_connect, test_get_device_by_name, test_play_action
from android_vr import android_connect, start_vr, stop_vr
from movie_editor import vr_maker


class Recorder(threading.Thread):

    columns = ['Time','FC1','FC2','C3','C1','C2','C4','CP1','CP2', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']
    data_dict = dict((k, []) for k in columns)
    
    def __init__(self, inlet, duration = 10, fs = 250):
        super(Recorder,self).__init__()
        self.inlet = inlet
        self.duration = duration
        self.fs = fs

    def run(self):
        
        finished = False
        while not finished:

            data, timestamp = self.inlet.pull_sample()
            #print("got %s at time %s" % (data[0], timestamp))
            #timestamp = datetime.fromtimestamp(psutil.boot_time() + timestamp)
            #The timestamp you get is the seconds since the computer was turned on,
            #so we add to the timestamp the date when the computer was started (psutil.boot_time())

            all_data = [timestamp] + data

            rep = 0
            for key in list(self.data_dict.keys()):
                self.data_dict[key].append(all_data[rep])
                rep = rep + 1
            
            if len(self.data_dict['Time']) >= self.fs*self.duration:
                finished = True

        return
    

def check_and_rename(file_path, add = 0):

    original_file_path = file_path
    if add != 0:
        split = file_path.rsplit('.', 1)
        part_1 = split[0] + '_' + str(add)
        file_path = '.'.join([part_1, split[1]])
    if not os.path.isfile(file_path):
        return file_path
    else:
        return check_and_rename(original_file_path, add + 1)
    
    
    
def play_video_3(videopath, end = False):

    clip = VideoFileClip(videopath, target_resolution=(720,1280))
    clip.preview(fullscreen = True)
    #clip.preview()

    duration = clip.duration

    if end:
        pygame.quit()

    return duration


def play_audio(audiopath):
    
    audio = AudioSegment.from_file(audiopath)
    play(audio)

    return audio.duration_seconds


def arm_setup(n_rep):
    movements = list()

    # Agregamos "izquierdo", "derecho" y "ambos" 
    for rep in range(n_rep):
        if rep < (n_rep/3):
            movements.append('left')
        elif rep >=(n_rep/3) and rep<((2*n_rep)/3):
            movements.append('right')
        else:
            movements.append('both')
    
    while True:
        # Shuffle the list randomly
        random.shuffle(movements)

        # Check if the list meets the constraint of no more than two consecutive elements of the same type
        valid = True
        for i in range(len(movements) - 2):
            if movements[i] == movements[i+1] == movements[i+2]:
                valid = False
                break
        if valid:
            return movements
        

def robot_connect():

    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU) #tipo de robot
    #Encontrar robot (device) en la red WiFi:
    device_robot: WiFiDevice = asyncio.get_event_loop().run_until_complete(test_get_device_by_name())
    if device_robot: #Si lo encuentra, se conecta
        asyncio.get_event_loop().run_until_complete(test_connect(device_robot))
        return True
    else:
        messagebox.showerror(title='Conection error', message = 'Alphamini está desconectado')
        return False
