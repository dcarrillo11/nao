from ppadb.client import Client

# Default is "127.0.0.1" and 5037
adb = Client(host="127.0.0.1", port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

screen_state = device.shell(f'dumpsys power | grep mScreenOn ')
print(screen_state)

device.shell(f'input keyevent 26')
device.shell(f'input touchscreen swipe 930 2500 1080 380')
device.shell(f'input text "9420"')
