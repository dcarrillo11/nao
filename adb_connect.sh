adb tcpip 5555
adb connect 10.13.6.51:5555
adb -s 10.13.6.51:5555 reverse tcp:8668 tcp:8668

#La IP es la del Quest 3
#adb connect 192.168.0.27:5555
#adb -s 192.168.0.27:5555 reverse tcp:8668 tcp:8668

#adb -s 2G0YC1ZG3P00JB reverse tcp:8668 tcp:8668