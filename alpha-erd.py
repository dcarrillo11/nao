
import os
import sys
import time
import asyncio
import random
from datetime import date, datetime
import json
import threading

import subprocess
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

from utils import *
from protocolos import *
from test_connect import test_connect, test_get_device_by_name, test_play_action
from android_vr import android_connect, start_vr, stop_vr
        

def participant_setup(clicked_id, n_rep):

    global newid_flag

    if not newid_flag:
        id = clicked_id.get()
        print(id)
    else:
        id = newid
        newid_flag = False
        print(newid, newid_flag)

    with open('participants.json', 'r') as file:
        participants = json.load(file)

    if id in participants.keys():
        movements_list = participants[id][0]
    else:
        movements_list = arm_setup(n_rep)
        last_key =  list(participants.keys())[-1]
        participants[id] = [movements_list, (participants[last_key][1] + 1)]
        with open('participants.json', 'w') as file:
            json.dump(participants, file)

        path = './Results/{p}/'.format(p = id)
        os.mkdir(path)
    
    return id, movements_list


def base_protocol(inlet, protocol_type, n_rep, clicked_id, ENG):

    id, movements_list = participant_setup(clicked_id, n_rep)
    
    #Connections
    if protocol_type == 'robot':
        connect_command = "py -2 nao_controls.py --mode 0"  # launch python2 script
        process = subprocess.Popen(connect_command.split(), stdout=subprocess.PIPE, text = True)
        output, error = process.communicate() # receive output from the python2 script
        connection_flag = output.strip().split('\n')[-1]
        if connection_flag == 'False':
            messagebox.showerror(title='Conection error', message = 'NAO está desconectado')
            return
    elif protocol_type == 'vr':
        #vr_flag, vr_device = android_connect()
        #shutil.copy('./participants.json', '../verge3d/alphamini/participants.json')
        #f = open('../verge3d/alphamini/user.txt', 'w')
        #f.write(id)
        #f.close()
        messagebox.askokcancel(title='Virtual Reality Protocol', message= 'Press OK to start the recording')
    else:
        pass

    #Protocol Initiation
    df_list = [relax_protocol(inlet, protocol_type, ENG, relax_time = 10)]
   
    #Choosen Protocol Execution
    options = {'control': control_protocol, 
            'robot': robot_protocol, 
            'video': video_protocol,
            'vr': vr_protocol}
    
    record_time = 4.05

    for rep in range(len(movements_list)):
    
        df_iter = f'df_{rep}'

        session_recorder = Recorder(inlet, record_time)
        session_recorder.start()
        print('Empiezo a anotar (' + str(rep) +')')
        options.get(protocol_type)(movements_list[rep], ENG)
        time.sleep(record_time + 0.1)

        data_dict = session_recorder.data_dict
        globals()[df_iter] = pd.DataFrame.from_dict(data_dict)

        del session_recorder

        if movements_list[rep] == 'right':
            
            globals()[df_iter]['STI'] = 1 #right_label
            df_list.append(globals()[df_iter])
            print('dch anotado\n')
            
        elif movements_list[rep]=='left':

            globals()[df_iter]['STI'] = 2 #left label
            df_list.append(globals()[df_iter])
            print('izq anotado\n')

        elif movements_list[rep]=='both':
            
            globals()[df_iter]['STI'] = 3 #both label
            df_list.append(globals()[df_iter])
            print('ambos anotados\n')
        
        df_relax = relax_protocol(inlet, protocol_type, ENG, relax_time = 5, start = False)
        df_list.append(df_relax)

        if rep == (n_rep -1):
            if protocol_type == 'control':
                if ENG:
                    play_video_3('./Media/ENG_control_fin.mp4', end = True)
                else:
                    play_video_3('./Media/control_fin.mp4', end = True)
            elif protocol_type == 'video':
                if ENG:
                    play_video_3('./Media/ENG_nao_fin.mp4', end = True)
                else:
                    play_video_3('./Media/nao_fin.mp4', end = True)
            elif protocol_type == 'robot':
                if ENG:
                    move_command = "py -2 nao_controls.py --mode 1 --sound fin --english True"  # launch your python2 script
                    process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
                else:
                    move_command = "py -2 nao_controls.py --mode 1 --sound fin"  # launch your python2 script
                    process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
            else:
                pass


    complete_df = pd.concat(df_list, ignore_index=True)
    complete_df.columns = ['Time', 'FC1', 'FCz', 'FC2', 'C3', 'C4', 'CP1', 'CPz', 'CP2', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation', 'STI']
    df_name = check_and_rename('./Results/{i}/{i}_{p}.csv'.format(p = protocol_type,i = id))
    complete_df.to_csv(df_name, index=False)
    print(df_name + ' saved!')


def main():

    #####################
    #Protocol parameters#
    #####################

    ENG = False #Modo ingles

    left_electrodes = ['FC1', 'C3', 'C1', 'CP1']
    right_electrodes = ['FC2', 'C4', 'C2', 'CP2']
    included_electrodes = ['FC1', 'FC2', 'C3', 'C1', 'C2', 'C4', 'CP1', 'CP2']
    fs = 250
    n_rep = 15 #Number of Imagery-Execution

    global newid_flag
    newid_flag = False

    #Participants
    if not os.path.isfile('participants.json'):
        participants = {'test' : [['both', 'left', 'right'],0]}
        with open('participants.json', 'w') as file:
            json.dump(participants, file)
    else:
        with open('participants.json', 'r') as file:
            participants = json.load(file)

    ####################
    #Unicorn connection#
    ####################

    try:
        streams = resolve_stream()
        inlet = StreamInlet(streams[0])
    except:
        messagebox.showerror(title='Conection error', message = 'Unicorn Brain Interface está desconectado')
        sys.exit(1) 

    ##########################
    #Graphical User Interface#
    ##########################

    root = tk.Tk()
    root.geometry('300x650+600+100')
    root.title('Protocol GUI')

    def openIDwindow():

        def save_newid():
            
            #Usar la keyword global es la unica manera de sacar una variable de esta función. 
            global newid
            newid = (id_entry.get()).lower()
            path = './Results/{p}/'.format(p = newid)
            if not os.path.exists(path):
                global newid_flag
                newid_flag = True
                print(newid_flag)
                print(f'ID guardado: {newid}')
            else:
                messagebox.showerror(title='ID error', message = 'El usuario %s ya existe' %newid)

            IDWindow.destroy()

        IDWindow = tk.Toplevel(root)
 
        IDWindow.title('New ID')
    
        # sets the geometry of toplevel
        IDWindow.geometry('300x220')
    
        newid_label = tk.Label(IDWindow,text ='Input the ID\nin the box below:', font = ('calibri', 20))
        id_entry = tk.Entry(IDWindow, width=40, font=('calibri', 15))
        save_button = ttk.Button(IDWindow, text='Save ID',style='B2.TButton', command=save_newid)

        newid_label.pack(pady = 10)
        id_entry.pack(pady = 10, padx = 50)
        save_button.pack(pady = 10)

    def refreshUser(drop, options, clicked_id):

        options = list(options)
        options.append(newid)
        options.sort()
        menu = drop['menu']
        menu.delete(0,'end')
        for i in options:
            menu.add_command(label=i,command=lambda val=i: clicked_id.set(val))

    
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
    
    b4_style = ttk.Style()
    b4_style.configure('B4.TButton', font =
               ('calibri', 12),
                    borderwidth = '3')
    b4_style.map('B4.TButton', foreground = [('active', '!disabled', 'blue')],
                     background = [('active', 'black')])

    #Dropdown Menu config
    options = sorted(participants.keys())
    clicked_id = tk.StringVar() 
    clicked_id.set('test') 
    
    #Create the widgets
    id_label = tk.Label(root,text ='Select the ID:', font = ('calibri', 20))
    drop = tk.OptionMenu( root , clicked_id , *options)
    drop.config(width = 6, font = ('calibri', 20), bg = 'gainsboro')
    newid_button = ttk.Button(root, text='New ID',style='B2.TButton', command=openIDwindow)
    refresh_button = ttk.Button(root, text='Refresh',style='B4.TButton', command= lambda: [refreshUser(drop, options, clicked_id)])
   
    protocol_label = tk.Label(root, text='Select the protocol\n to record:', font=('calibri', 20))

    button1 = ttk.Button(root, text='Control',style='TButton', command = lambda: [base_protocol(inlet, 'control', n_rep, clicked_id, ENG)])
    button2 = ttk.Button(root, text='Robot',style='TButton', command = lambda: [base_protocol(inlet, 'robot', n_rep, clicked_id, ENG)])
    button3 = ttk.Button(root, text='Video',style='TButton', command = lambda: [base_protocol(inlet, 'video', n_rep, clicked_id, ENG)])
    button4 = ttk.Button(root, text='VR',style='TButton', command = lambda: [base_protocol(inlet, 'vr', n_rep, clicked_id, ENG)])
    
    exit_button = ttk.Button(root, text='Exit', style='B3.TButton',command = root.destroy)

    # Pack the widgets vertically
    id_label.pack(pady = 10)
    drop.pack(pady = 10, padx = 40) 
    newid_button.pack(pady = 10)
    refresh_button.pack(pady = 10)

    protocol_label.pack(pady=10)
    button1.pack(pady = 7)
    button2.pack(pady = 7)
    button3.pack(pady = 7)
    button4.pack(pady = 7)
    exit_button.pack(pady = 25)

    root.mainloop()


if __name__ == '__main__':
    main()





