############
#Librerías 
############
import numpy as np 
import pandas as pd
import os
import pygame
import random
import tkinter as tk
import time
import datetime
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt 
from pylsl import StreamInlet, resolve_stream
from scipy import signal, stats
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch, freqz, filtfilt
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
#from sklearn.pipeline import Pipeline
import mne
from mne.channels import read_layout
from mne.time_frequency import psd_array_welch
from mne.time_frequency import tfr_multitaper
from mne.stats import permutation_cluster_1samp_test as pcluster_test
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import argparse
#import win32gui
import pyautogui
import psutil


######################
#Parámetros protocolo
######################
relax_time = 30 #segundos de relajación inicial
imagine_time = 4 #segundos de imaginación motora
robot_time = 5 #segundos de ejecución del robot 
n_rep = 10 #Número de repeticiones de imaginar-ejecución
left_electrodes = ['C3', 'PO7']
right_electrodes = ['C4', 'PO8']
sfreq = 250
#["Fz", "FC1", "FC2", "C3", "Cz", "C4", "CP1", "CP2"]
electrodos_incluidos = ["FZ", "C3", "CZ", "C4", "PZ", "PO7", "OZ", "PO8"]


##########################
#Lista brazo que se mueve
##########################
# Creamos una lista vacía
brazos = []

# Agregamos la mitad de repeticiones "izquierdo" y la mitad "derecho" aleatoriamente
for i in range(n_rep):
    if i < (n_rep/2):
        brazos.append("izquierdo")
    else:
        brazos.append("derecho")

# Mezclamos aleatoriamente la lista
random.shuffle(brazos)

# Mostramos la lista
print(brazos)

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



###############
#ID del sujeto
###############

root = tk.Tk()
root.geometry("800x400")

# Variable global para guardar el ID
id = ""

def guardar_id():
    global id
    id = entry.get()
    root.destroy()
    print(f"ID guardado: {id}")


label = tk.Label(root, text="Introducir ID:", font=("Arial", 50))
label.pack(pady=10)

entry = tk.Entry(root, width=50, font=("Arial", 40))
entry.pack(pady=10)


boton = tk.Button(root, text="Guardar ID", font=("Arial", 25), command=guardar_id)
boton.pack()

root.mainloop()

""" 
hwnd = win32gui.FindWindow(None, 'uCode - v3.9.1.1')

win32gui.SetForegroundWindow(hwnd) """


#Inicializar la streaming layer

pyautogui.click(x=698, y=279) #Hacer click en uCode
streams = resolve_stream()
inlet = StreamInlet(streams[0])
fs = 250

#Inicializar las columnas de los datos y el diccionario para capturar los datos
columns = ['Time', 'FZ', 'C3', 'CZ', 'C4', 'Pz', 'PO7', 'OZ', 'PO8', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']

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


data_dict = record_data(34)
df_relax = pd.DataFrame.from_dict(data_dict)
df_relax['STI'] = 1
df_relax.to_csv('df_relax.csv', index = False)

#PSD RELAX
ch_types=["eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "stim"]

ch_names = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8', 'STI']

montage = mne.channels.make_standard_montage("standard_1020")
info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
samples = (df_relax.iloc[:,1:10]).T*1e-6
raw_relax = mne.io.RawArray(samples, info)
raw_relax.set_montage(montage = montage)
#raw_relax.set_eeg_reference(ref_channels='average')
raw_relax.filter(7, None, picks = electrodos_incluidos)
#raw_relax.set_eeg_reference(ref_channels='average')
raw_relax.filter(None, 12, picks = electrodos_incluidos)
raw_relax_left = raw_relax.copy().pick_channels(left_electrodes)
raw_relax_right = raw_relax.copy().pick_channels(right_electrodes)

raw_relax_c3 = raw_relax.copy().pick_channels(['C3'])
raw_relax_c4 = raw_relax.copy().pick_channels(['C4'])

window = 'hamming'
n_fft = int(2*sfreq)  # Tamaño de la ventana para el cálculo de la FFT
n_overlap = int(sfreq)  # Número de muestras para el solapamiento entre segmentos


f, psd = signal.welch(raw_relax._data, window=window, fs = sfreq, nperseg = n_fft, noverlap=n_overlap)
f_r_right, psd_relax_right = signal.welch(raw_relax_right._data, window=window, fs = sfreq, nperseg = n_fft, noverlap=n_overlap)
f_r_left, psd_relax_left = signal.welch(raw_relax_left._data, window=window, fs = sfreq, nperseg = n_fft, noverlap=n_overlap)
f_r_c3, psd_relax_c3 = signal.welch(raw_relax_c3._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)
f_r_c4, psd_relax_c4 = signal.welch(raw_relax_c4._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)

# Calcular la media de la PSD
psd_relax_mean = np.mean(psd)
# Calcular la desviación estándar de la PSD
psd_relax_std = np.std(psd)

# Calcular la media de la PSD relax derecho
psd_relax_mean_right = np.mean(psd_relax_right)
# Calcular la desviación estándar de la PSD relax derecho
psd_relax_std_right = np.std(psd_relax_right)

# Calcular la media de la PSD relax izquierdo
psd_relax_mean_left = np.mean(psd_relax_left)
# Calcular la desviación estándar de la PSD relax izquierdo
psd_relax_std_left = np.std(psd_relax_left)

# Calcular la media de la PSD
psd_c3_r_mean = np.mean(psd_relax_c3)
psd_c4_r_mean = np.mean(psd_relax_c4)

# Calcular la desviación estándar de la PSD
psd_c3_r_std = np.std(psd_relax_c3)
psd_c4_r_std = np.std(psd_relax_c4)





#Primer imagina mover...
print('------------------------------')
print()
print(f"REPETICIÓN NÚMERO: 1")
print()
print('------------------------------')


print("IMAGINA " + brazos[0].upper())
print()
print()


if brazos[0]=='derecho':
    pyautogui.click(x=885, y=416)
elif brazos[0]=='izquierdo':
    pyautogui.click(x=513, y=414)

data_dict = record_data(5)
df_0 = pd.DataFrame.from_dict(data_dict)
df_0['STI'] = 6

lista_df = [df_relax, df_0]

for i in range(1, n_rep+1):

    if (i !=1):
        side_i = brazos[(i-2)]
    side = brazos[(i-1)]
    
    data_dict = record_data(4)

    df_name = f"df_{i}"

        
    globals()[df_name] = pd.DataFrame.from_dict(data_dict)
    lista_df.append(globals()[df_name])

    ch_types=["eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "eeg", "stim"]

    ch_names = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8', 'STI']

    
    if i == 1:
        if (brazos[0] == 'derecho'):
            globals()[df_name]['STI'] = 2 #imaginando derecho
        elif (brazos[0] == 'izquierdo'):
            globals()[df_name]['STI'] = 3 #imaginando izquierdo
    else:
        if (side_i == 'derecho'):
            globals()[df_name]['STI'] = 2 #imaginando derecho
        elif (side_i == 'izquierdo'):
            globals()[df_name]['STI'] = 3 #imaginando izquierdo
    

    montage = mne.channels.make_standard_montage("standard_1020")
    
    
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    muestras_final = int(0.5*sfreq) #solo tomamos para la psd 3.5 segundos
    samples = ((globals()[df_name]).iloc[:-muestras_final,1:10]).T*1e-6
    raw_name = f"raw_im_{i}"
    globals()[raw_name] = mne.io.RawArray(samples, info)
    globals()[raw_name].set_montage(montage = montage)
    #globals()[raw_name].set_eeg_reference(ref_channels='average')
    globals()[raw_name].filter(7, None, picks = electrodos_incluidos)
    #globals()[raw_name].set_eeg_reference(ref_channels='average')
    globals()[raw_name].filter(None, 12, picks = electrodos_incluidos)

    # Crear dos nuevos objetos Raw: electrodos izquierdos y derechos 
    raw_left = globals()[raw_name].copy().pick_channels(left_electrodes)
    raw_right = globals()[raw_name].copy().pick_channels(right_electrodes)
    raw_c3 = globals()[raw_name].copy().pick_channels(['C3'])
    raw_c4 = globals()[raw_name].copy().pick_channels(['C4'])
    
    n_fft = int(0.5*sfreq)  # Tamaño de la ventana para el cálculo de la FFT
    n_overlap = int(0.25*sfreq)  # Número de muestras para el solapamiento entre segmentos
    

    ##########
    #Izquierda
    ##########

    #psd_left = raw_left.compute_psd(method='welch', fmin=fmin, fmax=fmax, n_fft=n_fft, n_overlap=n_overlap)
    f_left, psd_left = signal.welch(raw_left._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)
    f_c3, psd_c3 = signal.welch(raw_c3._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)
    
    """
    plt.figure()
    plt.plot(f_left, psd_left.T)
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('PSD (μV^2/Hz)')
    plt.xlim(0.5, 45)
    #psd_left.plot()
    plt.savefig(f'{i}'+"left"+fecha_str+'.png')
    plt.close()
    """

    # Calcular la media de la PSD
    psd_left_mean = np.mean(psd_left)
    psd_c3_mean = np.mean(psd_c3)
    # Calcular la desviación estándar de la PSD
    psd_left_std = np.std(psd_left)
    psd_c3_std = np.std(psd_c3)
    
    #Derecha
    #psd_right= raw_right.compute_psd(method='welch', fmin=fmin, fmax=fmax, n_fft=n_fft, n_overlap=n_overlap)
    f_right, psd_right = signal.welch(raw_right._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)
    f_c4, psd_c4 = signal.welch(raw_c4._data, window=window, fs = sfreq, nperseg = n_fft, noverlap = n_overlap)
    

    # Calcular la media de la PSD
    psd_right_mean = np.mean(psd_right)
    psd_c4_mean = np.mean(psd_c4)
    
    # Calcular la desviación estándar de la PSD
    psd_right_std = np.std(psd_right)
    psd_c4_std = np.std(psd_c4)
    
    print('---------------------------------------------------------------------------------------------')
    print('---------------------------------------------------------------------------------------------')
    print(f"La psd media derecha es: {psd_right_mean} +- {psd_right_std}")
    print(f"La psd media izquierda es: {psd_left_mean} +- {psd_left_std}")

    print(f"La psd media en C3 es: {psd_c3_mean} +- {psd_c3_std}")
    print(f"La psd media en C4 es: {psd_c4_mean} +- {psd_c4_std}")
 
    print()

    # Calcular desviación media de las PSD izquierda y derecha respecto a la PSD de relax
    dev_left = psd_left_mean - psd_relax_mean
    dev_right = psd_right_mean - psd_relax_mean

    # Calcular número de desviaciones estándar de las PSD izquierda y derecha respecto a la PSD de relax
    num_std_left = dev_left / psd_relax_std
    num_std_right = dev_right / psd_relax_std

    #Por electrodos
    dev_c3 = psd_c3_mean - psd_c3_r_mean
    dev_c4 = psd_c4_mean - psd_c4_r_mean
    

    num_std_c3 = dev_c3 / psd_c3_r_std
    num_std_c4 = dev_c4 / psd_c4_r_std


    print(f"La PSD izquierda se desvía {num_std_left} desviaciones estándar respecto a la PSD de relax")
    print(f"La PSD derecha se desvía {num_std_right} desviaciones estándar respecto a la PSD de relax")
    print(f"La PSD en C3 se desvía {num_std_c3} desviaciones estándar respecto a la PSD de relax")
    print(f"La PSD en C4 se desvía {num_std_c4} desviaciones estándar respecto a la PSD de relax")
    
    print('---------------------------------------------------------------------------------------------')
    print(f"La psd media en relax es: {psd_relax_mean} +- {psd_relax_std}")
    print(f"La psd media en relax (izquierda) es: {psd_relax_mean_left} +- {psd_relax_std_left}")
    print(f"La psd media en relax (derecha) es: {psd_relax_mean_right} +- {psd_relax_std_right}")
    print('---------------------------------------------------------------------------------------------')
    print()

   
    print()
    print('---------------------------------------------------------------------------------------------')
    print('---------------------------------------------------------------------------------------------')
    
    #csvname = df_name+'_'+fecha_str+'.csv'
    #globals()[df_name].to_csv(csvname, sep=',', index=False)

    print()
    print()
    print()
    

    #RELAX + CUENTA ATRÁS IMAGINA MOVER...
    data_dict = dict((k, []) for k in columns)
    finished = False
    pyautogui.click(x=720, y=664)
    
    if num_std_right < num_std_left:
        print('EL ROBOT MUEVE EL BRAZO IZQUIERDO')
        robot = 4
        pyautogui.click(x=464, y=542) #brazo izq

    else:
        print('EL ROBOT MUEVE EL BRAZO DERECHO')
        robot = 5
        pyautogui.click(x=850, y=546) #brazo derecho

    
    data_dict = record_data(10)
    df_relax_i = f"df_relax_{i}"   
    globals()[df_relax_i] = pd.DataFrame.from_dict(data_dict)
    lista_df.append(globals()[df_relax_i])
    globals()[df_relax_i]['STI'] = 1

    # Mover el brazo izquierdo o derecho según la diferencia (z) calculada
    #uCode
    
    if (i == (n_rep)): #Si es la ultima rep, no se dice imagina mover...
        pyautogui.click(x=682, y=813)
    else:
        if side=='derecho':
            pyautogui.click(x=850, y=416)
        elif side=='izquierdo':
            pyautogui.click(x=513, y=414)
        data_dict = record_data(5)

        df_name_im = f"df_im_{i}"

        globals()[df_name_im] = pd.DataFrame.from_dict(data_dict)
        lista_df.append(globals()[df_name_im])

    #muestras_final = int(6.5*sfreq)
    #globals()[df_name_im] = (globals()[df_name]).iloc[:-muestras_final]
    
    """
    globals()[df_name_im].loc[:2560,'STI'] = 1
    
    if (robot==4):
        globals()[df_name_im].loc[2561:,'STI'] = 4
    elif (robot==5):
        globals()[df_name_im].loc[2561:,'STI'] = 5
    """

    if (i == (n_rep)):
       print()
    else:
        print('------------------------------')
        print()
        print(f"REPETICIÓN NÚMERO: {i+1}")
        print()
        print('------------------------------')
        print('')
        print("IMAGINA " + side.upper())
        print()
        print()
        



df_completo = pd.concat(lista_df, ignore_index=True)
df_completo.columns = ['Time', 'FZ', 'C3', 'CZ', 'C4', 'Pz', 'PO7', 'OZ', 'PO8', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation', 'STI']

#df_completo = df_completo.rename(columns={0: 'Fz', 1: 'FC1', 2: 'FC2', 3:'C3', 4:'Cz', 5:'C4', 6:'CP1', 7:'CP2'})
nombre_df = id+'_'+fecha_str+'.csv'
df_completo.to_csv(nombre_df, index=False)




"""

#Filtro paso banda
cutoffs = [4, 40]
order = 2

b, a = signal.butter(order, [cutoffs[0]/(fs/2), cutoffs[1]/(fs/2)], "bandpass")

columnas = ['Fz', 'C3', 'CZ', 'C4', 'Pz', 'PO7', 'OZ', 'PO8']
for column in columnas:
    data_df.loc[:, column] = signal.filtfilt(b, a, data_df.loc[:, column])


data_df.to_csv('EEGdata_filt.csv', index = False)
"""