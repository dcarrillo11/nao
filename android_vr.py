
import time
from subprocess import Popen,PIPE
import subprocess
from ppadb.client import Client
from tkinter import messagebox

def start_server():

    Popen(['adb.exe', 'start-server'], stderr=PIPE, stdout=PIPE)
    time.sleep(2)
    #Popen(['scrcpy'], stderr=PIPE, stdout=PIPE)
    print("daemon server online")

def kill_server():
    
    Popen(['adb.exe', 'kill-server'], stderr=PIPE, stdout=PIPE)
    print("daemon server offline")


def adb_wifi():

    subprocess.run(['adb_connects.sh'],shell=True, check=True)
    messagebox.showinfo(title="adb wifi", message = "Ya puedes desconectar el cable")

def android_connect():

    start_server()

    adb = Client(host="127.0.0.1", port=5037)
    devices = adb.devices()

    if len(devices) == 0:
        messagebox.showerror(title="Conection error", message = "Dispositivo desconectado o innaccesible")
        return False, []
    else:
        adb_wifi()
        device = devices[0]
        return True, device

def unlock(device):

    screen_state = device.shell(f'dumpsys display | grep mScreenState=')
    screen_lock = device.shell(f'dumpsys window | grep -oE "mDreamingLockscreen=....."')

    if "OFF" in screen_state:
        device.shell(f'input keyevent 26')
        device.shell(f'input swipe 930 2500 1080 380')
        device.shell(f'input text "9420"')
    elif "true" in screen_lock:
        device.shell(f'input swipe 930 2500 1080 380')
        device.shell(f'input text "9420"')
    else:
        device.shell(f'input keyevent 3')

 

def start_vr(device):

    #device.push("./media/merged.mp4", "/sdcard/Alphamini/merged.mp4")

    device.shell(f'pm clear com.xojot.vrplayer')
    device.shell(f'media volume --set 0')
    device.shell(f'am start -n com.xojot.vrplayer/.MainActivity')
    time.sleep(1.5)
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 400 950')
    time.sleep(1)
    device.shell(f'input tap 1350 1550')
    device.shell(f'input tap 600 1500')
    device.shell(f'input tap 210 2680')
    device.shell(f'input tap 1350 100')
    time.sleep(1)
    device.shell(f'input tap 1250 720')
    device.shell(f'media volume --set 7')
    device.shell(f'input tap 550 350')
    device.shell(f'input tap 1500 720')

def stop_vr(device):
    device.shell(f'pm clear com.xojot.vrplayer')
    kill_server()

def main():
    device_adb = android_connect()
    print(device_adb)
    adb_wifi()
    #start_vr(device_adb)

if __name__ == '__main__':
    main()
