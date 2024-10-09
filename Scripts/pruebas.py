from subprocess import Popen,PIPE

import os
import sys
import time
import asyncio
import random
from datetime import date, datetime
import threading

import psutil
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

        return self.data_dict

def play_video_3(videopath, end = False):

    clip = VideoFileClip(videopath, target_resolution=(720,1280))
    clip.preview()

    duration = clip.duration

    if end:
        pygame.quit()

    return duration

def play_audio(audiopath):
    
    audio = AudioSegment.from_file(audiopath)
    play(audio)

    return audio.duration_seconds


def relax_protocol(inlet, protocol_type, relax_time = 10, start = True):

    if start:
        if protocol_type == 'control':
            wait_time = play_video_3('../Media/Comienzo_control.mp4')
        elif protocol_type == 'video':
            play_video_3('../Media/Comienzo_video.mp4')
        elif protocol_type == 'robot':
            wait_time = play_audio('../Media/Comienzo.mp3')
        else:
            pass
    else:
        pass

    print("klk")
    #time.sleep(wait_time)

    relax_recorder = Recorder(inlet,relax_time)
    relax_recorder.start()

    print('Inicio relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    time.sleep(relax_time+0.1)

    print('Fin relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    data_dict = relax_recorder.data_dict
    df_relax = pd.DataFrame.from_dict(data_dict)
    df_relax['STI'] = 4 #Relax label for the data

    if start:
        if protocol_type == ('control' or 'robot'):
            play_audio('../Media/vamos_a_comenzar.m4a')
        elif protocol_type == 'video':
            play_video_3('../Media/vamos_a_comenzar.mp4')
        else:
            pass
    else:
        pass

    return df_relax

def main():
    inlet = []
    dict = relax_protocol(inlet, 'video', relax_time = 10, start = True)
    print(dict)

if __name__ == '__main__':
    main()
