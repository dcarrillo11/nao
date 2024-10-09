adb tcpip 5555
adb connect 10.13.6.51:5555
adb -s 10.13.6.51:5555 reverse tcp:8668 tcp:8668