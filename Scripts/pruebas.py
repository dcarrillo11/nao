from ppadb.client import Client
import time
from tkinter import messagebox


def android_connect():

    adb = Client(host="127.0.0.1", port=5037)
    devices = adb.devices() 

    if len(devices) == 0:
        messagebox.showerror(title="Conection error", message = "Móvil desconectado o innaccesible")
        return False, []
    else:
        device = devices[0]
        return True, device
    
def start_vr(device):

    screen_state = device.shell(f'dumpsys display | grep -oE "mScreenState=..."')
    screen_lock = device.shell(f'dumpsys window | grep -oE "mDreamingLockscreen=....."')
    print(screen_state, screen_lock)

    if "OFF" in screen_state:
        device.shell(f'input keyevent 26')
        device.shell(f'input swipe 930 2500 1080 380')
        device.shell(f'input text "9420"')
    elif "true" in screen_lock:
        device.shell(f'input swipe 930 2500 1080 380')
        device.shell(f'input text "9420"')
    else:
        device.shell(f'input keyevent 3')

    device.shell(f'pm clear com.xojot.vrplayer')
    device.shell(f'media volume --set 0')
    device.shell(f'am start -n com.xojot.vrplayer/.MainActivity')
    time.sleep(2)
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 530 2880')
    device.shell(f'input tap 400 950')
    time.sleep(1)
    device.shell(f'input tap 1350 1550')
    device.shell(f'input tap 600 1500')
    device.shell(f'input tap 210 2680')
    device.shell(f'input tap 1350 100')
    device.shell(f'input tap 1300 720')
    time.sleep(2.5)
    device.shell(f'media volume --set 7')
    device.shell(f'input tap 1500 720')

def stop_vr(device):
    device.shell(f'pm clear com.xojot.vrplayer')

def main():
    flag, device_adb = android_connect()
    start_vr(device_adb)

if __name__ == '__main__':
    main()
