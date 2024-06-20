import os
from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
from datetime import date, datetime
import pandas as pd
from moviepy.editor import *

def check_and_rename(file_path, add = 0):
    original_file_path = file_path
    if add != 0:
        split = file_path.split(".")
        part_1 = split[0] + "_" + str(add)
        file_path = ".".join([part_1, split[1]])
    if not os.path.isfile(file_path):
        return file_path
    else:
        return check_and_rename(original_file_path, add + 1)

def play_video(i):

    if i == n_rep:
        clip = VideoFileClip('C:/Users/pc2/Proyecto_Alphamini/Media/Comienzo.mp4', target_resolution=(720,1280))
        clip.preview(fullscreen = True)


def main() -> None:

    global n_rep
    n_rep = 3
    play_video(3)

    protocol_type = 'Control'

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
        columns = ['Time',"FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2", 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']
        data_dict = dict((k, []) for k in columns)
        df_iter = pd.DataFrame.from_dict(data_dict)
        df_name = check_and_rename('C:/Users/pc2/Proyecto_Alphamini/Datos/{p}/{i}_{p}.csv'.format(p = protocol_type,i = id))
        df_iter.to_csv(df_name, index=False)

        print(f"ID guardado: {df_name}")


    b1_style = ttk.Style()
    b1_style.configure('TButton', font =
               ('calibri', 20),
                    borderwidth = '4')
    b1_style.map('TButton', foreground = [('active', '!disabled', 'blue')],
                     background = [('active', 'black')])
    
    #Create the widgets
    id_label = tk.Label(root,
        text ="Input the ID\nin the box below:", font = ('calibri', 20))
    id_entry = tk.Entry(root, width=40, font=('calibri', 15))
    save_button = ttk.Button(root, text="Save ID",style="B2.TButton", command=save_id)

    id_label.pack(pady = 10)
    id_entry.pack(pady = 10, padx = 50)
    save_button.pack(pady = 10)

    root.mainloop()
  

    return None

if __name__ == '__main__':
    main()