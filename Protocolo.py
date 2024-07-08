
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

from test_connect import test_connect, test_get_device_by_name, test_play_action
from android_vr import android_connect, start_vr, stop_vr
from movie_editor import vr_maker


def check_and_rename(file_path, add = 0):

    original_file_path = file_path
    if add != 0:
        split = file_path.rsplit(".", 1)
        part_1 = split[0] + "_" + str(add)
        file_path = ".".join([part_1, split[1]])
    if not os.path.isfile(file_path):
        return file_path
    else:
        return check_and_rename(original_file_path, add + 1)


def robot_connect():

    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU) #tipo de robot
    #Encontrar robot (device) en la red WiFi:
    device_robot: WiFiDevice = asyncio.get_event_loop().run_until_complete(test_get_device_by_name())
    if device_robot: #Si lo encuentra, se conecta
        asyncio.get_event_loop().run_until_complete(test_connect(device_robot))
        return True
    else:
        messagebox.showerror(title="Conection error", message = "Alphamini está desconectado")
        return False


def record_data(duration, inlet, fs = 250):
    columns = ['Time',"FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2", 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']
    data_dict = dict((k, []) for k in columns)
    finished = False
    while not finished:

        data, timestamp = inlet.pull_sample()
        #print("got %s at time %s" % (data[0], timestamp))
        timestamp = datetime.fromtimestamp(psutil.boot_time() + timestamp)
        #The timestamp you get is the seconds since the computer was turned on,
        #so we add to the timestamp the date when the computer was started (psutil.boot_time())
        all_data = [timestamp] + data

        rep = 0
        for key in list(data_dict.keys()):
            data_dict[key].append(all_data[rep])
            rep = rep + 1
        
        if len(data_dict['Time']) >= fs*duration:
            finished = True

    return data_dict


def play_video_3(videopath, end = False):

    clip = VideoFileClip(videopath, target_resolution=(720,1280))
    clip.preview(fullscreen = True)

    if end:
        pygame.quit()

def play_audio(audiopath):
    
    audio = AudioSegment.from_file(audiopath)
    play(audio)


def arm_setup(n_rep, random_order = True):
    movements = list()

    # Agregamos "izquierdo", "derecho" y "ambos" 
    for rep in range(n_rep):
        if rep < (n_rep/3):
            movements.append("left")
        elif rep >=(n_rep/3) and rep<((2*n_rep)/3):
            movements.append("right")
        else:
            movements.append("both")
    
    if random_order == True: # Mezclamos aleatoriamente la lista
        random.shuffle(movements)
    
    return movements


def relax_protocol(inlet, protocol_type, relax_time = 5, start = True):

    if start:
        if protocol_type == 'control':
            play_video_3('./Media/Comienzo.mp4')
        elif protocol_type == ('video' or 'robot'):
            play_video_3('./Media/Comienzo_detalle.mp4')
        else:
            pass
    else:
        if protocol_type == 'control':
            play_video_3('./Media/Relax.mp4')
        else:
            pass

    print('Inicio relax '+datetime.now().strftime('%Y%m%d%H%M'))
    data_dict = record_data(relax_time, inlet)
    df_relax = pd.DataFrame.from_dict(data_dict)
    df_relax['STI'] = 0 #Relax label for the data
    print('Fin relax '+datetime.now().strftime('%Y%m%d%H%M'))

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
        play_video_3('./Media/alphamini_right_front.mp4')
    elif mov == 'left':
        play_video_3('./Media/alphamini_left_front.mp4')
    else:
        play_video_3('./Media/alphamini_both_front.mp4')  


def vr_protocol(movements_list, device = None):
    
    if type(movements_list) is list:
        vr_maker(movements_list)
        start_vr(device)
        time.sleep(24)
    else:
        pass
        

def base_protocol(inlet, protocol_type, n_rep):

    movements_list = arm_setup(n_rep)

    #Connections
    if protocol_type == 'robot':
        if not robot_connect():
            return
    elif protocol_type == 'vr':
        adb_ready, adb_device = android_connect()
        if not adb_ready:
            return
        else:
            vr_protocol(movements_list, adb_device)

    #Protocol Initiation
    df_list = [relax_protocol(inlet, protocol_type, relax_time = 5)]      
        
    #Choosen Protocol Execution
    options = {'control': control_protocol, 
            'robot': robot_protocol, 
            'video': video_protocol,
            'vr': vr_protocol}
    
    record_times = {'control': 10, 
            'robot': 5, 
            'video': 5, 
            'vr': 5}

    for rep in range(len(movements_list)):
    
        df_iter= f"df_{rep}"

        options.get(protocol_type)(movements_list[rep])
        data_dict = record_data(record_times.get(protocol_type), inlet)
        globals()[df_iter] = pd.DataFrame.from_dict(data_dict)

        if movements_list[rep] == 'right':
            
            globals()[df_iter]['STI'] = 1 #right_label
            df_list.append(globals()[df_iter])
            print("dch anotado")
            
        elif movements_list[rep]=='left':

            globals()[df_iter]['STI'] = 2 #left label
            df_list.append(globals()[df_iter])
            print("izq anotado")

        elif movements_list[rep]=='both':
            
            globals()[df_iter]['STI'] = 3 #both label
            df_list.append(globals()[df_iter])
            print("ambos anotados")
        
        df_relax = relax_protocol(inlet, protocol_type, relax_time = 4, start = False)
        df_list.append(df_relax)

        if rep == (n_rep -1):
            if protocol_type == "vr":
                time.sleep(5)
                stop_vr(adb_device)
            else:
                play_video_3("./Media/Fin.mp4", end = True)

    complete_df = pd.concat(df_list, ignore_index=True)
    complete_df.columns = ['Time', 'FC1', 'FC2', 'C3', 'C1', 'C2', 'C4', 'CP1', 'CP2', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation', 'STI']
    df_name = check_and_rename('./Results/{p}/{p}_{i}.csv'.format(p = protocol_type,i = id))
    complete_df.to_csv(df_name, index=False)
    print(df_name + ' saved!')


def main():

    #####################
    #Protocol parameters#
    #####################
    relax_time = 5 #Initial relax seconds
    record_time = 10 #Motor imagery seconds
    left_electrodes = ['FC1', 'C3', 'C1', 'CP1']
    right_electrodes = ['FC2', 'C4', 'C2', 'CP2']
    included_electrodes = ["FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2"]
    fs = 250

    global n_rep
    n_rep = 3 #Number of Imagery-Execution 

    global id
    id = "test"

    ####################
    #Unicorn connection#
    ####################
    try:
        streams = resolve_stream()
        inlet = StreamInlet(streams[0])
    except:
        messagebox.showerror(title="Conection error", message = "Unicorn Brain Interface está desconectado")
        sys.exit(1)

    ##########################
    #Graphical User Interface#
    ##########################

    root = tk.Tk()
    root.geometry("300x600+600+100")
    root.title("Protocol GUI")

    def save_id():
        
        #Date
        fecha = []
        today = date.today()
        fecha.append(today.day)
        fecha.append(today.month)
        fecha.append(today.year)
        fecha_str = ''.join(map(str, fecha)) #fecha actual en string (e.g. 10122022)
        
        global id
        id = '{}_{}'.format(id_entry.get(),fecha_str)
        # Aquí podrías guardar el ID en una variable o archivo para su posterior uso
        print(f"ID guardado: {id}")


    b1_style = ttk.Style()
    b1_style.configure('TButton', font =
               ('calibri', 20),
                    borderwidth = '4')
    b1_style.map('TButton', foreground = [('active', '!disabled', 'blue')],
                     background = [('active', 'black')])
    
    b2_style = ttk.Style()
    b2_style.configure('B2.TButton', font =
            ('calibri', 20),
            borderwidth = '3')
    b2_style.map('B2.TButton', foreground = [('active', '!disabled', 'green')],
                    background = [('active', 'black')])
    
    b3_style = ttk.Style()
    b3_style.configure('B3.TButton', font =
            ('calibri', 12),
            borderwidth = '3')
    b3_style.map('B3.TButton', foreground = [('active', '!disabled', 'red')],
                    background = [('active', 'black')])

    #Create the widgets
    id_label = tk.Label(root,
        text ="Input the ID\nin the box below:", font = ('calibri', 20))
    id_entry = tk.Entry(root, width=40, font=('calibri', 15))
    save_button = ttk.Button(root, text="Save ID",style="B2.TButton", command=save_id)
  
    protocol_label = tk.Label(root, text="Select the protocol\n to record:", font=('calibri', 20))

    button1 = ttk.Button(root, text="Control",style="TButton", command = lambda: [base_protocol(inlet, "control", n_rep)])
    button2 = ttk.Button(root, text="Robot",style="TButton", command = lambda: [base_protocol(inlet, "robot", n_rep)])
    button3 = ttk.Button(root, text="Video",style="TButton", command = lambda: [base_protocol(inlet, "video", n_rep)])
    button4 = ttk.Button(root, text="VR",style="TButton", command = lambda: [base_protocol(inlet, "vr", n_rep)])
    
    exit_button = ttk.Button(root, text="Exit", style="B3.TButton",command = root.destroy)

    # Pack the widgets vertically
    id_label.pack(pady = 10)
    id_entry.pack(pady = 10, padx = 50)
    save_button.pack(pady = 10)

    protocol_label.pack(pady=7)
    button1.pack(pady = 7)
    button2.pack(pady = 7)
    button3.pack(pady = 7)
    button4.pack(pady = 7)
    exit_button.pack(pady = 25)

    root.mainloop()


if __name__ == '__main__':
    main()





