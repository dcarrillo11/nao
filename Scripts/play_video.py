import cv2 as cv
import time

videopath = 'C:/Users/pc2/Proyecto_Alphamini/Videos/alphamini_right_front.mp4'
video = cv.VideoCapture(videopath)

""" def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv.resize(frame, dim, interpolation =cv.INTER_AREA)
 """
#let's reproduce the video
while (video.isOpened()):
    ret,frame = video.read() #read a single frame 
    if not ret: #this mean it could not read the frame 
         print("Could not read the frame")   
         break
    #frame = rescale_frame(frame, percent=60)
    cv.namedWindow('imagen', cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty('imagen',cv.WND_PROP_FULLSCREEN,
               cv.WINDOW_FULLSCREEN)
    cv.imshow('imagen', frame)

    if cv.waitKey(1) == 27: #Code for ESC key
        break

    time.sleep(1/30)
