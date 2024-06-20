#Librerías
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
import asyncio
import time
import logging
import mini.mini_sdk as MiniSdk
from mini.apis import *
from mini.apis.api_action import PlayAction
from mini.dns.dns_browser import WiFiDevice
from mini.apis.base_api import MiniApiResultType
from mini.apis.api_behavior import StartBehavior, ControlBehaviorResponse, StopBehavior
from mini.apis.api_expression import ControlMouthLamp, ControlMouthResponse, PlayExpression, PlayExpressionResponse, SetMouthLamp, SetMouthLampResponse, MouthLampColor, MouthLampMode
from mini.apis.test_connect import test_connect, shutdown, test_get_device_by_name, test_play_action
import pygame
import random
import tkinter as tk
from datetime import date, datetime
import mne
from mne.channels import read_layout
from mne.time_frequency import psd_array_welch, tfr_multitaper
from mne.stats import permutation_cluster_1samp_test as pcluster_test
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from scipy import signal
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch, freqz, filtfilt
import argparse
import psutil
import pyautogui
from pylsl import StreamInlet, resolve_stream
from pydub import AudioSegment
from pydub.playback import play




MiniSdk.set_robot_type(MiniSdk.RobotType.EDU) #tipo de robot
#Encontrar robot (device) en la red WiFi:
device: WiFiDevice = asyncio.get_event_loop().run_until_complete(test_get_device_by_name())
if device: #Si lo encuentra, se conecta
    asyncio.get_event_loop().run_until_complete(test_connect(device))


""" #Movimientos
asyncio.get_event_loop().run_until_complete(test_play_action('face_028b')) #derecho

asyncio.get_event_loop().run_until_complete(test_play_action('Surveillance_004')) #izquierdo

asyncio.get_event_loop().run_until_complete(test_play_action('random_short5')) #ambos

 """
######################
#Parámetros protocolo
######################
relax_time = 30 #segundos de relajación inicial
imagine_time = 4 #segundos de imaginación motora
robot_time = 5 #segundos de ejecución del robot 
n_rep = 3 #Número de repeticiones de imaginar-ejecución
left_electrodes = ['FC1', 'C3', 'C1', 'CP1']
right_electrodes = ['FC2', 'C4', 'C2', 'CP2']
sfreq = 250
#["Fz", "FC1", "FC2", "C3", "Cz", "C4", "CP1", "CP2"]
electrodos_incluidos = ["FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2"]

##########################
#Lista brazo que se mueve
##########################
# Creamos una lista vacía
brazos = []

# Agregamos 15 "izquierdo" y 15 "derecho" aleatoriamente
for i in range(n_rep):
    if i < (n_rep/3):
        brazos.append("izquierdo")
    elif i >=(n_rep/3) and i<((2*n_rep)/3):
        brazos.append("derecho")
    else:
        brazos.append("ambos")

# Mezclamos aleatoriamente la lista
random.shuffle(brazos)

# Mostramos la lista
#print(brazos)

########
#Fecha
########
fecha = []
today = date.today()
fecha.append(today.day)
fecha.append(today.month)
fecha.append(today.year)
fecha.append(datetime.now().hour)
fecha.append(datetime.now().minute)
fecha_str = ''.join(map(str, fecha)) #fecha actual en string (e.g. 10122022)

print(fecha_str)

##########
#Colores
##########

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURQUESA = (159, 215, 191)
VERDE = (153, 204, 0)



###############
#ID del sujeto
###############

root = tk.Tk()
root.geometry("600x300")

# Variable global para guardar el ID
id = ""

def guardar_id():
    global id
    id = entry.get()
    root.destroy()
    # Aquí podrías guardar el ID en una variable o archivo para su posterior uso
    print(f"ID guardado: {id}")


label = tk.Label(root, text="Introducir ID:", font=("Arial", 40))
label.pack(pady=10)

entry = tk.Entry(root, width=40, font=("Arial", 30))
entry.pack(pady=10)

boton = tk.Button(root, text="Guardar ID", font=("Arial", 20), command=guardar_id)
boton.pack()

root.mainloop()



#Inicializar la streaming layer
streams = resolve_stream()
inlet = StreamInlet(streams[0])
fs = 250

#Inicializar las columnas de los datos y el diccionario para capturar los datos
columns = ['Time',"FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2", 'AccX', 'AccY', 'AccZ',
            'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']

#Funcion para grabar datos del unicorn
def record_data(duracion):
    data_dict = dict((k, []) for k in columns)
    finished = False
    while not finished:

        data, timestamp = inlet.pull_sample()
        timestamp = datetime.fromtimestamp(psutil.boot_time() + timestamp)
        #El timestamp que obtiene son los segundos desde que se encenció el ordenador,
        #por eso sumamos al timestamp la fecha en la que se inició el ordenador (psutil.boot_time())
        all_data = [timestamp] + data

        i = 0
        for key in list(data_dict.keys()):
            data_dict[key].append(all_data[i])
            i = i + 1
        
        if len(data_dict['Time']) >= fs*duracion:
            finished = True
    return data_dict


#Funcion reproducir audio   
def reproducir_audio(ruta_archivo):
    audio = AudioSegment.from_file(ruta_archivo)
    play(audio)


""""
inicio1 = time.time()
#relax
relax_time = 10
reproducir_audio('C:/Users/pc2/GNEC/audios/hola_relaja.mp3')
#start_countdown_relax()
fin1 = time.time()


print('Inicio relax'+datetime.now().strftime('%Y%m%d%H%M%S%f'))
data_dict = record_data(relax_time)
df_relax = pd.DataFrame.from_dict(data_dict)
df_relax['STI'] = 1
df_relax.to_csv('df_relax.csv', index = False)
print('Fin relax'+datetime.now().strftime('%Y%m%d%H%M%S%f'))


#Primer imagina
#Primer imagina mover...
time.sleep(5)
reproducir_audio('C:/Users/pc2/GNEC/audios/ahora_imagina.mp3')
time.sleep(5)


lista_df = [df_relax]
"""
lista_df=[]

for i in range(n_rep):
    print('------------------------------')
    print()
    print(f"REPETICIÓN NÚMERO: {i+1}" )
    print()
    print('------------------------------')

    print('------------------------------')
    print()
    print("IMAGINA " + brazos[i].upper())
    print()
    print('------------------------------')
    df_name = f"df_{i}"

    if brazos[i]=='derecho':
        inicio = time.time()
        data_dict = record_data(5)
        asyncio.get_event_loop().run_until_complete(test_play_action('face_028b'))
        #asyncio.get_event_loop().run_until_complete(test_play_action('face_028b'))
        fin = time.time()
        print("TIEMPO:")
        print(fin-inicio)
        
        
        globals()[df_name] = pd.DataFrame.from_dict(data_dict)
        lista_df.append(globals()[df_name])
        globals()[df_name]['STI'] = 2 #imaginando derecho


    elif brazos[i]=='izquierdo':
        inicio = time.time()
        data_dict = record_data(5)
        asyncio.get_event_loop().run_until_complete(test_play_action('Surveillance_004'))
        #asyncio.get_event_loop().run_until_complete(test_play_action('Surveillance_004'))
        fin = time.time()
        print("TIEMPO:")
        print(fin-inicio)

        globals()[df_name] = pd.DataFrame.from_dict(data_dict)
        lista_df.append(globals()[df_name])
        globals()[df_name]['STI'] = 3 #imaginando izquierdo

    elif brazos[i]=='ambos':
        inicio = time.time()
        data_dict = record_data(5)
        asyncio.get_event_loop().run_until_complete(test_play_action('random_short5'))
        #asyncio.get_event_loop().run_until_complete(test_play_action('random_short5'))
        fin = time.time()
        print("TIEMPO:")
        print(fin-inicio)

        globals()[df_name] = pd.DataFrame.from_dict(data_dict)
        lista_df.append(globals()[df_name])
        globals()[df_name]['STI'] = 4 #imaginando ambos

    #relax    
    data_dict = record_data(10)
    time.sleep(10)
    df_relax_i = f"df_relax_{i}"   
    globals()[df_relax_i] = pd.DataFrame.from_dict(data_dict)
    lista_df.append(globals()[df_relax_i])
    globals()[df_relax_i]['STI'] = 1

#fin1 = time.time()
#print("TIEMPO audio:")
#print(fin1-inicio1)

df_completo = pd.concat(lista_df, ignore_index=True)
df_completo.columns = ['Time', 'FC1', 'FC2', 'C3', 'C1', 'C2', 'C4', 'CP1', 'CP2', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation', 'STI']

#df_completo = df_completo.rename(columns={0: 'Fz', 1: 'FC1', 2: 'FC2', 3:'C3', 4:'Cz', 5:'C4', 6:'CP1', 7:'CP2'})
nombre_df = id+'_'+fecha_str+'.csv'
df_completo.to_csv(nombre_df, index=False)
