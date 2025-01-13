import os
import sys
import time
import asyncio
import random
from datetime import date, datetime

import subprocess
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

from utils import play_video_3, play_audio, Recorder
from test_connect import test_connect, test_get_device_by_name, test_play_action
from android_vr import android_connect, start_vr, stop_vr


def relax_protocol(inlet, protocol_type, ENG, relax_time = 10, start = True):

    print('Empieza el protocolo relax'+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    if start:
        if protocol_type == 'control':
            if ENG:
                wait_time = play_video_3('./Media/ENG_control_comienzo.mp4')
            else:
                wait_time = play_video_3('./Media/control_comienzo.mp4')
        elif protocol_type == 'video':
            if ENG:
                wait_time = play_video_3('./Media/ENG_nao_comienzo.mp4')
            else:
                wait_time = play_video_3('./Media/nao_comienzo.mp4')
        elif protocol_type == 'robot':
            if ENG:
                move_command = "py -2 nao_controls.py --mode 1 --sound inicio --english True"  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
            else:
                move_command = "py -2 nao_controls.py --mode 1 --sound inicio"  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
            time.sleep(24)
        else:
            time.sleep(23)
    else:
        pass

    relax_recorder = Recorder(inlet,relax_time)
    relax_recorder.start()

    print('Inicio grabación relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    time.sleep(relax_time+0.1)

    print('Fin grabación relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    data_dict = relax_recorder.data_dict
    df_relax = pd.DataFrame.from_dict(data_dict)
    df_relax['STI'] = 0 #Relax label for the data

    del relax_recorder

    if start:
        time.sleep(3.25)
        if protocol_type == 'control':
            if ENG:
                play_video_3('./Media/ENG_control_vamosacomenzar.mp4')
            else:
                play_video_3('./Media/control_vamosacomenzar.mp4')
            time.sleep(3.8)
        elif protocol_type == 'video':
            if ENG:
                play_video_3('./Media/ENG_nao_vamosacomenzar.mp4')
            else:
                play_video_3('./Media/nao_vamosacomenzar.mp4')
            time.sleep(3.8)
        elif protocol_type == 'robot':
            if ENG:
                move_command = "py -2 nao_controls.py --mode 1 --sound acomenzar --english True"  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
            else:
                move_command = "py -2 nao_controls.py --mode 1 --sound acomenzar"  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
            time.sleep(6)
        else:
            time.sleep(6) #3.25 + 6 = 9 para adecuarse a los tempos del protocolo VR      
    else:
        pass

    print('Fin protocolo relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    return df_relax


def control_protocol(mov, ENG):

    if ENG:
        if mov == 'right':
            play_video_3('./Media/ENG_control_right.mp4')
        elif mov == 'left':
            play_video_3('./Media/ENG_control_left.mp4')
        else:
            play_video_3('./Media/ENG_control_both.mp4')
    else:
        if mov == 'right':
            play_video_3('./Media/control_right.mp4')
        elif mov == 'left':
            play_video_3('./Media/control_left.mp4')
        else:
            play_video_3('./Media/control_both.mp4')


    
def robot_protocol(mov, ENG):

    if mov == 'right':
        move_command = "py -2 nao_controls.py --mode 2 --move right"  # launch your python2 script
        process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
    elif mov == 'left':
        move_command = "py -2 nao_controls.py --mode 2 --move left"  # launch your python2 script
        process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
    else:
        move_command = "py -2 nao_controls.py --mode 2 --move both"  # launch your python2 script
        process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)


def video_protocol(mov, ENG):

    if mov == 'right':
        play_video_3('./Media/nao_right_sound.mp4')
    elif mov == 'left':
        play_video_3('./Media/nao_left_sound.mp4')
    else:
        play_video_3('./Media/nao_both_sound.mp4')  


def vr_protocol(mov, ENG):
    pass

def main():
    pass

if __name__ == '__main__':
    main()




