import os
import sys
import time
import asyncio
import random
from datetime import date, datetime

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
from movie_editor import vr_maker

def relax_protocol(inlet, protocol_type, relax_time = 10, start = True):

    print('Empieza el protocolo relax'+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    if start:
        if protocol_type == 'control':
            wait_time = play_video_3('./Media/comienzo_control.mp4')
        elif protocol_type == 'video':
            wait_time = play_video_3('./Media/comienzo_mini.mp4')
        elif protocol_type == 'robot':
            wait_time = play_audio('./Media/comienzo.mp3')
        else:
            pass
    else:
        pass

    #time.sleep(wait_time)

    relax_recorder = Recorder(inlet,relax_time)
    relax_recorder.start()

    print('Inicio grabación relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    time.sleep(relax_time+0.1)

    print('Fin grabación relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    data_dict = relax_recorder.data_dict
    df_relax = pd.DataFrame.from_dict(data_dict)
    df_relax['STI'] = 4 #Relax label for the data

    del relax_recorder

    if start:
        time.sleep(3.25)
        if protocol_type == ('control' or 'robot'):
            play_audio('./Media/vamos_a_comenzar.mp3')
        elif protocol_type == 'video':
            play_video_3('./Media/vamos_a_comenzar.mp4')
        else:
            pass
        time.sleep(6) #3.25 + 6 = 9 para adecuarse a los tempos del protocolo VR
    else:
        pass

    print('Fin protocolo relax '+datetime.now().strftime('%Y%m%d%H%M')+'\n')

    return df_relax


def control_protocol(mov):
    
    if mov == 'right':
        play_video_3('./Media/Imagina_dch.mp4')
    elif mov == 'left':
        play_video_3('./Media/Imagina_izq.mp4')
    else:
        play_video_3('./Media/Imagina_ambos.mp4')

    
def robot_protocol(mov):

    if mov == 'right':
        asyncio.get_event_loop().run_until_complete(test_play_action('face_028b'))
    elif mov == 'left':
        asyncio.get_event_loop().run_until_complete(test_play_action('Surveillance_004'))
    else:
        asyncio.get_event_loop().run_until_complete(test_play_action('random_short5'))


def video_protocol(mov):

    if mov == 'right':
        play_video_3('./Media/alphamini_right_sound.mp4')
    elif mov == 'left':
        play_video_3('./Media/alphamini_left_sound.mp4')
    else:
        play_video_3('./Media/alphamini_both_sound.mp4')  


def vr_protocol():
    pass

def main():
    pass

if __name__ == '__main__':
    main()




