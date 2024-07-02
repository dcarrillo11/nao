from ppadb.client import Client
import time
from tkinter import messagebox


def android_connect():

    adb = Client(host="127.0.0.1", port=5037)
    devices = adb.devices()

    if len(devices) == 0:
        messagebox.showerror(title="Conection error", message = "Móvil desconectado o innaccesible")
    else:
        device_adb = devices[0]
        return device_adb

def start_vr(device):
    # Default is "127.0.0.1" and 5037
    adb = Client(host="127.0.0.1", port=5037)
    devices = adb.devices()

    if len(devices) == 0:
        return False

    device = devices[0]

    device.push(f'./Media/merged.mp4 sdcard/Alphamini/')

    screen_state = device.shell(f'dumpsys display | grep mScreenState=')

    if "OFF" in screen_state:
        device.shell(f'input keyevent 26')
        device.shell(f'input swipe 930 2500 1080 380')
        device.shell(f'input text "9420"')

    device.shell(f'am start -n com.xojot.vrplayer/.MainActivity')
    time.sleep(3)
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 400 950')
    device.shell(f'input tap 1350 1550')
    device.shell(f'input tap 1350 100')
    device.shell(f'input tap 1300 720')

def main():
    pass

if __name__ == '__main__':
    main()
