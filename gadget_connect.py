
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
from android_vr import android_connect, start_vr, stop_vr, kill_server

def main():

    #####################
    #Protocol parameters#
    #####################

    ENG = True #Modo ingles

    left_electrodes = ['FC1', 'C3', 'C1', 'CP1']
    right_electrodes = ['FC2', 'C4', 'C2', 'CP2']
    included_electrodes = ['FC1', 'FC2', 'C3', 'C1', 'C2', 'C4', 'CP1', 'CP2']
    fs = 250
    n_rep = 15 #Number of Imagery-Execution

    global newid_flag
    newid_flag = False

    #Participants

    with open('participants.json', 'r') as file:
        participants = json.load(file)

    ##########################
    #Graphical User Interface#
    ##########################

    root = tk.Tk()
    root.geometry('300x600+600+100')
    root.title('Protocol GUI')
    
    def contact_nao():

        nao_command = "py -2 nao_controls.py --mode 0"  # launch your python2 script
        process = subprocess.Popen(nao_command.split(), stdout=subprocess.PIPE, text = True)
        output, error = process.communicate() # receive output from the python2 script
        connection_flag = output.strip().split('\n')[-1]
        if connection_flag == 'False':
            messagebox.showerror(title='Conection error', message = 'NAO está desconectado')
            return
        elif connection_flag == 'True':
            nao_command = "py -2 nao_controls.py --mode 2 --move ready"  # launch your python2 script
            process = subprocess.Popen(nao_command.split(), stdout=subprocess.PIPE, text = True)
            return

    def quest_connect(id, ENG):

        folder = 'alphamini'
        folder_eng = 'alphamini_eng'

        shutil.copy('./participants.json', '../verge3d/%s/participants.json' %folder)
        shutil.copy('./participants.json', '../verge3d/%s/participants.json' %folder_eng)

        f_id = open('../verge3d/%s/user.txt' %folder, 'w')
        f_id.write(id.get())
        f_id.close()

        f_id = open('../verge3d/%s/user.txt' %folder_eng, 'w')
        f_id.write(id.get())
        f_id.close()

        vr_flag, vr_device = android_connect()

        if vr_flag == False:
            messagebox.showerror(title='Conection error', message = 'Quest está desconectado')

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
   
    protocol_label = tk.Label(root, text='Select the gadget\n to connect:', font=('calibri', 20))

    button1 = ttk.Button(root, text='Robot',style='TButton', command = contact_nao)
    button2 = ttk.Button(root, text='VR',style='TButton', command = lambda: [quest_connect(clicked_id, ENG)])
    button3 = ttk.Button(root, text='Close',style='TButton', command = kill_server)

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

    exit_button.pack(pady = 25)

    root.mainloop()


if __name__ == '__main__':
    main()
